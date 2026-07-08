# Context - Portfolio Revamp

## Project Information
- **Project Root**: `C:\Users\99196\teamwork_projects\resume_e_portfolio_update\job`
- **Orchestrator Working Directory**: `C:\Users\99196\teamwork_projects\resume_e_portfolio_update\job\.agents\orchestrator`
- **Parent/Sentinel Conversation ID**: `bc0402c2-a49f-490b-9cb5-2e970e2cfba4`
- **Aesthetic Goal**: Dark Mode Cyber/Tech (glassmorphism, subtle neon, 3D interactive animations)
- **Libraries/Tech**: GSAP, Lenis.dev, Type (typography), Inspira-ui
- **Network Mode**: CODE_ONLY (no external web search except via the subagent if allowed, but wait, we have code search and local files)

## Constraints
- Delegate ALL work to subagents via `invoke_subagent`. Do not write code or solve problems directly.
- Use file-editing tools only for metadata/state files (.md) in `.agents/` folder.
- Do not reuse a subagent after it has delivered its handoff - always spawn fresh.
- Hard veto on forensic audit failure.
