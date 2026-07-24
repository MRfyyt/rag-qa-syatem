# RAG 项目整体思路回顾

> 记录时间：2026-07-24  
> 项目：RAG 知识库问答系统

---

## 一、核心问题

> **"让 LLM 基于你没有训练过的文档回答问题，并且不瞎编。"**

---

## 二、从零到一的 5 步推导

每一步都在解决上一步暴露的问题：

| 步骤 | 尝试 | 结果 | 暴露的问题 |
|:--:|------|:--:|------|
| ① | 把整个文件塞进 Prompt | ❌ | Context Window 有限，大文件塞不下 |
| ② | Ctrl+F 搜关键词，发给 LLM | ❌ | 用户问"谁发明的"，原文写的是"Guido 创造"——关键词不匹配 |
| ③ | 把文本变成向量，搜语义相似 | ✅ | 需要把每段都向量化，还要存起来 |
| ④ | 用向量数据库预计算+存储 | ✅ | 搜出来的文档怎么给 LLM？ |
| ⑤ | 拼到 Prompt 里，约束 LLM 只基于资料回答 | ✅ | — |

---

## 三、技术选型推导

| 选择 | 原因 |
|------|------|
| **sentence-transformers** 做 Embedding | DeepSeek 不提供 Embedding API；本地免费、不用联网 |
| **ChromaDB** 做向量存储 | 最轻量，Python 一行安装，不需要装 Docker |
| **DeepSeek** 做生成 | 已有 API Key，v4-pro 推理能力强 |
| **Streamlit** 做界面 | 比 Gradio 灵活，纯 Python，不需要 HTML/CSS/JS |

---

## 四、文件分工推导

只需回答 3 个问题：

| 问题 | 答案 | 文件 |
|------|------|------|
| 怎么向量化、存储、搜索、生成？ | 核心逻辑 | `src/rag.py` |
| 怎么让用户在浏览器里用？ | Web 界面 | `src/app.py` |
| 别人拿到代码怎么跑？ | 配置 + 文档 | `.env` + `requirements.txt` + `README.md` |

---

## 五、开发路径：先跑通，再包装

```
Step 1: 教学脚本 (01_rag_concepts_demo.py)
  → 纯文字 + 伪代码解释 5 个步骤，建立直觉

Step 2: 最小可跑版本 (rag.py 测试代码)
  → 4 条硬编码文档 → search() → ask()
  → 终端验证 "Python 是谁发明的" 返回正确答案
  → 还没有界面，没有文件上传，但核心链路通了
  │
  │  ⚠️ 关键原则：Step 2 不跑通，绝不开始 Step 3
  │     如果一开始就写界面，出错时分不清是 UI 问题还是逻辑问题
  │
Step 3: 加 Web 界面 (app.py)
  → Streamlit 包装：文件上传 + 提问 + 显示
  → 遇到真实问题：PDF 解码、编码检测、扫描版失败、按钮冲突

Step 4: 清理 & 推送
  → .gitignore 防泄露 API Key
  → README 写文档
  → GitHub 公开
```

---

## 六、RAG 一句话总结

> **RAG = Embedding（语义搜索）+ Prompt Engineering（搜索结果喂给 LLM）+ 一个简单的 Web 壳。**

---

## 七、你能从零重现它吗？

关掉所有代码，你能否凭理解写出以下骨架：

```python
# rag.py 骨架
1. 加载 Embedding 模型
2. 连接 ChromaDB
3. add_documents() — 文本 → 向量 → 存库
4. search()        — 问题 → 向量 → 搜相似
5. ask()           — 搜 + 拼 Prompt + 调 DeepSeek

# app.py 骨架
1. 文件上传组件
2. 读文件 → add_documents()
3. 提问输入框
4. search() → ask() → 显示
```

**如果能写出这个骨架，你就真正掌握了 RAG。**
