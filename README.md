# AI Insight Agent

## 1. 프로젝트 목적 (Project Purpose)
본 프로젝트는 **PDF 문서**와 **CSV 데이터**라는 서로 다른 성격의 데이터를 하나의 인터페이스에서 분석하기 위해 구축된 **Multi-Modal AI Agent**입니다.

**의문:** 비정형/정형 데이터 형태의 파일들을 업로드하고 Insight를 도출해내는 기능은 LLM solution들도 다 있는데 왜 만들었나요?
**답변:**
  * 확장성과 커스터마이징 가능성을 시험해보기 위해서입니다. 단순히 LLM API를 사용하여 만드는 'LLM이 도입된 어플리케이션'이 아니라 하나의 모듈을 만들어보는 데에 집중하고, 각 형태의 데이터 별로 어떤 방식으로 다뤄야 LLM이 사용자에게 유용한 답변을 반환하는지, 어떤 방식으로 커스터마이징하는 것이 가장 심플하면서도 사용자에게 도움이 되는지 등의 고민을 해보고 프로토타이핑하는 데에 의의가 있습니다.

Streamlit을 기반으로 웹 인터페이스를 구축하였으며, 비정형 데이터(PDF)는 **RAG(Retrieval-Augmented Generation)** 방식으로, 정형 데이터(CSV)는 **Python Code Execution(Pandas Agent)** 방식으로 이원화하여 처리합니다.

## 2. Dependencies
### Environment
* `python`@_v3.11.9_
* `direnv`@_v2.35.0_

### Packages
* `streamlit`@_v1.52.1_
* `langchain`@_v1.1.3_
* `langchain-openai`@_v1.1.3_
* `langchain-community`@_v0.4.1_
* `langchain-experimental`@_v0.4.1_
* `pandas`@_v2.3.3_
* `matplotlib`@_v3.10.8_
* `seaborn`@_v0.13.2_
* `pypdf`@_v6.4.2_
* `faiss-cpu`@_v1.13.1_
* `openai`@_v2.11.0_
* `tiktoken`@_v0.12.0_
* `tabulate`@_v0.9.0_

## 3. 프로젝트에서 고민한 점들(Technical Exploration)
### 3.1. 데이터 성격에 따른 분석 엔진의 이원화
**Cause:** PDF와 같은 텍스트 위주의 데이터는 의미론적 검색(Semantic Search)이 중요하지만, CSV와 같은 수치 데이터는 벡터 검색 시 행(Row) 간의 연산이나 전체 통계 도출이 불가능한 한계가 있었습니다.

**Engineering Decision:** PDF 분석에는 RAG(FAISS) 방식을, CSV 분석에는 LLM이 직접 코드를 작성하고 실행하는 Pandas Agent 방식을 채택하여 엔진을 분리했습니다.

**Effect:** PDF에서는 질문에 관련된 맥락을 정확히 찾아내고, CSV에서는 평균, 합계 등 복잡한 수치 연산과 그래프 시각화를 100% 정확하게 수행하는 환경을 구축했습니다.

### 3.2. 답변의 결정론적(Deterministic) 제어와 수치 신뢰성
**Cause:** LLM의 확률적 특성으로 인해 동일한 질문에도 답변이 달라지거나, 특히 수학적 연산에서 환각(Hallucination)이 발생하여 데이터 분석 도구로서의 신뢰성이 저하되는 문제가 있었습니다.

**Engineering Decision:** 모든 모델 호출에 temperature=0을 설정하여 무작위성을 최소화하고, 수치 연산은 LLM의 추론이 아닌 파이썬 인터프리터가 수행하도록 설계했습니다.

**Effect:** 분석 결과의 일관성을 확보했으며, 연산 실수가 발생할 수 없는 구조를 만들어 비즈니스 리포팅에 적합한 데이터 신뢰성을 확보했습니다.

## 4. 프로젝트 결과
### CSV insight 도출
![csv 업로드 전](./readme_pics/csv%201.jpg)
![csv 업로드 후 텍스트](./readme_pics/csv%202.jpg)
![csv 업로드 후 플롯](./readme_pics/csv%203.jpg)

### PDF insight 도출
![pdf 업로드 전](./readme_pics/pdf%201.jpg)
![pdf 업로드 후 설명](./readme_pics/pdf%202.jpg)
![pdf 내용 증거](./readme_pics/pdf%203.jpg)
![pdf 내용 요약](./readme_pics/pdf%204.jpg)
![pdf 요약 증거](./readme_pics/pdf%205.jpg)

## 5. 로컬 구동 방법
1. python 3.11.9 버전으로 가상환경을 설치하고 가상환경을 구동시킵니다.

    예시) `pyenv`를 사용할 때,
    ```bash
    $ pyenv install 3.11.9
    $ pyenv virtualenv 3.11.9 venv
    $ pyenv local venv
    ```

* (additional) direnv가 설치되어 있지 않을 시, `direnv` 패키지를 설치합니다. 설치 방법은 [여기](https://direnv.net/)에 기술되어 있습니다.

2. 터미널 위치(Terminal Path)를 루트 디렉토리로 두고 dependency를 설치합니다.
    ```bash
    $ pip install -r requirements.txt
    ```

3.  루트 디렉토리에 `.envrc` 파일을 생성하고 Open AI API key를 정의합니다.
    ```.envrc
    # .envrc
    export OPENAI_API_KEY=<API KEY>
    ```

4. 환경 변수를 시스템에 등록합니다.
    ```bash
    $ direnv allow
    ```

5. 터미널 위치(Terminal Path)를 루트 디렉토리로 두고 streamlit을 활용하여 app을 구동시킵니다.
    ```bash
    $ streamlit run src.app.py
    ```

## 6. 프로젝트 한계
* MVP: 상용 수준의 어플리케이션을 개발한 것이 아닌, 핵심 로직의 작동과 AI agent의 모듈화 및 확장성 검증에 중점을 두었습니다. 

* 리소스 최적화: 로컬 메모리 기반의 벡터 스토어(FAISS)를 사용하므로, 하드웨어의 RAM 용량에 따라 소화할 수 있는 문서의 용량이 상이할 수 있습니다. 예를 들어, [streamlit.app](https://ai-projects-jkxltk4xclygeyjm9rcn6r.streamlit.app/)에 배포한 어플리케이션에선 1 MB 이상의 파일은 소화할 수 없지만, 로컬에선 2 MB 이상의 파일도 소화할 수 있습니다.
  * 참고: streamlit 에 배포한 어플리케이션은 인가된 이메일로만 접근 가능하기 떄문에 제가 초대를 드려야 합니다. 사용해보시고 싶으신 경우, 이메일을 알려주시면 초대를 해드리겠습니다.