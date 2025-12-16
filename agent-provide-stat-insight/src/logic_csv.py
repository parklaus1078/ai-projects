from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from constants.common_constants import GPT_MODEL

def create_analysis_agent(df):
    """데이터프레임을 받아 Pandas Agent를 반환"""
    llm = ChatOpenAI(model=GPT_MODEL, temperature=0)
    
    agent = create_pandas_dataframe_agent(
        llm, 
        df, 
        agent_type="openai-tools", 
        verbose=True,
        allow_dangerous_code=True
    )
    return agent

def get_graph_instruction():
    """그래프 생성 시 지켜야 할 시스템 프롬프트 반환"""
    return (
        "\n\n[지침] "
        "1. 그래프를 그릴 때는 반드시 'plot_1.png' 같은 이름으로 파일로 저장하세요. "
        "2. plt.show()는 절대 사용하지 마세요. "
        "3. 한글 폰트가 없으므로 라벨과 제목은 반드시 영어로 작성하세요."
    )
