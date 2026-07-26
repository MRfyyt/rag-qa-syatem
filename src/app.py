import streamlit as st
from rag import search, ask, add_documents, clear_collection, collection, get_embedding

st.set_page_config(page_title="RAG 知识库问答", page_icon="📚")

st.title("📚 RAG 知识库问答系统")
st.caption("上传文档 → 构建知识库 → 提问 → 获得答案")

# 左侧栏：上传文档
with st.sidebar:
    st.header("📄 上传文档")
    uploaded_file = st.file_uploader("选择 PDF 或 TXT 文件", type=["pdf", "txt"])

    if uploaded_file is not None:
        # 用文件名作为 key，避免重复处理
        if "last_file" not in st.session_state:
            st.session_state.last_file = None

        if uploaded_file.name != st.session_state.last_file:
            st.session_state.last_file = uploaded_file.name
            raw = uploaded_file.read()
            filename = uploaded_file.name.lower()

            if filename.endswith(".pdf"):
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
                for encoding in ["utf-8", "gbk", "latin-1"]:
                    try:
                        content = raw.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue

            chunks = [c.strip() for c in content.split("\n") if c.strip()]

            if not chunks:
                st.error("未提取到文字内容")
            else:
                add_documents(chunks)
                st.success(f"已添加 {len(chunks)} 条文档")

    if st.button("🗑️ 清空知识库"):
        clear_collection()
        st.session_state.last_file = None
        st.success("知识库已清空")
        st.rerun()

# 主区域：提问
question = st.text_input("💬 输入你的问题")
if question:
    with st.spinner("正在检索..."):
        result = search(question)
        answer = ask(question,result)

    st.markdown("### 🤖 回答")
    st.write(answer)

    st.markdown("### 📖 参考来源")
    for doc in result:
        st.info(doc)
