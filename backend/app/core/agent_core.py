"""
agent_core.py

The agent loop. Claude receives a user message plus a list of tools it
can call. Instead of just replying with text, it can respond with a
request to run a tool - and we then run it and feed the result back.

This first version does one thing: prove Claude will call a tool when
the question needs one.
"""

import anthropic
from app.config import settings
from datetime import datetime
from zoneinfo import ZoneInfo

MODEL = "claude-sonnet-4-6"
client = anthropic.Anthropic(
    api_key=settings.anthropic_api_key,
    base_url="https://api.anthropic.com",
)

# The tool definitions we hand to Claude. This is just a description -
# Claude never runs anything itself, it only asks us to.
TOOLS = [
    {
        "name": "check_availability",
        "description": (
            "Check whether the user is free during a given time window "
            "on their calendar."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "start_iso": {
                    "type": "string",
                    "description": "ISO 8601 start datetime, e.g. 2026-09-01T14:00:00",
                },
                "end_iso": {
                    "type": "string",
                    "description": "ISO 8601 end datetime",
                },
            },
            "required": ["start_iso", "end_iso"],
        },
    }
]
USER_TIMEZONE = "Europe/London"


def build_system_prompt() -> str:
    """
    Built fresh on each call so the date is always current. A hardcoded
    string would be stale the moment the process outlived midnight.
    """
    now = datetime.now(ZoneInfo(USER_TIMEZONE))
    return f"""You are an assistant with real access to the user's Google Calendar.

Current date and time: {now.strftime("%A, %d %B %Y, %H:%M")}
User's timezone: {USER_TIMEZONE}

Use the tools available to you rather than guessing or describing what \
you would do. Resolve relative dates like "tomorrow" or "next Tuesday" \
against the current date above. Keep replies short."""


def execute_tool(tool_name: str, tool_input: dict) -> dict:
    """
    Runs a tool and returns its result. Stubbed for now - real Google
    Calendar calls land tomorrow.
    """
    if tool_name == "check_availability":
        return {"available": False, "conflict": "Dentist appointment"}
    raise ValueError(f"Unknown tool: {tool_name}")


def run_conversation(user_message: str) -> str:
    """
    The agent loop. Sends the message, runs any tool Claude asks for,
    feeds the result back, and repeats until Claude replies with plain
    text instead of another tool call.
    """
    messages = [{"role": "user", "content": user_message}]

    for _ in range(5):  # hard cap so a broken loop can't run forever
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=build_system_prompt(),
            tools=TOOLS,
            messages=messages,
        )

        # Claude's whole reply goes into the history, tool calls included
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            # No tool wanted - this is the final answer
            return "".join(b.text for b in response.content if b.type == "text")

        # Run every tool Claude asked for and collect the results
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result),
                    }
                )

        # Tool results are sent back with role "user" - that's the API's
        # convention, even though a human didn't type them
        messages.append({"role": "user", "content": tool_results})

    return "Sorry, that took too many steps."