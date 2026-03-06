# How to Contribute with AI | 使用 AI 辅助贡献指南

Arthor-Agent is an AI-powered project, and we encourage using AI tools to contribute! This guide helps you leverage LLMs (like ChatGPT, Claude, or GitHub Copilot) effectively while maintaining code quality and security standards.

---

## 🤖 Recommended AI Workflow

1.  **Understand the Architecture**: Feed `ARCHITECTURE.md` and `SPEC.md` to your AI context first. This ensures the AI understands the system design before generating code.
2.  **Generate Code**: Use AI to draft features, tests, or documentation.
    -   *Prompt Tip*: "Act as a senior Python developer. Implement a FastAPI endpoint for [Feature X] following the project structure in `app/api/`."
3.  **Refine & Review**: **Never copy-paste blindly.** Review the AI-generated code for:
    -   **Security**: Ensure no hardcoded secrets or unsafe inputs.
    -   **Style**: Run `make lint` and `make format` to match project standards.
    -   **Logic**: Verify edge cases that AI might miss.
4.  **Generate Tests**: Ask AI to write unit tests for the code it generated.
    -   *Prompt Tip*: "Write pytest unit tests for the code above, covering success and failure scenarios."

## 🛡️ AI Contribution Rules

-   **No Hallucinations**: Verify imports and library methods exist.
-   **Security First**: If AI suggests `eval()`, `exec()`, or disabling SSL verification, **reject it**.
-   **Attribution**: If you used AI significantly, mention it in the PR description (e.g., "Co-authored with Claude 3.5 Sonnet").

## 🛠️ Useful Prompts for Arthor-Agent

### For New Features
> "I want to add a new [Skill] to Arthor-Agent. Based on `app/agent/orchestrator.py`, how should I structure a new skill class that integrates with the existing tool calling mechanism?"

### For Documentation
> "Read `app/api/assessments.py` and generate a Swagger/OpenAPI description for the `POST /assessments` endpoint."

### For Bug Fixing
> "Here is a traceback from the logs: [Paste Logs]. Analyze the root cause in the context of a FastAPI async application and suggest a fix."

---

Happy Coding with AI! 🚀
