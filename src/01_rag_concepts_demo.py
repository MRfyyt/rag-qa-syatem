"""
RAG 核心概念 —— 一次性跑通
=============================
跑法: python src/01_rag_concepts_demo.py

RAG = Retrieval Augmented Generation（检索增强生成）
5 个步骤: 加载 → 切分 → 向量化 → 检索 → 生成
"""

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# ============================================================
# 概念 1: 加载文档 —— 把你要"喂"给 AI 的资料读进来
# ============================================================
print("=" * 60)
print("步骤 1: 加载文档")
print("=" * 60)

# 先手动创建一条"知识库"（假装是 PDF 的内容）
documents = [
    "Python 是 Guido van Rossum 于 1991 年发明的编程语言。",
    "Python 3.13 版本引入了新的 JIT 编译器，大幅提升了性能。",
    "DeepSeek 是一家中国 AI 公司，其模型 deepseek-chat 拥有 128K 上下文窗口。",
    "RAG（检索增强生成）技术可以让大模型基于外部知识回答问题。",
    "ChromaDB 是一个轻量级的开源向量数据库，适合本地开发。",
]

print(f"  知识库里有 {len(documents)} 条文档:")
for i, doc in enumerate(documents):
    print(f"    [{i}] {doc[:50]}...")

print("\n▶ 步骤 2: 文本切分"); print("-" * 40)

# ============================================================
# 概念 2: 文本切分 —— 把长文档切成小段 (Chunk)
# ============================================================
print()
print("  为什么要切分？")
print("  - LLM 的上下文窗口有限，不能一次塞整本书")
print("  - 每段太大 → 检索不精确；太小 → 缺少上下文")
print("  - 经验值: 每段 200-500 字")
print()
print("  在上面的例子中，每条文档已经是一个合理大小的 Chunk，不需要再切。")

print("\n▶ 步骤 3: 向量化 (Embedding)"); print("-" * 40)

# ============================================================
# 概念 3: Embedding —— 把文本变成向量（一串数字）
# ============================================================
print()

# 用 DeepSeek 的 embedding 来演示（需要联网）
# 但如果不想调用 API，先用一个伪代码演示

print("""
  Embedding 的直观理解:

  文本: "Python 是 Guido van Rossum 发明的"
    ↓ Embedding 模型
  向量: [0.23, -0.15, 0.87, 0.41, ..., -0.33]  ← 比如 1024 个数字
                    ↑
              这串数字编码了这句话的"语义"

  相似的两句话 → 它们的向量在空间中距离很近
  "Python 是谁发明的"     → 向量 A
  "Python 由 Guido 创造"  → 向量 B   （和 A 很近 ✓）
  "今天天气很好"          → 向量 C   （和 A 很远 ✗）
""")

print("▶ 步骤 4: 存储到向量数据库 & 检索"); print("-" * 40)

# ============================================================
# 概念 4: 向量数据库 + 检索
# ============================================================
print()

# 用 ChromaDB 实际演示
try:
    import chromadb
    from chromadb.utils import embedding_functions

    print("  正在用 DeepSeek 的 embedding 处理知识库...")

    # 创建客户端（数据存在内存里，不落盘）
    client = chromadb.Client()

    # 由于 ChromaDB 没有内置 DeepSeek embedding，这里用一个简化的方式
    # 实际项目中会用 OpenAI 兼容的 embedding API

    print("  ⚠️  完整的 Embedding 需要调用 API，这里只演示向量数据库的结构")
    print()
    print("  ChromaDB 的数据模型:")
    print("  ┌─────────────────────────────────────┐")
    print("  │ Collection（集合）                     │")
    print("  │  ├── Document 0: \"Python 是...\"     │")
    print("  │  │   ├── id: \"doc_0\"               │")
    print("  │  │   ├── embedding: [0.23, -0.15...]│")
    print("  │  │   └── metadata: {source: \"...\"} │")
    print("  │  ├── Document 1: \"Python 3.13...\"  │")
    print("  │  └── ...                             │")
    print("  └─────────────────────────────────────┘")
    print()
    print("  检索过程:")
    print("  用户问题 \"Python 最新版本是什么？\"")
    print("    → 用同一个 Embedding 模型把问题也转成向量")
    print("    → 在 Collection 里找最相似的 K 个文档")
    print("    → 返回 Document 1: \"Python 3.13...\"（最相关）")

except ImportError:
    print("  ⚠️ chromadb 还没安装，稍后安装即可")
    print("  概念先行，不影响理解")

print("\n▶ 步骤 5: 增强生成"); print("-" * 40)

# ============================================================
# 概念 5: 增强生成 —— 检索结果 + 用户问题 → LLM
# ============================================================
print("""
  最后一步: 把检索到的文档和用户问题拼在一起，发给 LLM

  System Prompt:
    "你是一个知识库助手。只根据以下参考资料回答问题。如果参考资料中没有答案，就说不知道。"

  User Message:
    参考资料:
    ---
    Python 3.13 版本引入了新的 JIT 编译器，大幅提升了性能。
    ---
    问题: Python 最新版本有什么新特性？

  LLM 回复:
    "根据资料，Python 3.13 版本引入了新的 JIT 编译器，大幅提升了性能。"

  👆 这就是 RAG 的完整流程！
  LLM 不需要"记住"Python 3.13 有什么新特性，
  而是从你给的资料里找到答案 → 组织语言 → 返回。
""")

print("=" * 60)
print("🎉 RAG 5 个步骤全部过完！")
print("=" * 60)
print()
print("下一步: 安装依赖，搭建真实的 RAG 问答系统")
print("  - ChromaDB: 向量数据库")
print("  - 你的 DeepSeek Key: 既当 Embedding 模型，又当生成模型")
