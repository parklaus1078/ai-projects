import os
import tempfile
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import streamlit as st
from constants.common_constants import GPT_MODEL

@st.cache_resource
def get_vectorstore(pdf_file):
    """PDF 파일을 받아 벡터 DB(FAISS)를 반환 (캐싱 적용)"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(pdf_file.getvalue())
        tmp_path = tmp_file.name

    loader = PyPDFLoader(tmp_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(splits, embeddings)

    os.remove(tmp_path)
    return vectorstore

def get_rag_chain(vectorstore: FAISS):
    """벡터 DB를 기반으로 질의응답 Chain을 생성하여 반환"""
    llm = ChatOpenAI(model=GPT_MODEL, temperature=0)
    retriever = vectorstore.as_retriever()
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    template = """
    당신은 문서를 분석해주는 AI 연구원입니다.
    아래 [Context]를 바탕으로 질문에 답하세요.
    
    [Context]:
    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain
