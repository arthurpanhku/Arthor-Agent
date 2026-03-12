# How to Contribute with AI | 使用 AI 辅助贡献指南

DocSentinel is an AI-powered project, and we encourage using AI tools to contribute! This guide helps you leverage LLMs (like ChatGPT, Claude, or GitHub Copilot) effectively while maintaining code quality and security standards.

DocSentinel 是一个 AI 驱动的项目，我们鼓励使用 AI 工具参与贡献！本指南将帮助你高效利用 LLM（如 ChatGPT、Claude 或 GitHub Copilot），同时保持代码质量与安全标准。

---

## 🤖 Recommended AI Workflow | 推荐的 AI 工作流

1.  **Understand the Architecture**: Feed `ARCHITECTURE.md` and `SPEC.md` to your AI context first. This ensures the AI understands the system design before generating code.
2.  **Generate Code**: Use AI to draft features, tests, or documentation.
    -   *Prompt Tip*: "Act as a senior Python developer. Implement a FastAPI endpoint for [Feature X] following the project structure in `app/api/`."
3.  **Refine & Review**: **Never copy-paste blindly.** Review the AI-generated code for:
    -   **Security**: Ensure no hardcoded secrets or unsafe inputs.
    -   **Style**: Run `make lint` and `make format` to match project standards.
    -   **Logic**: Verify edge cases that AI might miss.
4.  **Generate Tests**: Ask AI to write unit tests for the code it generated.
    -   *Prompt Tip*: "Write pytest unit tests for the code above, covering success and failure scenarios."

1.  **理解架构**：首先将 `ARCHITECTURE.md` 和 `SPEC.md` 提供给 AI 上下文。这能确保 AI 在生成代码前理解系统设计。
2.  **生成代码**：使用 AI 起草功能、测试或文档。
    -   *Prompt 技巧*："扮演高级 Python 开发者。遵循 `app/api/` 中的项目结构，为 [Feature X] 实现一个 FastAPI 端点。"
3.  **完善与审查**：**切勿盲目复制粘贴。** 审查 AI 生成的代码：
    -   **安全**：确保无硬编码密钥或不安全输入。
    -   **风格**：运行 `make lint` 和 `make format` 以符合项目标准。
    -   **逻辑**：验证 AI 可能遗漏的边缘情况。
4.  **生成测试**：让 AI 为其生成的代码编写单元测试。
    -   *Prompt 技巧*："为上述代码编写 pytest 单元测试，覆盖成功与失败场景。"

---

## 🛡️ AI Contribution Rules | AI 贡献规则

-   **No Hallucinations**: Verify imports and library methods exist.
-   **Security First**: If AI suggests `eval()`, `exec()`, or disabling SSL verification, **reject it**.
-   **Attribution**: If you used AI significantly, mention it in the PR description (e.g., "Co-authored with Claude 3.5 Sonnet").

-   **拒绝幻觉**：验证导入的库与方法是否真实存在。
-   **安全第一**：如果 AI 建议使用 `eval()`、`exec()` 或禁用 SSL 验证，**请拒绝**。
-   **署名**：如果你大量使用了 AI，请在 PR 描述中注明（例如："与 Claude 3.5 Sonnet 共同编写"）。

---

## 🛠️ Useful Prompts for DocSentinel | 常用提示词

### For New Features | 开发新功能
> "I want to add a new [Skill] to DocSentinel. Based on `app/agent/orchestrator.py`, how should I structure a new skill class that integrates with the existing tool calling mechanism?"

### For Documentation | 编写文档
> "Read `app/api/assessments.py` and generate a Swagger/OpenAPI description for the `POST /assessments` endpoint."

### For Bug Fixing | 修复 Bug
> "Here is a traceback from the logs: [Paste Logs]. Analyze the root cause in the context of a FastAPI async application and suggest a fix."

---

Happy Coding with AI! 🚀
