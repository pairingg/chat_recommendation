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

# 시스템 의존성 설치 

# konlpy의 경우 Java가 필요
RUN apt-get update && apt-get install -y \
    openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/*
# wget 설치 (MongoDB 클라이언트 설치 전에 wget이 필요)
RUN apt-get update && apt-get install -y wget
# 컨테이너 내부에서 mongodb 클라이언트 사용하기 위해 필요
RUN wget https://downloads.mongodb.com/compass/mongosh-1.7.0-linux-x64.tgz \
    && tar -xzvf mongosh-1.7.0-linux-x64.tgz \
    && cp mongosh-1.7.0-linux-x64/bin/mongosh /usr/local/bin/mongosh \
    && chmod +x /usr/local/bin/mongosh \
    && rm -rf mongosh-1.7.0-linux-x64.tgz mongosh-1.7.0-linux-x64
# 컨테이너 내부에서 mysql 클라이언트 사용하기 위해 필요
RUN apt-get update \
    && apt-get install -y default-mysql-client \
    && rm -rf /var/lib/apt/lists/*
    
# requirements.txt 파일을 먼저 복사하고 의존성 설치 (캐시 활용)
COPY requirements.txt .

# pip 최신화 및 의존성 설치 (캐시 최적화, 불필요한 캐시 파일 제거)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 프로젝트 전체 파일 복사
COPY . .

# 논의된 포트
EXPOSE 8086

# uvicorn을 사용해 FastAPI 앱 실행
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8086", "--reload"]