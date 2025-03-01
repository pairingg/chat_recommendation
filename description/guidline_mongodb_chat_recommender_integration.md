# MongoDB 컨테이너 배포 및 대화추천 컨테이너와의 연동 및 문제 해결 과정

## 1. 목표 및 초기 진행 순서

### 목표

대화추천 서버(chat‑recommendation 컨테이너)가 MongoDB 컨테이너에 저장된 데이터를 안전하게 조회할 수 있도록,
두 컨테이너가 동일한 네트워크에 속하고 올바른 MongoDB 클라이언트(mongosh)를 통해 접속하는 환경을 구축하는 것이 목표임.

### 초기 진행 순서 및 상황

#### MongoDB 컨테이너 실행

초기 시도: 최신 mongo:latest 이미지를 사용하여 mongo-container를 실행함.

```sh
docker run -d \
  --name mongo-container \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=<팀 노션에 정리되어 있는 사항대로> \
  -e MONGO_INITDB_ROOT_PASSWORD=<팀 노션에 정리되어 있는 사항대로> \
  mongo:latest
```

문제 인식: 최신 이미지의 패키지 구조나 설치 방식 변경으로 인한 호환성 문제가 우려되어,
안정적인 환경을 위해 이후 mongo:6.0 버전 사용으로 전환하기로 결정함.

#### 네트워크 구성

두 컨테이너(mongo-container와 대화추천 서버 chat-recommendation)가 서로 통신할 수 있도록,
사용자 정의 네트워크 chat-recommendation-network를 생성하고 두 컨테이너를 해당 네트워크에 연결함.

```sh
docker network create chat-recommendation-network
docker network connect chat-recommendation-network mongo-container
docker network connect chat-recommendation-network chat-recommendation
```

네트워크 검사 결과:
mongo-container 내부 IP: 172.19.0.2
chat-recommendation 내부 IP: 172.19.0.3
ping 테스트를 통해 두 컨테이너 간 통신이 정상적으로 이루어짐.

#### chat‑recommendation 컨테이너에서 mongosh 설치 시도 (apt 방식)

시도:
chat‑recommendation 컨테이너 내부에서 `apt install -y mongodb-org-shell`을 통해 mongosh 설치를 시도함.

문제:
`/usr/local/bin`에 mongosh 심볼릭 링크는 생성되었으나, 실제 실행 파일이 배포되지 않아 "command not found" 오류가 발생(즉, dangling symlink 상태 발생)함.

분석:
최소화된 베이스 이미지나 apt 방식 설치 시 패키지 구조 변경으로 인해 mongosh가 올바르게 설치되지 않은 것으로 판단됨.

#### MongoDB 이미지 문제 인식

최신 mongo:latest 이미지 사용 시 호환성 문제가 발생할 가능성이 있었음.
안정적인 환경을 위해 mongo:6.0 버전 사용으로 다운그레이드하기로 결정함.

---

## 2. 진행 프로세스

### (1) MongoDB 컨테이너 실행

최초 실행:
최신 mongo:latest 이미지를 사용하여 실행하려 했으나,
이후 호환성 문제를 인식하여 다운그레이드 결정을 내림.

### (2) 네트워크 구성

사용자 정의 네트워크 chat-recommendation-network를 생성하고, 두 컨테이너를 연결함.

```sh
docker network create chat-recommendation-network
docker network connect chat-recommendation-network mongo-container
docker network connect chat-recommendation-network chat-recommendation
docker network inspect chat-recommendation-network
```

결과:
두 컨테이너 간 통신 확인(ping 테스트 성공)함.

### (3) chat‑recommendation 컨테이너에서 mongosh 설치 시도 (apt 방식) 실패

시도:

```sh
apt install -y mongodb-org-shell
```

문제:
mongosh 심볼릭 링크만 생성되고, 실제 실행 파일이 배포되지 않아 "command not found" 오류가 발생함.
이 문제는 컨테이너의 베이스 이미지 및 최신 패키지의 구조 변경 때문일 가능성이 큼.

### (4) MongoDB 이미지 다운그레이드

목표: 최신 이미지에서 발생하는 호환성 문제를 피하고 안정적인 환경 구축을 위해 mongo:6.0 버전 사용임.

```sh
docker stop mongo-container
docker rm mongo-container
docker rmi mongo:latest
docker run -d \
  --name mongo-container \
  --network chat-recommendation-network \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=<팀 노션에 정리되어 있는 사항대로> \
  -e MONGO_INITDB_ROOT_PASSWORD=<팀 노션에 정리되어 있는 사항대로> \
  mongo:6.0
```

검증:

```sh
docker exec -it mongo-container mongod --version
```

결과: MongoDB 버전 6.0.20 정상 실행 확인함.

### (5) chat‑recommendation 컨테이너에서 MongoDB 클라이언트(mongosh) 설치 문제 해결 (공식 바이너리 수동 설치)

문제:
apt 방식으로 설치한 mongosh가 동작하지 않아 "command not found" 오류가 발생함.

해결:

기존 잘못된 심볼릭 링크 삭제

```sh
rm /usr/local/bin/mongosh
```

MongoDB 공식 사이트에서 최신 mongosh 바이너리(tar.gz 파일)를 다운로드 및 압축 해제

```sh
wget https://downloads.mongodb.com/compass/mongosh-1.7.0-linux-x64.tgz
tar -xzvf mongosh-1.7.0-linux-x64.tgz
```

mongosh 실행 파일을 /usr/local/bin에 복사 및 실행 권한 부여

```sh
cp mongosh-1.7.0-linux-x64/bin/mongosh /usr/local/bin/mongosh
chmod +x /usr/local/bin/mongosh
```

검증:

```sh
which mongosh
mongosh "mongodb://admin:pring987@mongo-container:27017"
```

결과: mongosh가 정상 인식되어 MongoDB 6.0.20에 성공적으로 접속함.

---

## 3. 문제 해결의 핵심

### 몽고셸 문제 해결:

초기 apt 방식 설치로 발생한 심볼릭 링크 문제를, MongoDB 공식 사이트에서 최신 mongosh 바이너리를 직접 다운로드해 수동 설치함으로써 해결함.

### MongoDB 이미지 다운그레이드:

최신 mongo:latest 이미지의 호환성 문제를 피하기 위해, 안정적인 mongo:6.0 버전으로 컨테이너를 재실행함.

### 네트워크 구성:

두 컨테이너를 동일한 사용자 정의 네트워크(chat-recommendation-network)에 연결하여,
컨테이너 이름이나 내부 IP를 통해 안정적인 통신 환경을 마련함.

---

## 정리

초기에는 apt를 통한 mongodb-org-shell 설치 방식으로 mongosh를 사용하려 했으나,
심볼릭 링크가 dangling 상태가 되어 "command not found" 오류가 발생함.

문제 해결을 위해 다음과 같이 진행함:

- **네트워크 구성:**
  두 컨테이너를 사용자 정의 네트워크(chat-recommendation-network)에 연결하여 안정적인 통신 환경을 구축함.

- **MongoDB 이미지 다운그레이드:**
  최신 이미지의 호환성 문제를 피하기 위해, mongo:6.0 버전으로 컨테이너를 재실행하여 MongoDB 6.0.20을 사용함.

- **mongosh 문제 해결:**
  apt 방식으로 설치한 mongosh의 문제를, MongoDB 공식 사이트에서 최신 mongosh 바이너리를 다운로드해 수동으로 설치함으로써 해결하여,
  mongosh가 정상적으로 인식되어 MongoDB에 접속할 수 있게 함.
