Architecture
System flow
User (voice/text)
     |
     v
[Frontend: Next.js chat UI]  -- mic -> Whisper STT (if audio) -> text
     |  POST /message  {session_id, text}
     v
[FastAPI Gateway]
     |
     v
[Session Manager]  (Redis: history, pending_action, state)
     |
     v
[Agent Orchestrator]  (Claude, tool-use loop)
     |
     +-- Claude proposes a tool call
     |
     v
[Ambiguity Layer]  (deterministic guardrail)
     |
     +-- ambiguous -> ask clarifying question
     |                state = AWAITING_CLARIFICATION
     |
     +-- resolved -> continue
              |
              v
     [Confirmation Gate]  (is this tool SENSITIVE?)
              |
              +-- yes -> show human-readable preview
              |          state = AWAITING_CONFIRMATION
              |
              +-- no (read-only) -> execute immediately
                       |
                       v
              [Tool Executor] -> Google Calendar / Gmail / Notion
                       |
                       v
              [Result] -> back into the agent loop if more steps remain
                       |
                       v
              [Response] -> text (+ optional speech)
Design decisions
Claude proposes, Python disposes

The ambiguity and confirmation logic is not left to the LLM alone. Telling a model "ask if you're unsure" produces inconsistent behaviour that can't be tested reliably. Instead:

Claude proposes tool calls and may call ask_clarification itself
Deterministic resolver functions independently re-check any field that came from fuzzy matching (dates, people, event titles)
If a resolver finds multiple candidates, clarification is forced, regardless of how confident Claude was
Tools are classified by risk
Class	Examples	Behaviour
SAFE (read-only)	check_availability, list_events	Execute immediately
SENSITIVE (writes)	schedule_event, send_email	Require explicit user confirmation first

A SENSITIVE tool never executes on the same turn it's proposed.

Scope

v1 includes: Google Calendar, Gmail, Notion; text and voice input; disambiguation; confirmation gates; multi-step tool chaining.

v1 excludes: multiple calendar/email providers, custom STT models, proactive behaviour without a user command.

Build order
Week	Focus
1	Agent loop + Google Calendar, text only
2	Gmail, Notion, multi-step chaining
3	Next.js frontend, voice input/output
4	Deploy, tests, demo