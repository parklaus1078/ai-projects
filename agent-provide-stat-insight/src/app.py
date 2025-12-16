import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# 모듈 임포트 (우리가 만든 파일들)
import utils
import logic_rag
import logic_csv
from constants.app_constants import Modes

# 1. 초기 설정
load_dotenv()
st.set_page_config(page_title="AI Multi-Modal Agent", layout="wide")
utils.init_environment()

# ==========================================
# [사이드바] 메뉴 및 파일 업로드
# ==========================================
with st.sidebar:
    st.title("🤖 AI Agent Menu")
    selected_mode = st.radio("작업 모드", [Modes.CSV.value, Modes.PDF.value])
    st.markdown("---")
    
    # 파일 업로더 (상태 유지를 위해 항상 렌더링)
    with st.expander(Modes.CSV.value, expanded=(selected_mode == "📊 CSV 데이터 분석")):
        uploaded_csv = st.file_uploader("CSV 파일", type=["csv"], key="csv_uploader")

    with st.expander(Modes.PDF.value, expanded=(selected_mode == "📄 PDF 문서 검색")):
        uploaded_pdf = st.file_uploader("PDF 파일", type=["pdf"], key="pdf_uploader")

# ==========================================
# [메인] 모드별 로직 실행
# ==========================================
st.header(selected_mode)
chat_container = st.container()

if selected_mode == Modes.CSV.value:
    if uploaded_csv:
        df = pd.read_csv(uploaded_csv)
        with st.expander("데이터 미리보기"):
            st.dataframe(df.head())
            
        agent = logic_csv.create_analysis_agent(df)
        
        if "csv_messages" not in st.session_state:
            st.session_state.csv_messages = []
            
        with chat_container:
            utils.display_chat_messages(st.session_state.csv_messages)

        if prompt := st.chat_input("데이터 분석 요청"):
            st.session_state.csv_messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"): st.markdown(prompt)
                
                with st.chat_message("assistant"):
                    with st.spinner("데이터 분석 중..."):
                        utils.cleanup_temp_images()

                        full_prompt = prompt + logic_csv.get_graph_instruction()
                        response = agent.invoke(full_prompt)
                        result = response["output"]
                        
                        st.markdown(result)
                        saved_images = utils.save_generated_images()
                        for img in saved_images:
                            st.image(img)

                        st.session_state.csv_messages.append({
                            "role": "assistant", 
                            "content": result, 
                            "images": saved_images
                        })
    else:
        st.info("👈 CSV 파일을 업로드해주세요.")

if selected_mode == Modes.PDF.value:
    if uploaded_pdf:
        with st.spinner("문서 분석 중..."):
            vectorstore = logic_rag.get_vectorstore(uploaded_pdf)
            rag_chain = logic_rag.get_rag_chain(vectorstore)
            
        if "pdf_messages" not in st.session_state:
            st.session_state.pdf_messages = []

        with chat_container:
            utils.display_chat_messages(st.session_state.pdf_messages)

        if prompt := st.chat_input("문서 내용 질문"):
            st.session_state.pdf_messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"): st.markdown(prompt)
                
                with st.chat_message("assistant"):
                    with st.spinner("문서 검색 중..."):
                        response = rag_chain.invoke(prompt)
                        st.markdown(response)
                        st.session_state.pdf_messages.append({
                            "role": "assistant", 
                            "content": response
                        })
    else:
        st.info("👈 PDF 파일을 업로드해주세요.")
