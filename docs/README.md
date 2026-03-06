# Arthor Agent — 设计/规范文档目录 | Design & Specification Index

本目录存放与 PRD（产品需求文档）配套的**可执行设计与规范**，供开发、集成与运维使用。  
This directory holds **executable design and specification** artifacts that accompany the PRD for development, integration, and operations.

**PRD 位置 / PRD location**：`../SPEC.md`（仓库根目录）

---

## 文档列表与填写顺序 | Document List and Order

| 序号 | 文档 | 用途 | 建议填写时机 |
|------|------|------|--------------|
| 01 | [01-architecture-and-tech-stack.md](./01-architecture-and-tech-stack.md) | 技术选型、整体架构、组件接口与数据流 | 项目启动 / 技术设计阶段 |
| 02 | [02-api-specification.yaml](./02-api-specification.yaml) | REST API 契约（OpenAPI 3.x），可与代码同步生成 | 与 01 并行或紧随其后 |
| 03 | [03-assessment-report-and-skill-contract.md](./03-assessment-report-and-skill-contract.md) | 评估报告 JSON Schema、Skill 输入/输出契约 | 与 01 并行，Agent/Skill 开发前定稿 |
| 04 | [04-integration-guide.md](./04-integration-guide.md) | AAD、ServiceNow 等集成的配置与字段映射 | 接入企业环境前 |
| 05 | [05-deployment-runbook.md](./05-deployment-runbook.md) | 部署方式、配置项、网络与运维步骤 | 首次部署 / 交付前 |

---

## 技术栈默认假设（与 PRD 一致）| Default Tech Stack

- **语言 / Language**：Python 3.10+
- **Web/API**：FastAPI
- **Agent 编排**：LangChain / LangGraph
- **向量库**：Chroma / Qdrant / 其他（在 01 中确定）
- **文档解析**：Unstructured、PyMuPDF、python-docx、openpyxl 等（在 01 中确定）
- **LLM 抽象**：LangChain LLM 抽象或自研统一接口

具体版本与选型以 **01-architecture-and-tech-stack.md** 为准。

---

## 使用方式 | How to Use

1. **从 01 开始**：确定技术栈与架构，再填写 02（API）、03（报告/Skill）。
2. **02 与代码同步**：建议用 FastAPI 的 OpenAPI 导出或手写 YAML，与实现保持一致。
3. **03 的 Schema**：已提供独立 JSON Schema 文件 `schemas/assessment-report.json`，可供校验与代码生成使用。
4. **04、05**：在对接真实 AAD/ServiceNow 环境与部署时完善。

### 目录结构

```
docs/
├── README.md
├── 01-architecture-and-tech-stack.md
├── 02-api-specification.yaml
├── 03-assessment-report-and-skill-contract.md
├── 04-integration-guide.md
├── 05-deployment-runbook.md
└── schemas/
    └── assessment-report.json
```

---

*最后更新 / Last updated：与 PRD 版本对应。*
