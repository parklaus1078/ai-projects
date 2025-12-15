# app.py
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# 모듈 임포트 (우리가 만든 파일들)
import utils
import logic_rag
import logic_csv

# 1. 초기 설정
load_dotenv()
st.set_page_config(page_title="AI Multi-Modal Agent", layout="wide")
utils.init_environment()

# ==========================================
# [사이드바] 메뉴 및 파일 업로드
# ==========================================
with st.sidebar:
    st.title("🤖 AI Agent Menu")
    selected_mode = st.radio("작업 모드", ["📊 CSV 데이터 분석", "📄 PDF 문서 검색"])
    st.markdown("---")
    
    # 파일 업로더 (상태 유지를 위해 항상 렌더링)
    with st.expander("📊 CSV 파일 업로드", expanded=(selected_mode == "📊 CSV 데이터 분석")):
        uploaded_csv = st.file_uploader("CSV 파일", type=["csv"], key="csv_uploader")

    with st.expander("📄 PDF 파일 업로드", expanded=(selected_mode == "📄 PDF 문서 검색")):
        uploaded_pdf = st.file_uploader("PDF 파일", type=["pdf"], key="pdf_uploader")

# ==========================================
# [메인] 모드별 로직 실행
# ==========================================
st.header(selected_mode)
chat_container = st.container() # 대화 기록이 표시될 영역

if selected_mode == "📊 CSV 데이터 분석":
    if uploaded_csv:
        # 1. 데이터 로드 및 에이전트 생성
        df = pd.read_csv(uploaded_csv)
        with st.expander("데이터 미리보기"):
            st.dataframe(df.head())
            
        agent = logic_csv.create_analysis_agent(df)
        
        # 2. 세션 초기화 및 출력
        if "csv_messages" not in st.session_state:
            st.session_state.csv_messages = []
            
        with chat_container:
            utils.display_chat_messages(st.session_state.csv_messages)

        # 3. 입력 처리
        if prompt := st.chat_input("데이터 분석 요청"):
            st.session_state.csv_messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"): st.markdown(prompt)
                
                with st.chat_message("assistant"):
                    with st.spinner("데이터 분석 중..."):
                        utils.cleanup_temp_images() # 기존 그래프 청소
                        
                        # 에이전트 실행 (지침 추가)
                        full_prompt = prompt + logic_csv.get_graph_instruction()
                        response = agent.invoke(full_prompt)
                        result = response["output"]
                        
                        # 결과 및 이미지 저장
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

else: # PDF 모드
    if uploaded_pdf:
        # 1. 벡터 DB 및 체인 생성 (캐싱 활용)
        with st.spinner("문서 분석 중..."):
            vectorstore = logic_rag.get_vectorstore(uploaded_pdf)
            rag_chain = logic_rag.get_rag_chain(vectorstore)
            
        # 2. 세션 초기화 및 출력
        if "pdf_messages" not in st.session_state:
            st.session_state.pdf_messages = []
            
        with chat_container:
            utils.display_chat_messages(st.session_state.pdf_messages)
            
        # 3. 입력 처리
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