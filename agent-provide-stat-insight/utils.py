# utils.py
import os
import glob
import shutil
import uuid
import streamlit as st

def init_environment():
    """환경 초기화: 폴더 생성 및 페이지 설정"""
    if not os.path.exists("saved_images"):
        os.makedirs("saved_images")
    
    # 캐시 디렉토리 등 청소 (선택사항)
    # for f in glob.glob("plot_*.png"): os.remove(f)

def cleanup_temp_images():
    """임시 그래프 파일(plot_*.png) 삭제"""
    for old_file in glob.glob("plot_*.png"):
        try:
            os.remove(old_file)
        except:
            pass

def save_generated_images():
    """생성된 plot_*.png 파일을 saved_images 폴더로 이동하고 경로 반환"""
    saved_paths = []
    for img_file in sorted(glob.glob("plot_*.png")):
        unique_filename = f"saved_images/plot_{uuid.uuid4()}.png"
        shutil.move(img_file, unique_filename)
        saved_paths.append(unique_filename)
    return saved_paths

def display_chat_messages(messages):
    """채팅 메시지(텍스트 + 이미지) 출력"""
    for message in messages:
        with st.chat_message(message["role"]):
            if "content" in message:
                st.markdown(message["content"])
            if "images" in message:
                for img_path in message["images"]:
                    st.image(img_path)