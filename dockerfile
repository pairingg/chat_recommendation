# 베이스 이미지 선택 (파이썬 버전 맞춰 Python 3.10-slim으로 택)
FROM python:3.10-slim

# 환경변수 설정: 파이썬 버퍼링 없이 출력하도록

# ENV PYTHONUNBUFFERED=1 설정은 파이썬 애플리케이션의 표준 출력(예: print() 함수, 로깅 등)이 버퍼링 없이 즉시 출력되도록 만들어줌.
# 기본적으로 파이썬은 표준 출력을 버퍼링하는데, 이는 프로그램이 출력하는 데이터를 모아서 한 번에 처리함으로써 성능을 높일 수 있지만, 로그나 디버그 메시지가 즉시 보이지 않는 단점이 생기게 됨.
# 이러면 Docker 컨테이너에서 로그를 모니터링할 때, 버퍼링 때문에 출력이 지연되면 실시간 로그 확인이 어려워짐. (즉, 컨테이너가 실행 중인 상태에서도 로그가 바로 반영되지 않고, 어느 정도 쌓인 후에 한 번에 출력)
# 따라서 ENV PYTHONUNBUFFERED=1을 설정하면 파이썬이 출력을 즉시 플러시(Flush)하게 되어, 로그가 바로 나타나도록 함. 
# 이로 인해 Docker 로그나 콘솔에서 실시간으로 애플리케이션 상태를 확인할 수 있어 이 설정은 Docker 환경에서 애플리케이션 로그가 실시간으로 전달되어 문제 발생 시 빠르게 대응할 수 있도록 돕는 중요한 설정.
ENV PYTHONUNBUFFERED=1

# 이름 가독성 있게 명명 후 및 작업 디렉토리 설정
WORKDIR /pAIring_chatting_recommender_docker

# 시스템 의존성 설치 (+ konlpy의 경우 Java가 필요할 수 있으므로)
RUN apt-get update && apt-get install -y \
    openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 파일을 먼저 복사하고 의존성 설치 (캐시 활용)
COPY requirements.txt .

# pip 최신화 및 의존성 설치 (캐시 최적화, 불필요한 캐시 파일 제거)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 프로젝트 전체 파일 복사
COPY . .

# 포트 논의 필요: 일단 임의 설정
EXPOSE 8086

# uvicorn을 사용해 FastAPI 앱 실행
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8086", "--reload"]

# Docker 캐시를 최대한 활용하기 위한 방법 모색 필요
    
    # 1. 변경이 적은 파일을 먼저 복사

    # 현재와 같이 requirements.txt만 먼저 복사하고 의존성을 설치하는 방식은 캐시 활용에 좋은 접근.
    # 코드 전체를 복사하기 전에, 변경이 적은 설정 파일이나 의존성 목록을 먼저 복사하면 이후 변경된 소스 코드 때문에 캐시가 무효화되는 것을 막을 수 있음.
    
    # 2. .dockerignore 파일 작성

    # 불필요한 파일(예: .git, pycache, 로컬 설정 파일 등)을 제외시켜서, 소스 복사 단계에서 변경이 발생하지 않도록 함.
    # 이렇게 하면 불필요한 파일 변경으로 인한 캐시 무효화를 줄일 수 있음.
    
    # 3. RUN 명령어 최적화

    # 여러 패키지를 설치하는 RUN 명령어는 하나의 RUN 명령어로 묶어서 실행하면 중간 레이어가 생성되는 것을 줄여 캐시 효율을 높일 수 있음.
    # 예를 들어, apt-get update와 apt-get install을 하나의 RUN 명령어에 넣는 것이 좋음.

    # 4. 멀티 스테이지 빌드 고려

    # 필요에 따라 빌드 스테이지와 실제 실행 스테이지를 분리해, 최종 이미지에 불필요한 빌드 도구나 캐시 데이터를 포함하지 않도록 할 수 있음.