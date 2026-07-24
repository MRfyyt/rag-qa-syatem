# RAG 项目深度复盘

> 复盘时间：2026-07-24  
> 项目：RAG 知识库问答系统

---

## 一、完整数据流追踪

追踪一个请求从上传到回答的全路径：

```
用户上传 test.txt
  │
  ├─ app.py:14  st.file_uploader → 拿到文件对象
  ├─ app.py:20  uploaded_file.name → "test.txt"
  ├─ app.py:34  raw.decode("utf-8") → "RAG即检索增强生成..."
  ├─ app.py:44  content.split("\n") → ["段落1", "段落2", ...]
  │
  ├─ app.py:50  add_documents(chunks)
  │               │
  │               ├─ rag.py:30  get_embedding("段落1") → [0.02, -0.11, ...]
  │               ├─ rag.py:30  get_embedding("段落2") → [0.05, 0.13, ...]
  │               │  (本地模型，384维向量，不联网)
  │               │
  │               └─ rag.py:32  collection.add(文本 + 向量 + ID)
  │                              │
  │                              └─ chroma_db/ 文件夹里持久化
  │
用户提问 "什么是RAG"
  │
  ├─ app.py:62  search("什么是RAG")
  │               │
  │               ├─ rag.py:46  get_embedding("什么是RAG") → [0.01, -0.08, ...]
  │               └─ rag.py:48  collection.query(问题向量, top_k=3)
  │                              → ChromaDB 比较 384 维空间中向量距离
  │                              → 返回最相似的 3 条文档
  │
  ├─ app.py:63  ask("什么是RAG")
  │               │
  │               ├─ rag.py:62  search("什么是RAG")   ← 再搜一次（冗余！）
  │               ├─ rag.py:64  context = "文档1\n文档2\n文档3"
  │               ├─ rag.py:65  prompt = "参考资料：...\n问题：..."
  │               └─ rag.py:72  client.chat.completions.create(...)
  │                              → DeepSeek API (联网，按量付费)
  │                              → "RAG是检索增强生成技术..."
  │
  └─ app.py:66  st.write(answer)  → 浏览器显示回答
```

---

## 二、发现的问题

### 严重：`ask()` 重复调用 `search()`

```python
# app.py 第 62-63 行
result = search(question)     # 第一次向量检索
answer = ask(question)         # ask() 内部第 62 行又做一次向量检索
```

每次提问，向量检索跑了**两遍**，浪费计算资源。

修复方向：`ask()` 接受已检索的文档作为参数，避免重复搜索。

### 中等：文本切分太粗糙

```python
chunks = content.split("\n")   # 只按换行切
```

- 一整段没有换行 → 整个文件变成一个 chunk → 检索精度差
- 每句都换行 → chunk 太小 → 缺少上下文

修复方向：按固定字数切（如 300 字一段），段间重叠 50 字。

### 中等：没有模型缓存保护

```python
embed_model = SentenceTransformer("all-MiniLM-L6-v2")  # 每次 import 都加载
```

程序启动时自动加载 90MB 的 Embedding 模型，即使这次运行不需要。

修复方向：延迟加载——只在第一次调用 `get_embedding()` 时才初始化。

### 小问题：`global` 不优雅

```python
def clear_collection():
    global collection
```

能跑，但更好的方式是用类封装，避免全局变量。

---

## 三、架构评价

```
当前架构：

  app.py (Streamlit UI)
    │
    └── rag.py (所有逻辑混在一起)
          ├── Embedding 加载
          ├── ChromaDB 操作
          ├── search()
          └── ask()
```

**当前优点：** 简单直接，两个文件就能跑。

**当前缺点：** 功能增加时维护困难。

**更好的分层（后续项目参考）：**

```
app.py          → 只管 UI，不碰数据逻辑
knowledge.py    → ChromaDB 增删改查
embedder.py     → Embedding 模型加载和调用
generator.py    → DeepSeek 生成回答
```

---

## 四、概念掌握度检查

| 概念 | 代码位置 | 应该能解释 |
|------|----------|-----------|
| Embedding | `rag.py:13-14` | "把文本变成 384 个数字，语义相近的向量空间距离近" |
| 向量数据库 | `rag.py:17-18` | "存向量 + 搜相似向量，给 AI 建外部记忆" |
| 语义检索 | `rag.py:46-51` | "不拼关键词，拼语义相似度" |
| RAG 完整链路 | `rag.py:59-79` | "检索文档 → 拼 Prompt → LLM 基于文档回答" |
| Chunking | `app.py:44` | "长文档切小块，每块是独立检索单元" |
| System Prompt | `rag.py:71` | "约束 LLM 只基于给的资料回答，不瞎编" |
| Streamlit | `app.py` 全文 | "Python 快速搭建 Web 界面的框架" |

---

## 五、和 Week 1 的关系

```
Week 1: CLI AI 助手                    Week 2: RAG 问答
  ├── 纯 LLM 对话                        ├── LLM + 外部知识
  ├── 流式输出                           ├── 向量检索
  ├── @retry / TokenCounter / Pydantic   ├── ChromaDB / Embedding / Streamlit
  └── DeepSeek API 基础用法              └── DeepSeek API + Prompt 工程
```

---

## 六、面试可能追问

| 问题 | 答案要点 |
|------|---------|
| 为什么用本地 Embedding？ | DeepSeek 无 Embedding API；本地免费、离线、快 |
| 为什么选 ChromaDB？ | 轻量、Python 原生、无需 Docker、适合原型 |
| 检索返回不相关文档怎么办？ | 调大 top_k、ReRank 二次排序、混合检索（关键词+语义） |
| 1000 人同时用会崩在哪？ | Embedding 模型 CPU 瓶颈、ChromaDB 单机限制、API 频率限制 |

---

## 七、踩坑记录

| 坑 | 学到的 |
|----|--------|
| DeepSeek 不支持 Embedding | 查官方文档 + GitHub Issues，不瞎猜 |
| HuggingFace 被墙 | 国内镜像 `hf-mirror.com` |
| PDF 扫描版提不出文字 | PDF 分文字型 vs 图片型 |
| `chroma_db/` 残留旧数据 | 持久化数据库的状态管理 |
| `st.button` + `file_uploader` 冲突 | Streamlit 每次交互都重跑整个脚本 |
| GBK / UTF-8 编码问题 | Windows 中文系统默认 GBK，需多编码尝试 |
| `ask()` 重复调 `search()` | 追踪数据流才能发现冗余 |
