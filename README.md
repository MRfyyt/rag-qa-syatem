# 📚 RAG 知识库问答系统

基于 **DeepSeek + 本地 Embedding + ChromaDB** 的检索增强生成（RAG）问答系统。上传文档，构建知识库，用自然语言提问，获得基于文档的准确回答。

## 🧠 什么是 RAG？

RAG（Retrieval-Augmented Generation）= 检索 + 生成

```
上传文档 → Embedding 向量化 → 存入 ChromaDB
                                    ↓
用户提问 → 向量检索找相关段落 → 拼接 Prompt → DeepSeek 生成回答
```

LLM 不需要"记住"你的文档内容，而是在回答前先搜索知识库，基于真实资料生成答案。

## ✨ 功能

- 📄 **多格式上传** — 支持 PDF 和 TXT 文件
- 🔍 **语义检索** — 用 Embedding 理解问题含义，不只靠关键词匹配
- 🤖 **智能生成** — DeepSeek 基于检索结果生成准确回答，带参考来源
- 🖥️ **Web 界面** — Streamlit 可视化操作，无需命令行
- 💾 **本地向量库** — ChromaDB 数据持久化，关掉程序知识不丢

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 配置 API Key

复制 `.env.example` 为 `.env`，填入你的 DeepSeek API Key：

```ini
DEEPSEEK_API_KEY=sk-your-real-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-pro
```

### 3. 运行

```bash
streamlit run src/app.py
```

浏览器打开 `http://localhost:8501`。

## 📖 使用方法

1. **上传文档** — 左侧边栏选择 PDF 或 TXT 文件，自动构建知识库
2. **清空知识库** — 需要换一批文档时，先点清空按钮
3. **提问** — 在输入框用自然语言提问
4. **查看来源** — 回答下方会显示引用的原文段落

## 📁 项目结构

```
RAG问答/
├── requirements.txt          # Python 依赖
├── .env                      # API Key 配置（不提交）
├── chroma_db/                # 向量数据库文件（不提交）
└── src/
    ├── 01_rag_concepts_demo.py  # RAG 5步教学脚本
    ├── rag.py                   # 核心逻辑：Embedding、存储、检索、生成
    └── app.py                   # Streamlit Web 界面
```

## 🔧 技术栈

| 环节 | 技术 |
|------|------|
| Embedding | sentence-transformers (all-MiniLM-L6-v2, 本地运行) |
| 向量数据库 | ChromaDB (持久化存储) |
| 生成模型 | DeepSeek API (deepseek-v4-pro) |
| Web 界面 | Streamlit |
| PDF 解析 | pypdf |

## ⚠️ 注意事项

- **扫描版 PDF 不支持** — 系统通过 pypdf 提取文字，无法识别图片中的文字（需要 OCR）
- **首次运行会下载模型** — Embedding 模型约 80MB，需网络连接（使用 HuggingFace 国内镜像）
- **DeepSeek API 需要联网** — 生成回答环节调用云端 API
