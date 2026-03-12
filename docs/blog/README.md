# Blog posts (outlines and drafts)

Q1 goal: publish 1–2 English posts to drive traffic and stars. Publish on Dev.to, Medium, or your own blog; link back to the repo.

---

## Post 1: LLM + RAG for security questionnaire assessment

**Target title**: *How we use LLM + RAG to automate security questionnaire assessment (open-source)*

**Audience**: DevSecOps, security engineers, compliance leads.

**Outline**:
1. **Problem**: Security teams drown in questionnaires and evidence; manual review doesn’t scale.
2. **Approach**: One pipeline: upload docs → parse (PDF/Word/Excel) → RAG over policy KB → LLM produces structured report (risks, gaps, remediations).
3. **Tech**: FastAPI, Chroma, LangChain-style flow, OpenAI or Ollama. Why we support local LLM (privacy, air-gap).
4. **Open source**: DocSentinel, MIT. Quick start with Docker; link to repo and SPEC.
5. **What’s next**: More skills, AAD/SSO, ServiceNow. Invite contributions.

**CTA**: Star the repo, try `docker compose up`, open an issue for your use case.

**Keywords**: security questionnaire, compliance assessment, RAG, LLM, open source, self-hosted, Ollama.

---

## Post 2: Running security assessments locally with Ollama

**Target title**: *Run AI security assessments entirely on your laptop with Ollama*

**Audience**: Teams that can’t send docs to the cloud; privacy-conscious orgs.

**Outline**:
1. **Why local**: Sensitive questionnaires and design docs; no data leaves your network.
2. **Stack**: DocSentinel + Ollama; Docker Compose one-command run.
3. **Steps**: Clone → `docker compose up` → `ollama pull llama2` → upload a PDF via `/docs` or curl → get JSON report.
4. **Trade-offs**: Local model vs cloud (speed, quality, cost). When to use which.
5. **Link**: Repo, Quick Start, CHANGELOG.

**CTA**: Try it; if you’re on a different OS or model, we’d love feedback (issue or PR).

**Keywords**: Ollama, local LLM, security assessment, self-hosted, Docker, privacy.

---

## Checklist before publishing

- [ ] Run through Quick Start (Docker) and fix any broken steps.
- [ ] Add 1–2 screenshots or a short GIF (e.g. Swagger upload → response).
- [ ] Add repo link and “Star us on GitHub” in the first and last paragraph.
- [ ] Post in relevant communities after publish (see [LAUNCH-CHECKLIST.md](../LAUNCH-CHECKLIST.md)).
