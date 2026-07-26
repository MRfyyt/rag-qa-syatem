import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
import chromadb
from openai import OpenAI 
from dotenv import load_dotenv 
from sentence_transformers import SentenceTransformer

load_dotenv()

# 本地 Embedding 模型
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text: str) -> list[float]:
    return embed_model.encode(text).tolist()

#ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="my_knowledge_base")

def clear_collection():
    """清空知识库"""
    global collection
    chroma_client.delete_collection(name="my_knowledge_base")
    collection = chroma_client.get_or_create_collection(name="my_knowledge_base")
    print("知识库已清空")

def add_documents(documents: list[str], ids: list[str] = None):
    """把文档存入向量数据库"""
    if ids is None:
        ids = [f"doc_{i}" for i in range(len(documents))]

    embeddings = [get_embedding(doc) for doc in documents]

    collection.add(
        documents = documents,
        embeddings =embeddings,
        ids =ids,
    )
    print(f"已存入{len(documents)}条文档")

def search(query:str,top_k:int = 3):
    """搜索相关文档"""
    query_embedding = get_embedding(query)

    results = collection.query(
        query_embeddings = [query_embedding],
        n_results = top_k,
    )
    return results["documents"][0]

client = OpenAI(
    api_key = os.getenv("DEEPSEEK_API_KEY"),
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
)

def ask(question:str,docs:list[str])->str:
    """检索+生成:RAG完整流程"""
    context = "\n".join(docs)

    context = "\n".join(docs)
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
        temperature = 0.3,
        stream = False,
    )
    return response.choices[0].message.content

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
