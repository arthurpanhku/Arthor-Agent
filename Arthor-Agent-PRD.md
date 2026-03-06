# Arthor Agent — 产品需求文档（PRD）  
# Arthor Agent — Product Requirements Document (PRD)

**文档版本 / Document Version**：v1.4  
**创建日期 / Date**：2025-03-06  
**作者 / Author**：PAN CHAO  
**联系身份 / Contact**：u3638376@connect.hku.hk  

> **系统架构文档 | System Architecture**  
> 完整的系统架构说明（含图示、数据流、部署视图）已单独成文，采用开源项目常用格式：  
> **[ARCHITECTURE.md](./ARCHITECTURE.md)**  
> 本文 PRD 第五节仅保留架构摘要与索引；详细组件设计、Mermaid 图及安全架构请见 ARCHITECTURE.md。

**v1.4**：PRD 与系统架构文档分离；架构细节迁移至 ARCHITECTURE.md，PRD 保留产品目标、需求与安全控制。  
*v1.4: PRD and System Architecture doc split; architecture details moved to ARCHITECTURE.md.*

**v1.3**：新增非业务性「安全需求与安全控制」（§7.2）。  
**v1.2**：知识库多格式上传与开源解析、Parser 复用。  
**v1.1**：企业集成（ServiceNow）、IAM（AAD/SSO、RBAC）、部署与连通性。

---

## 一、文档说明 | Section 1 — Document Purpose

### 中文

本 PRD 面向「Arthor Agent」开源项目，用于明确业务痛点、解决方案、系统架构与产品范围，为后续设计与开发提供统一依据。项目目标是通过 AI Agent 自动化完成安全评估相关文档/表格/报告的审阅与建议，减轻企业安全团队负担，并支持对接主流与本地大模型、多格式文件解析及可扩展的 Skill 与知识库。

### English

This PRD is for the open-source “Arthor Agent” project. It defines business pain points, solution approach, system architecture, and product scope to serve as a single source of truth for subsequent design and development. The project aims to use an AI Agent to automate the review of and recommendations for security-related documents, forms, and reports, reduce the burden on enterprise security teams, and support integration with mainstream and local LLMs, multi-format file parsing, and extensible Skills and knowledge bases.

---

## 二、业务背景与痛点 | Section 2 — Business Context and Pain Points

### 2.1 业务背景 | Business Context

#### 中文

大型企业的 Cyber Security 团队需要在以下多维度约束下工作：

- **依据来源多样**：公司内部 Security Policy、行业最佳实践（如 NIST SSDF、OWASP、CISA 等）、历史项目案例与合规框架（如 SOC2、ISO 27001）。
- **流程覆盖完整 SSDLC**：从需求/设计、开发、测试、部署到运维，每个阶段都有安全评审与管控要求。
- **交付物类型繁多**：安全问卷（Security Questionnaire）、设计文档、威胁建模、SAST/DAST 报告、合规证明、审计材料等，需人工阅读、比对与签字（Sign-off）。

在敏捷与 DevOps 环境下，企业每年上线项目数量从几十到几百不等，安全人员需要在有限人力下完成大量评估与审阅，成为明显瓶颈。

#### English

Enterprise Cyber Security teams operate under multiple constraints:

- **Diverse reference sources**: Internal security policies, industry best practices (e.g. NIST SSDF, OWASP, CISA), past project cases, and compliance frameworks (e.g. SOC2, ISO 27001).
- **Full SSDLC coverage**: Security review and control requirements exist at every stage—requirements/design, development, testing, deployment, and operations.
- **Wide variety of deliverables**: Security questionnaires, design documents, threat models, SAST/DAST reports, compliance evidence, and audit materials all require manual reading, comparison, and sign-off.

In agile and DevOps environments, enterprises ship dozens to hundreds of projects per year. Security teams must complete large volumes of assessments and reviews with limited headcount, creating a clear bottleneck.

---

### 2.2 核心痛点 | Core Pain Points

#### 中文

| 痛点类别 | 具体描述 |
|----------|----------|
| **评估依据分散** | 需同时参照 Policy、行业标准、项目案例；不同项目/客户可能对应不同合规要求（如 FedRAMP、PCI-DSS）与风险偏好，人工查找与对齐成本高。 |
| **问卷与证据流程繁重** | 业务团队填写大量 Security Questionnaire；安全团队评估后出具 Security Control 清单；业务团队再提供控制实施证明；安全团队二次审阅。多轮往返、模板不统一、证据质量参差。 |
| **开发阶段管控依赖人工** | 期望开发使用带 Code Review 的 IDE，在提交或 CI/CD 中自动执行 SAST/DAST 等；但策略制定、结果解读、例外审批仍依赖安全人员，难以规模化。 |
| **上线前集中审阅压力大** | 所有交付物就绪后，安全人员需 Review 全部文件并 Sign-off。技术文档（架构图、接口说明、配置清单等）对非技术背景安全人员不友好，阅读与理解成本高。 |
| **规模与一致性矛盾** | 项目数量大、标准多、企业风险偏好不一，人工评估易出现不一致、遗漏或延迟，且难以沉淀可复用的评估模式。 |

#### English

| Pain point | Description |
|------------|-------------|
| **Fragmented assessment criteria** | Teams must align with policies, industry standards, and project precedents; different projects or customers may have different compliance needs (e.g. FedRAMP, PCI-DSS) and risk appetites, leading to high manual lookup and alignment cost. |
| **Heavy questionnaire and evidence workflow** | Business teams complete large security questionnaires; security teams evaluate and issue control lists; business teams then provide evidence of controls; security performs a second review. Multiple rounds, inconsistent templates, and variable evidence quality. |
| **Development-phase control relies on people** | Organizations expect IDE-based code review and automated SAST/DAST in commit or CI/CD; policy definition, result interpretation, and exception approval still depend on security staff and are hard to scale. |
| **Pre-release review pressure** | Once all deliverables are ready, security must review every file and sign off. Technical documents (architecture diagrams, API specs, config lists) are hard for non-technical security staff to read and interpret. |
| **Scale vs. consistency** | With many projects, multiple standards, and varying risk appetites, manual assessment tends to be inconsistent, incomplete, or delayed, and reusable assessment patterns are difficult to institutionalize. |

---

### 2.3 期望改变 | Desired Change

#### 中文

- **自动化**：对需要评估的表格、文档、报告进行自动化分析与初评，减少重复性人工阅读。
- **一致性**：基于统一知识库与策略，输出一致的评估结论与整改建议。
- **可扩展**：支持不同合规框架、不同客户/项目类型的评估场景，便于后续接入更多 SSDLC 环节（如需求、设计、代码、运维）。

#### English

- **Automation**: Automate analysis and initial assessment of forms, documents, and reports to reduce repetitive manual reading.
- **Consistency**: Produce consistent assessment conclusions and remediation recommendations based on a unified knowledge base and policies.
- **Extensibility**: Support assessment scenarios for different compliance frameworks and customer/project types, enabling future integration of more SSDLC stages (e.g. requirements, design, code, operations).

---

## 三、解决方案概述 | Section 3 — Solution Overview

### 3.1 产品定位 | Product Positioning

#### 中文

构建**安全团队专用 AI Agent**，首要方向为：**自动化评估所有需要安全团队审阅的表格、文档与报告**。安全人员将项目相关文件提交给 Agent 后，Agent 能够：

1. **解析多格式文件**：将 Word、PDF、Excel、PPT、图片等转为可被模型理解的中间格式（如 JSON/Markdown）。
2. **结合知识库与策略**：基于内置/可配置的合规与策略知识库，理解「应该满足什么标准」。
3. **执行风险评估与建议**：识别与安全/合规相关的风险点，给出安全建议与可操作的整改方案。
4. **输出结构化结果**：便于安全人员快速复核、签字或转交业务/开发团队整改。

#### English

Build a **dedicated AI Agent for security teams**, with the primary focus on **automating the assessment of all forms, documents, and reports that require security team review**. After security staff submit project-related files to the Agent, the Agent will:

1. **Parse multi-format files**: Convert Word, PDF, Excel, PPT, images, etc. into an intermediate format (e.g. JSON/Markdown) that models can process.
2. **Use knowledge base and policy**: Rely on built-in or configurable compliance and policy knowledge to understand “what standards must be met.”
3. **Perform risk assessment and recommendations**: Identify security/compliance risks and provide security advice and actionable remediation.
4. **Produce structured output**: Enable security staff to quickly review, sign off, or hand off to business/development for remediation.

---

### 3.2 方案价值 | Solution Value

#### 中文

- **降本**：减少安全人员在重复性文档审阅上的时间，使其更聚焦高价值决策与例外处理。
- **提速**：缩短问卷—评估—证据—审阅的周期，支持敏捷节奏下的安全门禁。
- **可复现**：评估逻辑与依据可沉淀在知识库与 Skill 中，便于审计与持续优化。
- **开放**：支持对接多种商用与本地 LLM，满足数据不出域、成本控制等企业需求。

#### English

- **Cost reduction**: Reduce time security staff spend on repetitive document review so they can focus on high-value decisions and exceptions.
- **Speed**: Shorten the questionnaire → assessment → evidence → review cycle and support security gates in agile cadences.
- **Reproducibility**: Assessment logic and criteria can be captured in the knowledge base and Skills for audit and continuous improvement.
- **Openness**: Support multiple commercial and local LLMs to meet requirements for data residency and cost control.

---

## 四、产品目标与成功指标 | Section 4 — Product Goals and Success Metrics

### 4.1 产品目标 | Product Goals

#### 中文

| 目标 | 说明 |
|------|------|
| **自动化评估** | 支持对 Security Questionnaire、设计文档、合规证明、审计报告等的主流格式进行自动解析与风险评估。 |
| **可配置评估场景** | 通过知识库与 Skill 支持按合规框架、客户类型、项目类型配置不同评估标准与检查项。 |
| **多模型支持** | 支持主流商用 LLM（如 ChatGPT、千问、Claude 等）与本地/私有化部署模型（如 Ollama），统一接口便于切换。 |
| **结果可操作** | 输出风险项、合规差距、具体整改建议及（可选）优先级，便于安全与业务团队执行。 |

#### English

| Goal | Description |
|------|-------------|
| **Automated assessment** | Support automatic parsing and risk assessment of common formats for security questionnaires, design documents, compliance evidence, and audit reports. |
| **Configurable assessment scenarios** | Use the knowledge base and Skills to configure different assessment criteria and check items by compliance framework, customer type, or project type. |
| **Multi-model support** | Support mainstream commercial LLMs (e.g. ChatGPT, Qwen, Claude) and local/on-prem models (e.g. Ollama) through a unified interface for easy switching. |
| **Actionable results** | Output risk items, compliance gaps, concrete remediation suggestions, and (optionally) priority to support execution by security and business teams. |

---

### 4.2 成功指标（建议）| Success Metrics (Suggested)

#### 中文

- **覆盖度**：支持评估的文档类型数量（如 5+ 种常见格式）、知识库内合规/策略条目数量。
- **效率**：单次评估任务从上传到生成报告的平均时长；与纯人工审阅相比的时间节省比例（需在试点中度量）。
- **可用性**：安全人员完成一次「上传 → 查看报告 → 做出决策」的闭环所需步骤与时间。
- **可扩展性**：新增一种文件类型或新增一个评估场景（新合规框架）的配置/开发成本。

#### English

- **Coverage**: Number of document types supported for assessment (e.g. 5+ common formats) and number of compliance/policy entries in the knowledge base.
- **Efficiency**: Average time from upload to report generation per assessment; time saved vs. fully manual review (to be measured in pilots).
- **Usability**: Number of steps and time for security staff to complete one “upload → view report → make decision” loop.
- **Extensibility**: Configuration/development cost to add a new file type or a new assessment scenario (e.g. new compliance framework).

---

## 五、系统架构 | Section 5 — System Architecture

> **完整架构文档（含图示与部署视图）**  
> **Full system architecture** (with diagrams, data flow, deployment, and security architecture) is maintained in:  
> **[ARCHITECTURE.md](./ARCHITECTURE.md)**

### 5.1 架构摘要 | Architecture Summary

#### 中文

系统采用分层设计：**接入层**（REST API / Web / CLI）→ **核心**（任务编排、记忆体、Skill 层、知识库 RAG、文件解析）→ **LLM 抽象层** → **商用/本地 LLM**。可选对接 **AAD**（身份/SSO）与 **ServiceNow**（项目元数据）。详细组件说明、Mermaid 架构图、数据流与时序图、集成视图、安全架构及部署视图见 **[ARCHITECTURE.md](./ARCHITECTURE.md)**。

#### English

The system uses a layered design: **Access** (REST API / Web / CLI) → **Core** (Orchestrator, Memory, Skills, Knowledge Base RAG, Parser) → **LLM abstraction** → **Cloud/local LLMs**. Optional integrations: **AAD** (identity/SSO) and **ServiceNow** (project metadata). For component details, Mermaid diagrams, data flow, integration view, security architecture, and deployment view, see **[ARCHITECTURE.md](./ARCHITECTURE.md)**.

#### 架构图 | Architecture Diagram

```
                    ┌─────────────────────────────────────────────────────────┐
                    │           用户 / 安全人员 | User / Security Staff         │
                    └───────────────────────────┬─────────────────────────────┘
                                                │
                    ┌───────────────────────────▼─────────────────────────────┐
                    │                接入层 | Access Layer (API / Web / CLI)   │
                    └───────────────────────────┬─────────────────────────────┘
                                                │
    ┌───────────────────────────────────────────▼───────────────────────────────────────────┐
    │                         Arthor Agent 核心 | Core                                        │
    │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │
    │  │  任务编排    │  │  记忆体     │  │  Skill 层   │  │  知识库     │  │  文件解析   │  │
    │  │  (Orchestr.) │  │  (Memory)   │  │  (Skills)   │  │  (RAG/KB)   │  │  (Parser)   │  │
    │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬───────┘  │
    │         │                │                │                │                │          │
    │         └────────────────┴────────────────┴────────────────┴────────────────┘          │
    │                                          │                                               │
    │                              ┌───────────▼───────────┐                                  │
    │                              │  LLM 抽象层 | LLM Abstraction                            │
    │                              └───────────┬───────────┘                                  │
    └──────────────────────────────────────────┼──────────────────────────────────────────────┘
                                               │
        ┌─────────────────────────────────────┼─────────────────────────────────────┐
        │  商用/云端 LLM | Commercial/Cloud     │    本地/私有化 LLM | Local/On-prem   │
        │  ChatGPT / Claude / Qwen / Gemini    │    Ollama / vLLM / ...               │
        └─────────────────────────────────────────────────────────────────────────────┘
```

**中文**：接入层与核心之外，系统可对接 **AAD**（身份/登录与 API Token 校验）与 **项目管理平台**（如 ServiceNow，读取项目元数据；可选回写评估结果）。  
**English**: Beyond the access and core layers, the system can integrate with **AAD** (identity/login and API token validation) and **project management platforms** (e.g. ServiceNow for project metadata; optional write-back of assessment results).

### 5.2 核心组件索引 | Component Index

| 组件 | 职责概要 | 详见 |
|------|----------|------|
| **Orchestrator** | 接收任务，协调 Parser / KB / Skill / LLM，输出报告 | ARCHITECTURE.md § Component Design |
| **Memory** | 工作记忆、情景记忆（可选）、语义记忆（可选） | ARCHITECTURE.md § Component Design |
| **Skills** | 问卷比对、策略符合性、证据检查、风险分级等 | ARCHITECTURE.md § Component Design |
| **Knowledge Base** | 多格式上传→解析→切块→向量化→RAG 检索 | ARCHITECTURE.md § Component Design |
| **Parser** | 多格式→统一 Markdown/JSON，服务评估与 KB 入库 | ARCHITECTURE.md § Component Design |
| **LLM abstraction** | 统一接口，支持 OpenAI / Ollama / Claude / 千问等 | ARCHITECTURE.md § Component Design |
| **Integrations** | AAD（SSO/Token）、ServiceNow（项目元数据/回写） | ARCHITECTURE.md § Integration Points |

<details>
<summary>原 5.2.1–5.2.8 详细说明（已迁移至 ARCHITECTURE.md，此处保留折叠供参考）</summary>

#### 5.2.1 Agent 智能体（任务编排）| Agent (Orchestration)

**中文**

- **职责**：接收评估任务（如「评估某项目的安全问卷 + 设计文档」），拆解子步骤，调用记忆、Skill、知识库与文件解析结果，驱动多轮与 LLM 的交互，并汇总输出。
- **能力**：任务规划、工具调用（Skill）、上下文组装、结果聚合与格式化（如评估报告 JSON/Markdown）。
- **参考**：可借鉴 LangGraph/VoltAgent 等项目的编排模式，保持与具体 LLM 解耦。

**English**

- **Role**: Accept assessment tasks (e.g. “assess security questionnaire + design doc for project X”), break them into steps, invoke memory, Skills, knowledge base, and parser output, drive multi-turn LLM interaction, and aggregate results.
- **Capabilities**: Task planning, tool invocation (Skills), context assembly, result aggregation and formatting (e.g. assessment report as JSON/Markdown).
- **Reference**: Orchestration patterns from projects such as LangGraph/VoltAgent; keep orchestration decoupled from any specific LLM.

---

#### 5.2.2 记忆体（Memory）| Memory

**中文**

- **职责**：为 Agent 提供跨轮次、跨会话的上下文，避免重复询问、支持多轮追问与历史评估复用。
- **建议分层**（可与开源 Agent 记忆架构对齐）：
  - **工作记忆**：当前任务相关的会话与当前轮次的上下文窗口。
  - **情景记忆**：历史会话摘要、关键实体与结论，用于「与上次评估对比」等场景。
  - **语义记忆**：与知识库结合，存储从历史评估中提炼的规则或模式（可选，后期扩展）。
- **实现**：可选用 Redis/内存 + 向量库（用于语义检索），并设定 TTL 与压缩策略以控制成本。

**English**

- **Role**: Provide the Agent with context across turns and sessions to avoid redundant questions and support multi-turn follow-up and reuse of past assessments.
- **Suggested layers** (aligned with common Agent memory designs):
  - **Working memory**: Session and current-turn context for the active task.
  - **Episodic memory**: Summaries of past sessions, key entities and conclusions (e.g. for “compare with last assessment”).
  - **Semantic memory**: Combined with the knowledge base, store rules or patterns derived from past assessments (optional, later phase).
- **Implementation**: Redis/in-memory plus a vector store for semantic retrieval; TTL and compression to control cost.

---

#### 5.2.3 Skill（技能层）| Skills

**中文**

- **职责**：封装可复用的安全评估能力，供 Agent 按需调用。
- **示例 Skill**：
  - 问卷一致性检查：对比问卷答案与知识库中的控制要求，标记差距。
  - 策略符合性检查：将文档内容与指定 Policy/标准条款做比对。
  - 证据充分性检查：判断提供的证据类型与描述是否满足控制要求。
  - 风险等级判定：根据规则或模型输出对发现项进行分级。
- **设计**：Skill 输入/输出接口标准化（如 JSON Schema），便于新增与组合；部分 Skill 可主要依赖规则+检索，部分依赖 LLM 生成。

**English**

- **Role**: Encapsulate reusable security assessment capabilities for the Agent to invoke as needed.
- **Example Skills**:
  - Questionnaire consistency: Compare questionnaire answers to control requirements in the knowledge base and flag gaps.
  - Policy compliance: Compare document content to specified policy/standard clauses.
  - Evidence sufficiency: Judge whether provided evidence type and description meet control requirements.
  - Risk rating: Grade findings by rules or model output.
- **Design**: Standardize Skill input/output (e.g. JSON Schema) for easy addition and composition; some Skills can be rule- and retrieval-based, others LLM-generated.

---

#### 5.2.4 知识库（Knowledge Base）| Knowledge Base

**中文**

- **职责**：存放合规与策略等「指导性」内容，用于构建不同场景的评估标准，并为 RAG 提供检索源。
- **多格式上传与转换**：知识库需**支持上传多种格式的文档**（如 Word、PDF、Excel、PPT、图片、HTML 等）。上传后，通过**文档解析与转换能力**（与 5.2.5 文件解析复用或共用技术栈）识别文档内容，并**转换为 LLM 可读的格式**（如纯文本、Markdown 或统一 JSON 结构），再进入切块、向量化与入库流程。可优先采用或集成**开源文档解析项目**（如基于 PyMuPDF、python-docx、Unstructured、Apache Tika、Docling 等）实现各格式的识别与转换，在保证可维护性的前提下减少自研成本。
- **内容类型**：
  - 公司 Security Policy、基线控制列表。
  - 行业/合规框架（如 NIST SSDF、OWASP ASVS、CISA attestation 要点、客户专用条款）。
  - 历史项目案例、常见问题与最佳实践（脱敏后）。
- **技术**：上传 → 多格式解析与转 LLM 可读格式 → 文档切块 → 向量化 → 写入向量库；查询时通过 RAG 检索相关片段注入 Agent 上下文；可支持多库（如按合规框架分库）与元数据过滤。

**English**

- **Role**: Store “guidance” content such as compliance and policy to define assessment criteria for different scenarios and to serve as the retrieval source for RAG.
- **Multi-format upload and conversion**: The knowledge base **must support uploading documents in multiple formats** (e.g. Word, PDF, Excel, PPT, images, HTML). After upload, a **document parsing and conversion layer** (shared with or aligned to the Parser in 5.2.5) extracts content and **converts it into LLM-readable form** (e.g. plain text, Markdown, or a unified JSON schema) before chunking, embedding, and indexing. The implementation may use or integrate **open-source document parsing projects** (e.g. PyMuPDF, python-docx, Unstructured, Apache Tika, Docling) for format detection and conversion to reduce custom development while keeping the pipeline maintainable.
- **Content types**:
  - Company security policies and baseline control lists.
  - Industry/compliance frameworks (e.g. NIST SSDF, OWASP ASVS, CISA attestation points, customer-specific terms).
  - Historical project cases, FAQs, and best practices (sanitized).
- **Technical**: Upload → multi-format parse and convert to LLM-readable format → chunk → embed → store in vector DB; at query time retrieve relevant chunks via RAG and inject into Agent context; support multiple collections (e.g. by framework) and metadata filters.

---

#### 5.2.5 文件解析与标准化（Parser）| File Parsing and Normalization (Parser)

**中文**

- **职责**：将用户上传的各类文件（**评估任务中的文件**与**知识库中的文档**）转换为 Agent/LLM 可稳定阅读的中间表示（如 JSON 或 Markdown），保留结构（标题、表格、列表）与关键文本。同一解析与转换能力可复用于「评估输入文件」与「知识库文档入库」两条链路。
- **实现方式**：优先采用或集成**开源文档解析/识别项目**实现各格式的内容识别与转换，例如：PyMuPDF / pdfplumber（PDF）、python-docx（Word）、openpyxl / xlrd（Excel）、python-pptx（PPT）、Unstructured、Apache Tika、Docling 等；图片可结合 Tesseract、PaddleOCR 或视觉模型。通过统一输出 schema 便于下游（Skill、LLM、知识库切块）消费。
- **支持格式**（目标）：
  - **Word**（.docx）：正文、标题、表格提取。
  - **PDF**：文本 + 可选表格结构识别（若需可后续接入 OCR）。
  - **Excel**：工作表、行列、单元格文本导出为结构化 JSON/表格 Markdown。
  - **PPT**：幻灯片文本与备注。
  - **图片**：通过 OCR 或视觉模型生成描述/文本，再进入下游分析。
- **输出**：统一 schema（如 `{ format: "markdown"|"json", content: ..., metadata: { filename, type, pages? } }`），便于后续 Skill、LLM 与知识库入库流程消费。

**English**

- **Role**: Convert uploaded files (both **assessment inputs** and **knowledge base documents**) into a stable intermediate representation (e.g. JSON or Markdown) that the Agent/LLM can read, preserving structure (headings, tables, lists) and key text. The same parsing and conversion pipeline can be reused for assessment file processing and for knowledge base ingestion.
- **Implementation**: Prefer using or integrating **open-source document parsing/recognition projects** for content extraction and conversion, e.g. PyMuPDF / pdfplumber (PDF), python-docx (Word), openpyxl / xlrd (Excel), python-pptx (PPT), Unstructured, Apache Tika, Docling; for images, Tesseract, PaddleOCR, or vision models. A unified output schema allows downstream consumers (Skills, LLM, KB chunking) to use the result consistently.
- **Target formats**:
  - **Word** (.docx): Extract body text, headings, tables.
  - **PDF**: Text plus optional table structure; OCR can be added later if needed.
  - **Excel**: Export sheets, rows, columns, cell text as structured JSON or table Markdown.
  - **PPT**: Slide text and notes.
  - **Images**: Use OCR or vision models to produce description/text for downstream analysis.
- **Output**: Unified schema (e.g. `{ format: "markdown"|"json", content: ..., metadata: { filename, type, pages? } }`) for consumption by Skills, the LLM, and the knowledge base ingestion pipeline.

---

#### 5.2.6 LLM 抽象层 | LLM Abstraction Layer

**中文**

- **职责**：统一多引擎调用接口，支持切换模型而不改 Agent 逻辑。
- **对接范围**：
  - **商用/云端**：OpenAI（ChatGPT）、Anthropic（Claude）、阿里千问、Google（Gemini）等，通过各自 API 或统一网关。
  - **本地/私有化**：Ollama、vLLM、LocalAI 等，满足数据不出域与成本控制。
- **接口**：统一抽象为「补全/聊天」与「可选的 function calling」，便于 Agent 调用工具（Skill）与流式输出。

**English**

- **Role**: Provide a unified interface to multiple LLM backends so the model can be switched without changing Agent logic.
- **Scope**:
  - **Commercial/cloud**: OpenAI (ChatGPT), Anthropic (Claude), Alibaba Qwen, Google (Gemini), etc., via their APIs or a unified gateway.
  - **Local/on-prem**: Ollama, vLLM, LocalAI, etc., for data residency and cost control.
- **Interface**: Abstract to “completion/chat” and optional function calling so the Agent can invoke tools (Skills) and support streaming.

---

#### 5.2.7 企业集成（项目管理平台）| Enterprise Integrations (Project Management)

**中文**

- **职责**：从企业项目管理平台读取**项目元数据**，为评估任务提供项目上下文（项目类型、所属部门、合规范围、客户/合同等），支撑「按项目选场景、按项目过滤知识库」等能力，并可与现有流程打通（如评估结果回写工单）。
- **目标平台**：优先支持 **Service Now** 等成熟 ITSM/项目治理平台；架构上预留适配器接口，便于后续扩展 Jira、Azure DevOps、自建项目库等。
- **项目元数据用途**：
  - 评估场景选择：根据项目类型、客户、合规要求自动或推荐适用的评估场景与知识库。
  - 权限与可见性：结合 IAM 与项目归属，控制谁可发起/查看该项目的评估（见 5.2.8）。
  - 可追溯与审计：评估任务与项目 ID、变更请求（Change Request）等关联，便于审计与报告。
- **集成方式**：通过平台提供的 REST API / 官方集成方式读取项目、工单、配置项等元数据；可选支持 Webhook/事件订阅，在「项目状态变更」或「交付物就绪」时触发或提醒评估。

**English**

- **Role**: Read **project metadata** from the enterprise project management platform to provide project context (project type, department, compliance scope, customer/contract, etc.) for assessment tasks, support “select scenario by project” and “filter knowledge base by project,” and integrate with existing workflows (e.g. write assessment results back to tickets).
- **Target platforms**: Prioritise support for **ServiceNow** and similar mature ITSM/project governance platforms; the architecture shall expose an adapter interface for future extensions (e.g. Jira, Azure DevOps, custom project repositories).
- **Use of project metadata**:
  - **Assessment scenario selection**: Derive or recommend applicable assessment scenarios and knowledge bases from project type, customer, and compliance requirements.
  - **Authorization and visibility**: Together with IAM and project ownership, control who can start or view assessments for a given project (see 5.2.8).
  - **Traceability and audit**: Link assessment tasks to project IDs, change requests, etc., for audit and reporting.
- **Integration**: Read project, ticket, and configuration-item metadata via the platform’s REST API or official integration; optionally support webhooks/events so that “project status change” or “deliverables ready” can trigger or remind assessments.

---

#### 5.2.8 身份与访问管理（IAM）| Identity and Access Management (IAM)

**中文**

- **职责**：统一用户身份与访问控制，保证仅授权用户可登录、发起评估、查看结果与管理配置；支持与公司** Azure Active Directory（AAD）** 等企业身份体系对接，实现单点登录（SSO）与统一账号生命周期管理。
- **登录与 SSO**：
  - 支持使用 **AAD（微软 Azure AD / Entra ID）** 作为身份提供方（IdP），用户使用公司账号登录 Web/CLI，无需在本系统单独维护密码。
  - 支持标准协议（如 OAuth 2.0 / OpenID Connect），便于扩展其他 IdP（如 Okta、Google Workspace）。
- **角色与权限（RBAC）**：建议角色包括但不限于——
  - **安全分析员**：发起评估、查看自己参与或有权项目的评估结果、上传/管理知识库（在权限范围内）。
  - **安全负责人**：上述权限 + 评估场景与策略配置、审批/ Sign-off、查看审计日志。
  - **项目/业务负责人**：查看所属项目的评估结果与整改建议，不可修改策略与知识库。
  - **API/集成消费者**：通过 API Key 或服务账号调用 API，用于与 ServiceNow、CI/CD 等集成；权限范围可限定到特定项目或操作（如仅提交评估、仅拉取结果）。
  - **系统管理员**：用户与角色管理、集成配置（AAD、ServiceNow、LLM）、系统参数与审计。
- **API 认证**：除浏览器 SSO 外，API 调用支持 Bearer Token（如 AAD 颁发的 JWT）、API Key 或客户端凭证（用于 M2M），并校验 token 有效期与权限范围。
- **数据隔离**：按角色与项目归属限制可访问的评估任务与报告，避免跨部门/跨项目越权查看；与项目管理平台中的项目—人员关系对接时，可据此做细粒度授权。

**English**

- **Role**: Unify user identity and access control so that only authorised users can log in, start assessments, view results, and manage configuration; integrate with the organisation’s **Azure Active Directory (AAD)** (or equivalent) for single sign-on (SSO) and centralised account lifecycle.
- **Login and SSO**:
  - Support **AAD (Microsoft Azure AD / Entra ID)** as the identity provider (IdP); users sign in to Web/CLI with corporate accounts without maintaining separate passwords in this system.
  - Use standard protocols (e.g. OAuth 2.0 / OpenID Connect) to allow future IdPs (e.g. Okta, Google Workspace).
- **Roles and permissions (RBAC)** (suggested):
  - **Security analyst**: Start assessments, view results for projects they are assigned or authorised for, upload/manage knowledge base within scope.
  - **Security lead**: Above plus assessment scenario and policy configuration, approval/sign-off, and audit log access.
  - **Project / business owner**: View assessment results and remediation for their projects only; cannot change policy or knowledge base.
  - **API / integration consumer**: Call API via API key or service account for integrations (e.g. ServiceNow, CI/CD); scope to specific projects or actions (e.g. submit assessment only, fetch results only).
  - **System administrator**: User and role management, integration config (AAD, ServiceNow, LLM), system parameters, and audit.
- **API authentication**: In addition to browser SSO, API calls support Bearer Token (e.g. JWT from AAD), API Key, or client credentials (M2M), with validation of token validity and scope.
- **Data isolation**: Restrict access to assessment tasks and reports by role and project ownership to prevent cross-department/cross-project access; when integrated with project–person mapping from the project management platform, use it for fine-grained authorisation.

</details>

---

### 5.3 数据流（简要）| Data Flow (Summary)

#### 中文

1. 用户通过 **AAD** 登录（或 API 凭据）后，通过 API/Web/CLI 提交**评估任务**（含一个或多个文件，可选关联**项目 ID** 或指定评估场景/合规框架）。
2. **项目元数据**（可选）：若关联项目 ID，从 **ServiceNow** 等项目管理平台拉取项目元数据，用于选择评估场景、过滤知识库及权限校验。
3. **文件解析**：各文件经 Parser 转为统一中间格式，与元数据一起传入 Agent。
4. **任务编排**：Agent 加载场景对应的**知识库**检索结果与**Skill**，结合**记忆**（如有历史会话），组装 prompt 并调用 **LLM**。
5. **多轮推理**：Agent 可能多轮调用 LLM 与 Skill（如先做问卷解析，再做策略比对，再生成建议），期间写入/读取**记忆**。
6. **输出**：生成结构化评估结果（风险项、合规差距、整改建议、可选优先级），返回给用户或写入存储供审阅与 Sign-off；可选将结果或链接回写到项目管理平台工单。

#### English

1. After the user signs in via **AAD** (or API credentials), they submit an **assessment task** (one or more files; optional **project ID** or scenario/compliance framework) via API/Web/CLI.
2. **Project metadata** (optional): If a project ID is provided, fetch project metadata from **ServiceNow** or another project management platform to select assessment scenario, filter knowledge base, and enforce access.
3. **File parsing**: Each file is converted by the Parser to the common intermediate format and passed to the Agent with metadata.
4. **Orchestration**: The Agent loads **knowledge base** retrieval results and **Skills** for the scenario, plus **memory** (if there is prior session context), assembles the prompt, and calls the **LLM**.
5. **Multi-turn reasoning**: The Agent may make multiple LLM and Skill calls (e.g. questionnaire parsing, then policy comparison, then recommendations), reading and writing **memory** as needed.
6. **Output**: Produce structured assessment results (risk items, compliance gaps, remediation suggestions, optional priority) and return to the user or persist for review and sign-off; optionally write results or links back to the project management platform (e.g. ticket).

---

## 六、功能范围与用户故事 | Section 6 — Scope and User Stories

### 6.1 核心功能列表 | Core Feature List

| 功能模块 / Module | 功能点 / Feature | 优先级 / Priority |
|-------------------|------------------|-------------------|
| 文件解析 / Parser | 支持 Word / PDF / Excel / PPT 上传并转为 JSON 或 Markdown | P0 |
| 文件解析 / Parser | 支持图片 OCR 或视觉模型生成文本描述 | P1 |
| 知识库 / KB | 支持上传多格式文档（Word/PDF/Excel/PPT/图片等），经解析转换为 LLM 可读格式后切块、向量化与检索；可集成开源解析项目（如 Unstructured、Tika、Docling 等） | P0 |
| 知识库 / KB | 上传/管理合规与策略文档，建立向量索引，支持按场景/标签检索 | P0 |
| 知识库 / KB | 多知识库与元数据过滤（如按框架、客户） | P1 |
| Agent 评估 / Assessment | 选择评估场景（如「客户 A 安全问卷」），上传文件，一键触发评估 | P0 |
| Agent 评估 / Assessment | 输出结构化报告：风险项、合规差距、整改建议（Markdown/JSON） | P0 |
| LLM 对接 / LLM | 配置并切换多种商用 LLM（OpenAI/Claude/千问等） | P0 |
| LLM 对接 / LLM | 配置并对接本地模型（如 Ollama） | P0 |
| Skill | 至少 1 个可用的评估 Skill（如问卷与策略比对） | P0 |
| Skill | Skill 可配置、可扩展（接口规范 + 示例） | P1 |
| 记忆 / Memory | 单会话内多轮对话与上下文保持 | P0 |
| 记忆 / Memory | 跨会话摘要或关键结论复用（可选） | P1 |
| 接入方式 / Access | REST API；可选 Web UI 与 CLI | P0 / P1 |
| **企业集成 / Integrations** | 对接项目管理平台（如 ServiceNow）读取项目元数据（项目类型、归属、合规范围等） | P0 |
| **企业集成 / Integrations** | 可选：评估结果回写工单 / Webhook 触发评估 | P1 |
| **身份与访问 / IAM** | 支持 AAD（Azure AD/Entra ID）登录与 SSO | P0 |
| **身份与访问 / IAM** | 角色与权限（RBAC）：安全分析员、负责人、项目负责人、API 消费者、系统管理员 | P0 |
| **身份与访问 / IAM** | API 认证：Bearer Token（AAD JWT）/ API Key / 客户端凭证 | P0 |
| **身份与访问 / IAM** | 按项目/角色做评估结果数据隔离与可见性控制 | P0 |

---

### 6.2 用户故事（示例）| User Stories (Examples)

#### 中文

- **作为** 安全团队成员，**我希望** 上传一份 Security Questionnaire（Excel/Word）和一份架构说明（PDF），**以便** Agent 自动识别与政策/标准的差距并给出整改建议，减少我逐条比对的时间。
- **作为** 安全团队负责人，**我希望** 在知识库中维护「客户 A 专用条款」与「公司基线控制」，**以便** 评估时优先依据这些标准，保证对外评估一致性。
- **作为** 企业 IT，**我希望** 将 Agent 配置为仅使用本地 Ollama 模型，**以便** 评估内容不离开内网，满足合规要求。
- **作为** 开发者，**我希望** 通过 REST API 提交文档并获取 JSON 格式的评估结果，**以便** 将 Agent 集成进现有工单或审批流程。
- **作为** 安全分析员，**我希望** 使用公司 AAD 账号登录系统，**以便** 无需记忆额外密码且符合企业统一身份策略。
- **作为** 安全负责人，**我希望** 在发起评估时选择或关联 ServiceNow 中的项目，**以便** 系统自动带出项目类型与合规范围并推荐评估场景，评估结果可与项目/工单关联便于追溯。

#### English

- **As a** developer, **I want to** submit documents via REST API and receive assessment results in JSON **so that** the Agent can be integrated into existing ticketing or approval workflows.
- **As a** security analyst, **I want to** sign in with my corporate AAD account **so that** I do not need a separate password and we comply with centralised identity policy.
- **As a** security lead, **I want to** select or link a project from ServiceNow when starting an assessment **so that** the system auto-fills project type and compliance scope and recommends assessment scenarios, and results are linked to the project/ticket for traceability.
- **As a** security team lead, **I want to** maintain “Customer A specific terms” and “company baseline controls” in the knowledge base **so that** assessments consistently prioritize these criteria for external consistency.
- **As** enterprise IT, **I want to** configure the Agent to use only a local Ollama model **so that** assessment content never leaves the internal network and compliance is met.
- **As a** security team member, **I want to** upload a Security Questionnaire (Excel/Word) and an architecture document (PDF) **so that** the Agent can automatically identify gaps vs. policy/standards and suggest remediation, reducing my manual line-by-line comparison.
- **As a** developer, **I want to** submit documents via REST API and receive assessment results in JSON **so that** the Agent can be integrated into existing ticketing or approval workflows.

---

## 七、非功能需求 | Section 7 — Non-Functional Requirements

| 类别 / Category | 中文要求 | English Requirement |
|-----------------|----------|----------------------|
| **安全与隐私** / Security & privacy | 支持纯本地/私有化部署与本地 LLM，敏感文档可不经过公网；支持审计日志（谁在何时评估了哪些文件）。 | Support fully local/on-prem deployment and local LLM so sensitive documents need not traverse the public internet; support audit logs (who assessed which files when). |
| **性能** / Performance | 单次评估（如 10 页 PDF + 1 份问卷）在合理模型与硬件下，目标端到端时延可接受（具体目标可在试点中定）。 | For a single assessment (e.g. 10-page PDF + one questionnaire), target end-to-end latency acceptable under reasonable model and hardware (concrete targets to be set in pilots). |
| **可维护性** / Maintainability | 知识库、Skill、LLM 配置均可通过配置或管理界面维护，无需改代码即可扩展新场景。 | Knowledge base, Skills, and LLM configuration maintainable via config or admin UI so new scenarios can be added without code changes. |
| **可观测性** / Observability | 记录每次调用的模型、token 用量、耗时与错误，便于成本与稳定性管理。 | Log model used, token usage, duration, and errors per call for cost and stability management. |
| **授权与数据隔离** / Authorization & data isolation | 按角色与项目归属限制可访问的评估任务与报告；与 AAD 组/项目平台人员数据结合做细粒度授权；敏感评估结果仅授权角色可查看。 | Restrict access to assessment tasks and reports by role and project ownership; combine with AAD groups and project-platform membership for fine-grained auth; only authorised roles can view sensitive assessment results. |
| **部署与连通性** / Deployment & connectivity | 支持内网/私有化部署；需可连通 AAD（登录/Token 校验）、项目管理平台（如 ServiceNow）API、所选 LLM 端点；文档说明网络与防火墙要求。 | Support on-prem/private deployment; must be able to reach AAD (login/token validation), project management platform APIs (e.g. ServiceNow), and chosen LLM endpoints; document network and firewall requirements. |
| **开源与兼容** / Open source & compatibility | 架构设计参考主流开源 Agent 项目（见下文），便于社区贡献与与现有工具链集成。 | Architecture aligns with mainstream open-source Agent projects (see below) to facilitate community contribution and integration with existing toolchains. |

---

### 7.2 安全需求与安全控制（非业务）| Security Requirements and Controls (Non-Functional)

本节规定**本系统自身**的安全需求与安全控制设计，属于非业务性要求，用于保障产品在开发、部署与运行中的机密性、完整性与可用性，并支持合规与审计。与「业务功能」中的「安全评估」区分：此处针对的是**项目/产品的安全建设**，而非 Agent 所评估的外部文档与策略。

**English**: This section defines **security requirements and controls for the system itself** as non-functional requirements. It aims to protect confidentiality, integrity, and availability during development, deployment, and operation, and to support compliance and audit. It is distinct from the “security assessment” business feature: here we address **the security of the project/product**, not the documents and policies assessed by the Agent.

#### 7.2.1 控制域总览 | Control Domains Overview

| 控制域 / Domain | 中文说明 | English |
|-----------------|----------|---------|
| **身份与访问控制** | 认证、授权、会话与 API 安全 | Identity and access control |
| **数据安全** | 传输与存储加密、敏感数据与密钥管理 | Data security |
| **应用安全** | 输入校验、注入防护、依赖与构建安全 | Application security |
| **运维与审计** | 日志、监控、事件响应与备份恢复 | Operations and audit |
| **供应链与开源** | 依赖管理、漏洞扫描与许可合规 | Supply chain and open source |

---

#### 7.2.2 身份与访问控制 | Identity and Access Control

| 控制项 ID | 需求描述（中文）| Requirement (English) | 设计/实现要点 |
|-----------|------------------|------------------------|----------------|
| IAM-01 | 所有面向用户或集成方的接口必须经过认证（除显式放行的健康检查等）| All user- or integration-facing endpoints must require authentication except explicitly exempt (e.g. health check). | API 层统一认证中间件；未认证请求返回 401。 |
| IAM-02 | 采用强认证方式：支持 AAD/OIDC SSO；API 支持 Bearer JWT 或 API Key，禁止在 URL 中传递敏感凭据。 | Use strong authentication: AAD/OIDC SSO; API supports Bearer JWT or API Key; no sensitive credentials in URL. | 见 PRD 5.2.8；Token 仅放在 Header 或 Body。 |
| IAM-03 | 实施基于角色的访问控制（RBAC），权限与角色定义清晰，默认最小权限。 | Implement RBAC with clear role and permission definitions; principle of least privilege by default. | 见 PRD 5.2.8 角色列表；新用户/服务默认仅最小必要权限。 |
| IAM-04 | 会话与 Token 具备超时与失效机制；支持撤销（如登出、API Key 吊销）。 | Sessions and tokens have timeout and expiry; support revocation (logout, API key revocation). | JWT expiry、refresh 策略；API Key 可禁用。 |
| IAM-05 | 敏感操作（如删除知识库、修改全局配置）需二次确认或更高权限角色。 | Sensitive operations (e.g. delete KB, change global config) require confirmation or higher-privilege role. | 定义敏感操作清单；必要时审批或审计日志强制。 |

---

#### 7.2.3 数据安全 | Data Security

| 控制项 ID | 需求描述（中文）| Requirement (English) | 设计/实现要点 |
|-----------|------------------|------------------------|----------------|
| DATA-01 | 传输层加密：与客户端、AAD、ServiceNow、LLM 等外部服务通信使用 TLS（推荐 1.2+）。 | Use TLS (1.2+) for all communication with clients and external services (AAD, ServiceNow, LLM). | 生产环境禁用纯 HTTP；配置 HSTS、证书有效性校验。 |
| DATA-02 | 存储敏感数据时采用加密：密钥、凭据、会话密钥等不得明文落盘；敏感配置与密钥通过安全机制注入（如环境变量、密钥管理服务）。 | Encrypt sensitive data at rest; secrets and credentials must not be stored in plaintext; inject via secure means (env, secrets manager). | 密钥/DB 密码等使用密钥管理或受控环境变量；不在代码与仓库中硬编码。 |
| DATA-03 | 敏感数据最小化：仅收集与保留业务与审计所必需的数据；评估文档与报告按策略保留与过期删除。 | Minimise sensitive data: collect and retain only what is necessary; assessment documents and reports retained and purged per policy. | 明确保留期与删除策略；日志中不记录文档正文或完整 Token。 |
| DATA-04 | 个人数据与可识别信息（PII）的处理符合隐私要求：访问可控、可审计；支持数据主体权利（如查询、删除）若适用。 | PII handling complies with privacy requirements: access controlled and auditable; support data subject rights (access, deletion) where applicable. | 审计日志中用户标识可脱敏或受控；提供数据导出/删除能力若涉及 PII。 |
| DATA-05 | 与第三方 LLM 交互时：若使用云端 LLM，明确数据是否出境、是否被用于训练；支持仅使用本地/私有化 LLM 以满足数据不出域要求。 | When using third-party LLMs: clarify data residency and training use for cloud LLMs; support local/private LLM only for data-sovereignty. | 配置与文档中说明各 LLM 提供商策略；本地 Ollama 等不向公网发送数据。 |

---

#### 7.2.4 应用安全 | Application Security

| 控制项 ID | 需求描述（中文）| Requirement (English) | 设计/实现要点 |
|-----------|------------------|------------------------|----------------|
| APP-01 | 对所有输入进行校验与规范化：文件类型、大小、数量、请求体结构；防止路径遍历、恶意文件名。 | Validate and sanitise all inputs: file type, size, count, body schema; prevent path traversal and malicious filenames. | 白名单文件类型与扩展名；限制单文件/总大小与数量；文件名脱敏或重写。 |
| APP-02 | 防范注入类风险：API 参数、上传内容解析结果注入 LLM prompt 或下游系统时需转义/隔离；避免拼接生成动态查询或命令。 | Prevent injection: escape or isolate API params and parsed content when injected into LLM prompts or downstream; no raw concatenation for dynamic queries or commands. | Prompt 模板化与参数占位；向量检索使用参数化/安全 API；不执行用户可控命令。 |
| APP-03 | 依赖与第三方库：维护依赖清单，定期更新以修复已知漏洞；构建与 CI 中集成依赖/软件成分扫描（如 SCA）。 | Dependencies: maintain manifest, update regularly for known vulnerabilities; integrate dependency/SCA scanning in build and CI. | requirements.txt/pyproject.toml 锁定版本；CI 中运行 pip-audit / Dependabot / Snyk 等。 |
| APP-04 | 错误与异常处理不向外部泄露内部路径、堆栈或配置细节；统一返回格式与错误码。 | Error handling must not expose internal paths, stack traces, or config to external callers; use consistent response format and error codes. | 生产环境关闭详细异常输出；日志中记录完整信息供内部排查。 |
| APP-05 | 防护常见 Web 风险：CSRF（若存在状态化 Web）、安全头（CSP、X-Frame-Options 等）、速率限制与防滥用。 | Mitigate common web risks: CSRF (if stateful web), security headers (CSP, X-Frame-Options), rate limiting and anti-abuse. | FastAPI 中间件设置安全头；对登录与 API 做限流；大文件上传限并发与频率。 |

---

#### 7.2.5 运维与审计 | Operations and Audit

| 控制项 ID | 需求描述（中文）| Requirement (English) | 设计/实现要点 |
|-----------|------------------|------------------------|----------------|
| OPS-01 | 审计日志：记录谁在何时对哪些资源执行了何种操作（如发起评估、上传知识库、删除文档、修改配置）；日志不可被普通用户篡改。 | Audit log: who did what to which resource and when (e.g. start assessment, upload KB, delete doc, change config); logs not modifiable by normal users. | 结构化日志写入专用存储或文件；访问权限与保留期单独管理。 |
| OPS-02 | 运行日志与监控：记录请求 ID、错误、耗时与关键资源使用；不记录敏感正文或完整凭据。 | Operational logs and monitoring: request ID, errors, latency, key resource usage; do not log sensitive content or full credentials. | 见 PRD 7 可观测性；敏感字段脱敏或排除。 |
| OPS-03 | 安全事件与异常可被检测与告警（如大量失败登录、异常 API 调用模式、资源耗尽）；定义简单响应流程。 | Security events and anomalies detectable and alertable (e.g. mass failed logins, anomalous API patterns, resource exhaustion); define a simple response process. | 监控与告警规则；文档化响应步骤与联系人。 |
| OPS-04 | 备份与恢复：关键数据（如知识库索引、配置、审计库）有定期备份；恢复流程经过验证。 | Backup and recovery: critical data (KB index, config, audit store) backed up regularly; recovery procedure tested. | 见 05-deployment-runbook；定期演练恢复。 |

---

#### 7.2.6 供应链与开源 | Supply Chain and Open Source

| 控制项 ID | 需求描述（中文）| Requirement (English) | 设计/实现要点 |
|-----------|------------------|------------------------|----------------|
| SCM-01 | 依赖来源可信：仅从官方或受控源获取依赖；校验完整性（如哈希、签名）若可用。 | Dependencies from trusted sources only; verify integrity (hash, signature) where available. | 使用官方 PyPI 或内部镜像；pip/poetry 校验。 |
| SCM-02 | 已知漏洞处理：对扫描发现的高危/严重漏洞制定修复或缓解计划并在合理时间内落地。 | Address known vulnerabilities: plan and implement fix or mitigation for high/critical findings within a defined timeframe. | 与 APP-03 联动；漏洞策略文档（如 30 天内修复严重）。 |
| SCM-03 | 开源许可合规：识别依赖的许可证，确保与项目许可与使用场景兼容；在 NOTICE 或文档中声明关键依赖。 | Open-source license compliance: identify licenses of dependencies, ensure compatibility with project license and use; acknowledge key dependencies in NOTICE or docs. | 使用 license-checker 等；README/NOTICE 列出主要依赖与许可。 |

---

#### 7.2.7 安全需求与设计落地 | Mapping to Design and Implementation

| 阶段 | 建议动作 |
|------|----------|
| **设计** | 在 01-architecture-and-tech-stack、04-integration-guide、05-deployment-runbook 中体现上述控制（认证方式、TLS、密钥管理、日志与备份）。 |
| **开发** | 在代码评审检查清单中包含 IAM、DATA、APP 相关项；CI 中集成依赖扫描与（若适用）静态安全扫描。 |
| **部署与运维** | 按 OPS 与 DATA 配置日志、备份、网络与密钥；定期复查权限与审计日志。 |
| **发布与合规** | 若对外交付或开源，提供安全说明（如 SECURITY.md）、漏洞披露方式与 SCM 合规信息。 |

**English**: Design phase—reflect the above controls in architecture, integration, and deployment docs. Development—include IAM/DATA/APP in code review checklist; integrate dependency and optional SAST in CI. Operations—configure logging, backup, network, and secrets per OPS/DATA; periodically review access and audit logs. Release—provide security documentation (e.g. SECURITY.md), vulnerability disclosure, and SCM compliance when distributing or open-sourcing.

---

## 八、参考与借鉴（开源 AI Agent 项目）| Section 8 — References (Open-Source AI Agent Projects)

#### 中文

以下项目在架构与能力上可作为参考，不表示本产品直接依赖其代码：

- **Docker Agent (cagent)**：YAML 配置驱动的多 Agent、多 LLM、MCP 工具生态与 RAG，适合作为「可插拔 LLM + 工具」的参考。
- **VoltAgent AI Agent Platform**：覆盖编排、多模型抽象、记忆、RAG、可观测性等 11 类能力，适合作为「生产级 Agent 平台」的架构参考。
- **GitHub Agentic Workflows**：基于 Markdown 的工作流与多引擎决策，强调安全与审批，可借鉴「人类在环」与安全策略。
- **Agent 记忆架构**：工作记忆 / 情景记忆 / 语义记忆分层、RAG 与向量库、会话压缩与 TTL，可与本 PRD 中的「记忆体」设计对应。

#### English

The following projects can be used as architectural and capability references; this product does not necessarily depend on their code:

- **Docker Agent (cagent)**: YAML-driven multi-agent, multi-LLM, MCP tooling, and RAG; useful as a reference for “pluggable LLM + tools.”
- **VoltAgent AI Agent Platform**: Covers 11 areas including orchestration, multi-model abstraction, memory, RAG, and observability; useful as a “production Agent platform” architecture reference.
- **GitHub Agentic Workflows**: Markdown-based workflows and multi-engine decisions with emphasis on security and approval; useful for “human-in-the-loop” and safety policies.
- **Agent memory architecture**: Layered working / episodic / semantic memory, RAG and vector stores, session compression and TTL; maps to the “Memory” design in this PRD.

---

## 九、后续步骤建议 | Section 9 — Next Steps

#### 中文

1. **技术选型**：确定语言（如 Python）、框架（如 LangChain/LangGraph）、向量库、文件解析库（如 python-docx、PyMuPDF、openpyxl）与 LLM SDK 抽象层形态。
2. **MVP 范围**：先实现「单种文件（如 PDF + Excel）+ 单知识库 + 单 Skill（问卷/策略比对）+ 1～2 种 LLM」，完成端到端闭环；在此基础上增加 **AAD 登录** 与 **ServiceNow 项目元数据读取**（适配器接口 + 首个实现），以及基础 RBAC。
3. **企业集成与 IAM**：与 IT 确认 AAD 应用注册、权限范围与网络可达性；与项目管理方确认 ServiceNow（或等效平台）API、项目/工单数据模型与权限，设计适配器与元数据映射。
4. **试点**：与 1～2 个内部或合作团队试点，收集对报告质量、效率与可操作性的反馈，迭代知识库与 Skill 设计，并验证 AAD/ServiceNow 集成与角色权限是否符合实际流程。
5. **开源与社区**：在 MVP 稳定后，以「安全 AI Agent」为定位开源，提供清晰架构文档与扩展点（Skill、Parser、LLM 适配器、**集成适配器**），吸引安全与 AI 双背景贡献者。

#### English

1. **Technology choices**: Decide on language (e.g. Python), framework (e.g. LangChain/LangGraph), vector store, file parsing libraries (e.g. python-docx, PyMuPDF, openpyxl), and LLM SDK abstraction.
2. **MVP scope**: Implement “one or two file types (e.g. PDF + Excel) + single knowledge base + one Skill (questionnaire/policy comparison) + 1–2 LLM backends” to close the end-to-end loop; then add **AAD login** and **ServiceNow project metadata** (adapter interface + first implementation) and basic RBAC.
3. **Enterprise integration and IAM**: Align with IT on AAD app registration, scopes, and network reachability; with project management on ServiceNow (or equivalent) API, project/ticket data model, and permissions; design adapter and metadata mapping.
4. **Pilot**: Run pilots with 1–2 internal or partner teams, gather feedback on report quality, efficiency, and actionability, iterate on knowledge base and Skill design, and validate AAD/ServiceNow integration and role permissions against real workflows.
5. **Open source and community**: After MVP stabilizes, open source under the “Arthor Agent” positioning with clear architecture docs and extension points (Skills, Parser, LLM adapters, **integration adapters**) to attract contributors with both security and AI background.

---

## 十、开发前待澄清与建议产出 | Section 10 — Open Questions and Deliverables for Development

本节列出在**直接依据本 PRD 开展开发**前建议澄清的问题，以及建议先产出的设计/规范文档，以便团队有一致的技术约定。

### 10.1 总体结论 | Verdict

**中文**：本 PRD 已具备**业务与产品层面的完整性**（痛点、方案、架构、功能、非功能、用户故事、后续步骤），可作为项目立项与需求评审的依据。若要**直接支撑开发与构建**，建议在技术选型后补充以下「待澄清项」与「建议产出」，再进入迭代开发；也可采用「先做 MVP 闭环、再逐步补全」的方式，在开发过程中同步完善这些产出。

**English**: This PRD is **complete at the business and product level** (pain points, solution, architecture, features, NFRs, user stories, next steps) and can be used for project kick-off and requirement review. To **directly support development and implementation**, it is recommended to resolve the “open questions” below and produce the “recommended deliverables” after technology choices; alternatively, adopt an “MVP first, then iterate” approach and refine these artifacts in parallel with development.

---

### 10.2 待澄清问题（建议在技术设计前确认）| Open Questions

#### 中文

| 类别 | 问题 | 说明 |
|------|------|------|
| **接口契约** | 核心 API 的请求/响应形态？ | 如：提交评估任务、获取评估结果、知识库上传/检索、项目元数据拉取等接口的 URL、方法、请求体与响应体结构需在技术设计阶段定稿，便于前后端与集成方对齐。 |
| **评估报告结构** | 结构化报告的具体 schema？ | 「风险项、合规差距、整改建议、优先级」在 JSON/Markdown 中的字段命名、层级与可选字段（如引用条款、证据建议）需统一，便于前端展示与回写 ServiceNow。 |
| **Skill 契约** | 首个 Skill 的入参/出参？ | 至少一个评估 Skill（如问卷与策略比对）的输入、输出 JSON Schema 或示例，便于编排层与 Skill 实现方并行开发。 |
| **知识库切块** | 切块策略与参数？ | 块大小、重叠、按标题/段落切分等策略未在 PRD 中规定，影响 RAG 效果，需在技术设计或试点中确定。 |
| **项目管理平台** | ServiceNow 具体表/API？ | 项目元数据来自哪些表或 API（如 Project、Change、CMDB）、必选/可选字段及与「评估场景」「合规范围」的映射关系，依赖实际环境，建议与运维/项目管理方对齐后文档化。 |
| **边界与降级** | 失败与限流策略？ | 单文件大小上限、单次评估文件数量上限、解析失败/LLM 超时时的返回格式与重试策略、并发与限流策略，影响 SLA 与用户体验，建议在 NFR 或技术方案中明确。 |
| **MVP 与阶段** | P0 的交付顺序？ | 功能表中 P0 较多，建议明确 Phase 1（MVP）与 Phase 2 的边界（如先不做 ServiceNow、先做本地账号再上 AAD），便于排期与验收。 |
| **开源与许可** | 项目开源协议？ | 若计划开源，建议在 README 或 CONTRIBUTING 中明确许可证（如 Apache 2.0、MIT）与贡献流程。 |

#### English

| Category | Question | Note |
|----------|----------|------|
| **API contract** | Request/response shape for core APIs? | e.g. submit assessment, get result, KB upload/query, project metadata; URL, method, body schema should be fixed in technical design for frontend and integration. |
| **Assessment report schema** | Concrete schema for structured report? | Field names, hierarchy, and optional fields (e.g. clause reference, evidence suggestion) for risk items, compliance gaps, remediation, priority in JSON/Markdown for UI and ServiceNow write-back. |
| **Skill contract** | Input/output for the first Skill? | At least one assessment Skill (e.g. questionnaire vs policy) needs input/output JSON Schema or example for orchestration and Skill implementation to develop in parallel. |
| **KB chunking** | Chunking strategy and parameters? | Chunk size, overlap, section-based vs fixed-size not specified in PRD; affects RAG quality; to be decided in technical design or pilot. |
| **Project management platform** | Concrete ServiceNow tables/APIs? | Which tables/APIs (e.g. Project, Change, CMDB) and which fields map to “project metadata” and to “assessment scenario / compliance scope”; document after alignment with ops/project management. |
| **Limits and fallback** | Failure and rate-limit policy? | Max file size, max files per assessment, response format and retry on parse/LLM failure, concurrency and rate limits; recommend defining in NFR or technical design. |
| **MVP vs phases** | Delivery order of P0s? | Many P0s in the feature list; recommend defining Phase 1 (MVP) vs Phase 2 (e.g. no ServiceNow in MVP, local auth before AAD) for scheduling and acceptance. |
| **Open source and license** | Project license? | If open-sourcing, state license (e.g. Apache 2.0, MIT) and contribution process in README or CONTRIBUTING. |

---

### 10.3 建议产出的设计/规范文档 | Recommended Deliverables

#### 中文

在进入编码前或与编码并行，建议产出以下文档（可与本 PRD 同仓或同项目下维护）：

1. **技术选型与架构设计**：语言、框架、向量库、解析库、部署方式；组件间接口与数据流（可引用本 PRD 第五章）。
2. **API 规范**：REST 端点列表、请求/响应示例、错误码与认证方式（OpenAPI/Swagger 优先）。
3. **评估报告与 Skill 契约**：报告 JSON Schema；至少一个 Skill 的 I/O Schema 或示例。
4. **集成说明**：AAD 应用注册与必选 scope；ServiceNow（或等效）适配器需调用的 API 与字段映射。
5. **部署与运行手册**：环境要求、配置项、与 AAD/ServiceNow/LLM 的网络与防火墙要求（对应 NFR 中的部署与连通性）。
6. **安全落地**：将 PRD §7.2 安全需求与安全控制纳入架构与运维文档；建议在仓库中提供 SECURITY.md（漏洞披露方式、安全相关配置与检查清单），并在代码评审与 CI 中体现 APP/SCM 类控制。

#### English

Before or in parallel with coding, the following artifacts are recommended (maintained in the same repo or project as this PRD):

1. **Technology choices and architecture**: Language, framework, vector store, parsing libs, deployment; component interfaces and data flow (can reference Section 5 of this PRD).
2. **API specification**: REST endpoint list, request/response examples, error codes and auth (OpenAPI/Swagger preferred).
3. **Assessment report and Skill contract**: Report JSON Schema; I/O Schema or example for at least one Skill.
4. **Integration guide**: AAD app registration and required scopes; APIs and field mapping for ServiceNow (or equivalent) adapter.
5. **Deployment and runbook**: Environment requirements, configuration, network and firewall requirements for AAD, ServiceNow, LLM (per deployment/connectivity NFR).
6. **Security implementation**: Reflect PRD §7.2 Security Requirements and Controls in architecture and ops docs; provide SECURITY.md in repo (vulnerability disclosure, security-related config and checklist); reflect APP/SCM controls in code review and CI.

---

### 10.4 能否据此开展项目开发构建？| Can We Use This PRD to Start Building?

**中文**：**可以。** 本 PRD 足以作为**需求基线**开展项目：确定技术栈、划分 MVP/Phase 1、分配模块（Parser、KB、Agent、LLM 抽象、IAM、集成适配器），并按照功能列表与用户故事做迭代开发与验收。建议在**第一个迭代或技术设计阶段**内，对 10.2 中的待澄清项做决策并沉淀为 10.3 中的设计/规范文档，以便接口、数据格式与集成方式在团队内一致，减少返工。若资源有限，可优先实现「无 AAD/无 ServiceNow」的本地 MVP（文件上传 → 解析 → 知识库检索 + 单 Skill + 单 LLM → 报告输出），再在后续迭代接入 IAM 与企业集成。

**English**: **Yes.** This PRD is sufficient as a **requirements baseline** to start the project: decide the tech stack, define MVP/Phase 1, assign modules (Parser, KB, Agent, LLM abstraction, IAM, integration adapters), and iterate against the feature list and user stories. Resolve the open questions in 10.2 and produce the deliverables in 10.3 **within the first iteration or technical design phase** so that APIs, data formats, and integrations are consistent and rework is minimised. If resources are limited, prioritise a local MVP without AAD/ServiceNow (file upload → parse → KB retrieval + one Skill + one LLM → report output), then add IAM and enterprise integrations in later iterations.

---

**文档结束 | End of Document**

*本文档为 Arthor Agent 项目的产品需求说明，后续可根据技术设计与试点反馈进行版本迭代。*  
*This document is the product requirements specification for the Arthor Agent project and may be revised based on technical design and pilot feedback.*
