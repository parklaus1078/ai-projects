import os
import glob
import shutil
import uuid
import time
import streamlit as st

IMAGE_DIR = "saved_images"

def init_environment():
    """환경 초기화 및 오래된 파일 청소"""
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)
    
    cleanup_old_images(retention_seconds=3600)

def cleanup_old_images(retention_seconds=3600):
    """
    Garbage Collector:
    생성된 지 retention_seconds(기본 1시간)가 지난 이미지를 삭제합니다.
    """
    current_time = time.time()
    
    for file_path in glob.glob(os.path.join(IMAGE_DIR, "*.png")):
        try:
            file_mod_time = os.path.getmtime(file_path)
            
            if current_time - file_mod_time > retention_seconds:
                os.remove(file_path)
                print(f"[GC] Deleted old image: {file_path}")
        except Exception as e:
            print(f"[GC] Error deleting {file_path}: {e}")

def save_generated_images():
    """생성된 plot_*.png 파일을 saved_images 폴더로 이동(이름 변경) 및 저장"""
    saved_paths = []
    for img_file in sorted(glob.glob("plot_*.png")):
        unique_filename = f"{IMAGE_DIR}/plot_{uuid.uuid4()}.png"
        shutil.move(img_file, unique_filename)
        saved_paths.append(unique_filename)
    return saved_paths

def cleanup_temp_images():
    """임시 생성된 plot_*.png 삭제 (이동 실패 등 잔여물 처리)"""
    for old_file in glob.glob("plot_*.png"):
        try:
            os.remove(old_file)
        except:
            pass

def display_chat_messages(messages):
    """채팅 메시지 출력 (이미지 경로 유효성 체크 추가)"""
    for message in messages:
        with st.chat_message(message["role"]):
            if "content" in message:
                st.markdown(message["content"])
            if "images" in message:
                for img_path in message["images"]:
                    if os.path.exists(img_path):
                        st.image(img_path)
                    else:
                        st.caption("⚠️ (이미지 유효 기간이 만료되어 삭제되었습니다)")