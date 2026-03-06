# 如何录制 30 秒演示 | How to record the 30s demo

用下面任一方式跑一遍流程，同时用录屏软件录制，保存为 **`docs/images/demo-assessment.gif`**，README 会自动展示。

---

## 方式一：浏览器 + 本地页面（推荐，画面清晰）

1. **启动 API**（二选一）：
   ```bash
   # 终端 1
   cd Arthor-Agent
   source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
   或 `docker compose up -d`（确保 8000 端口可用）。

2. **打开演示页**：用浏览器打开 **`docs/demo.html`**（双击文件，或先 `cd docs && python -m http.server 8888` 再打开 http://localhost:8888/demo.html，避免 file:// 的 CORS 限制）。

3. **开始录屏**（macOS：QuickTime → 文件 → 新建屏幕录制；或 [LICEcap](https://www.cockos.com/licecap/) 录成 GIF）。

4. **操作**（约 20–30 秒）：
   - 点击「选择文件」，选 **`examples/sample.txt`**；
   - 点击 **Assess**；
   - 等待 2–5 秒，页面下方出现 JSON 报告；
   - 结束录屏。

5. **保存**：将录制的视频导出为 GIF，命名为 **`demo-assessment.gif`**，放到 **`docs/images/`**。

---

## 方式二：Swagger UI（/docs）

1. 启动 API 后，浏览器打开 **http://localhost:8000/docs**。
2. 录屏开始。
3. 找到 **POST /api/v1/assessments**，点 "Try it out" → 选择 `examples/sample.txt` → Execute。
4. 在 Response 里看到 `task_id`，复制。
5. 找到 **GET /api/v1/assessments/{task_id}**，粘贴 task_id → Execute，看到报告。
6. 结束录屏，保存为 `docs/images/demo-assessment.gif`。

---

## 方式三：终端脚本（适合“极客”风格）

1. 启动 API（同上）。
2. 录屏（只录终端窗口）。
3. 运行：
   ```bash
   cd Arthor-Agent
   chmod +x scripts/demo.sh
   ./scripts/demo.sh
   ```
4. 看到 JSON 输出后结束录屏，保存为 `docs/images/demo-assessment.gif`。

---

## 将 GIF 放进 README

GIF 放到 **`docs/images/demo-assessment.gif`** 后，在 README 的 Quick Start 顶部把占位换成：

```markdown
![Demo: upload → assessment report](docs/images/demo-assessment.gif)
```

推送后若在 GitHub 上不显示，可使用绝对地址：

```markdown
![Demo](https://github.com/arthurpanhku/Arthor-Agent/raw/main/docs/images/demo-assessment.gif)
```
