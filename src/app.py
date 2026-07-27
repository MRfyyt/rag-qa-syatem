# ============================================================
# app.py — Streamlit Web 界面
# ============================================================
# 职责: 提供浏览器端的文件上传 + 知识库管理 + 问答界面。
# 依赖: rag.py（所有核心逻辑都在那里，本文件只管 UI）
# 注意: Streamlit 的执行模型是"每次交互都重跑整个脚本"——
#       st.session_state 用来记住跨重跑的状态（比如上次上传的文件名）。
# ============================================================

import streamlit as st
from rag import search, ask, add_documents, clear_collection, collection, get_embedding

st.set_page_config(page_title="RAG 知识库问答", page_icon="📚")

st.title("📚 RAG 知识库问答系统")
st.caption("上传文档 → 构建知识库 → 提问 → 获得答案")

# ============================================================
# 左侧栏: 文档上传 + 知识库管理
# ============================================================
with st.sidebar:
    st.header("📄 上传文档")
    uploaded_file = st.file_uploader("选择 PDF 或 TXT 文件", type=["pdf", "txt"])

    if uploaded_file is not None:
        # ---- 避免重复处理: 用 session_state 记录上次处理的文件名 ----
        if "last_file" not in st.session_state:
            st.session_state.last_file = None

        if uploaded_file.name != st.session_state.last_file:
            st.session_state.last_file = uploaded_file.name
            raw = uploaded_file.read()
            filename = uploaded_file.name.lower()

            # ---- 根据文件类型选择解析方式 ----
            if filename.endswith(".pdf"):
                # PDF: 用 pypdf 逐页提取文字
                from pypdf import PdfReader
                import io
                reader = PdfReader(io.BytesIO(raw))
                text_parts = []
                for page in reader.pages:
                    t = page.extract_text()
                    if t:
                        text_parts.append(t)
                content = "\n".join(text_parts)
            else:
                # TXT: 逐编码尝试解码（Windows 中文系统常用 GBK）
                for encoding in ["utf-8", "gbk", "latin-1"]:
                    try:
                        content = raw.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue

            # ---- 按换行切段（简化版 chunking） ----
            chunks = [c.strip() for c in content.split("\n") if c.strip()]

            if not chunks:
                st.error("未提取到文字内容")
            else:
                # 存入 ChromaDB（文本 → Embedding → 存库）
                add_documents(chunks)
                st.success(f"已添加 {len(chunks)} 条文档")

    # ---- 清空知识库按钮 ----
    if st.button("🗑️ 清空知识库"):
        clear_collection()
        st.session_state.last_file = None
        st.success("知识库已清空")
        st.rerun()  # 强制刷新页面

# ============================================================
# 主区域: 问答
# ============================================================
question = st.text_input("💬 输入你的问题")
if question:
    with st.spinner("正在检索..."):
        # Step 1: 向量检索
        result = search(question)
        # Step 2: 把检索结果传给 ask()（不重复搜索——这是修复后的版本）
        answer = ask(question,result)

    st.markdown("### 🤖 回答")
    st.write(answer)

    st.markdown("### 📖 参考来源")
    for doc in result:
        st.info(doc)
