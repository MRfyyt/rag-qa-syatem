# ============================================================
# rag.py — RAG 核心逻辑模块
# ============================================================
# 职责: Embedding 向量化 → ChromaDB 存储 → 语义检索 → DeepSeek 生成回答。
# 依赖: sentence-transformers（本地 Embedding）、ChromaDB（向量数据库）、DeepSeek API（生成）
# 项目架构: app.py（UI）→ rag.py（本模块，核心逻辑）→ .env（配置）
#
# RAG = Retrieval Augmented Generation（检索增强生成）
# 5 步流程: 加载文档 → 切段 → Embedding 向量化 → 存向量库 → 检索+生成
# ============================================================

import os

# ⚠️ HuggingFace 被墙，必须在 import sentence_transformers 之前设置国内镜像
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

import chromadb
from openai import OpenAI
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

# ============================================================
# Embedding: 文本 → 384 维向量
# ============================================================
# all-MiniLM-L6-v2: 轻量、本地运行、免费，每个文本转成 384 个 float
# 为什么不用 DeepSeek Embedding? → DeepSeek 不提供 Embedding API（已查 GitHub Issues 确认）
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text: str) -> list[float]:
    """输入文本，返回 384 个 float 组成的向量。语义相近的文本向量距离近。"""
    return embed_model.encode(text).tolist()

# ============================================================
# ChromaDB: 向量存储 + 语义检索
# ============================================================
# PersistentClient: 数据存硬盘（chroma_db/ 文件夹），关了程序还在
# Collection: 相当于数据库里的"一张表"，所有文档向量都存在这里
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="my_knowledge_base")

def clear_collection():
    """清空知识库——删掉旧 Collection，新建空 Collection。"""
    global collection
    chroma_client.delete_collection(name="my_knowledge_base")
    collection = chroma_client.get_or_create_collection(name="my_knowledge_base")
    print("知识库已清空")

def add_documents(documents: list[str], ids: list[str] = None):
    """把文档存入向量数据库。每条文档: 文本 + 向量 + ID 三位一体存储。"""
    if ids is None:
        ids = [f"doc_{i}" for i in range(len(documents))]

    # 批量向量化——每条文档调用一次 get_embedding
    embeddings = [get_embedding(doc) for doc in documents]

    # 存入 ChromaDB（文本用于返回给用户看，向量用于数学比较）
    collection.add(
        documents = documents,
        embeddings =embeddings,
        ids =ids,
    )
    print(f"已存入{len(documents)}条文档")

def search(query:str,top_k:int = 3):
    """语义搜索: 把问题也转成向量 → 在 ChromaDB 里找最相似的 top_k 条文档。"""
    query_embedding = get_embedding(query)

    results = collection.query(
        query_embeddings = [query_embedding],
        n_results = top_k,
    )
    # results["documents"] 是二维列表 [["doc1", "doc2", ...]]
    # [0] 取第一个查询的结果（因为我们只查了一个 query）
    return results["documents"][0]

# ============================================================
# DeepSeek: 生成回答
# ============================================================
client = OpenAI(
    api_key = os.getenv("DEEPSEEK_API_KEY"),
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
)

def ask(question:str,docs:list[str])->str:
    """RAG 完整流程的最后一步: 检索结果 + 用户问题 → 拼接 Prompt → DeepSeek 生成回答。
    docs 参数由外部 search() 后传入，避免重复检索。"""

    # 拼接检索到的文档作为参考资料
    context = "\n".join(docs)

    # 构造 Prompt: 约束 LLM"只根据参考资料回答"，防止幻觉
    prompt = f"""你是一个知识库助手。只根据以下参考资料回答问题。如果资料中没有答案，就说"根据现有资料，我无法回答这个问题"。

参考资料：
{context}

问题：{question}"""

    response = client.chat.completions.create(
        model = os.getenv("DEEPSEEK_MODEL","deepseek-v4-pro"),
        messages = [
            {"role":"system","content":"用中文回答，简洁明确。"},
            {"role":"user","content":prompt},
        ],
        temperature = 0.3,     # 低随机性 → 更忠于原文，不瞎编
        stream = False,
    )
    return response.choices[0].message.content

# ---- 自检: 4 条硬编码文档 + 语义搜索 + RAG 回答 ----
if __name__ == "__main__":
    docs = [
        "Python 是 Guido van Rossum 于 1991 年发明的编程语言。",
        "Python 3.13 引入了 JIT 编译器，大幅提升了性能。",
        "ChromaDB 是一个轻量级向量数据库，适合本地开发。",
        "DeepSeek 是一家中国 AI 公司,deepseek-v4-pro 是其旗舰模型。",
    ]
    add_documents(docs)

    # 测试搜索
    results = search("Python 是谁发明的？")
    print("搜索结果：")
    for r in results:
        print(f"  - {r}")
    answer = ask("Python是谁发明的")
    print(f"\nAI回答:{answer}")
