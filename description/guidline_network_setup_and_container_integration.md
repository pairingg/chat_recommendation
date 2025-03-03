# 네트워크 구성 및 컨테이너 연동 정리

## 1. 네트워크 구성 변경 및 이유

### 원래 상황

- 사용자 정의 네트워크 **"chat-recommendation-network"** 생성 후,
  - `mongo-container` (MongoDB 컨테이너)
  - `chat-recommendation` (대화추천 서버 컨테이너)
- 두 컨테이너가 동일 네트워크에서 내부 IP 또는 컨테이너명으로 통신 가능하도록 설정됨.

### 네트워크 변경 이유

- `chat-recommendation` 서버가 **MongoDB와 MySQL** 모두에 접근해야 하는 요구 발생
- 여러 네트워크에 컨테이너를 나누어 연결하면 다음과 같은 문제 발생:
  - `chat-recommendation` 컨테이너가 여러 네트워크에 동시에 연결되어야 함
  - 네트워크 간 cross-communication이 복잡해질 가능성 존재
- 관리 및 통신 단순화를 위해 기존에 같은 네트워크에서 관리한 컨테이너(MongoDB,  chat-recommendation)를 기존에 존재했던 MySQL 컨테이너가 포함된 하나의 네트워크(“mysql-network”)로 통합
- 기존 `mongo-container` 및 `chat-recommendation` 컨테이너를 **"chat-recommendation-network" 대신 "mysql-network"에 연결**
- `mysql-container`는 "mysql-network"에 이미 포함되어 있는 상황

---

## 2. 컨테이너 연동 과정 (명령어 포함)

### 2.1. 네트워크 재구성

#### 네트워크 삭제 및 재생성

- 기존 "chat-recommendation-network" 삭제 후, chat-recommendation-network에 있던 컨테이너를 "mysql-network"에 연결

**네트워크 확인 명령어:**

```sh
docker network ls
```

#### 컨테이너 연결 (재연결)

```sh
docker network connect mysql-network chat-recommendation 
docker network connect mysql-network mongo-container
```

- `chat-recommendation` 컨테이너가 이미 "mysql-network"에 연결된 경우, 오류 메시지 (`endpoint ... already exists`)가 발생하지만 정상적인 상태로 간주
- `mysql-container` 역시 "mysql-network"에 연결 필요

### 2.2. 결과 확인

**연결된 컨테이너 목록 확인:**

```sh
docker network inspect mysql-network
```

**예시 출력:**

```json
"Containers": {
  "abc123...": {
     "Name": "mongo-container",
     "IPv4Address": "172.~~~~~~/16"
  },
  "def456...": {
     "Name": "mysql-container",
     "IPv4Address": "172.~~~~~~/16"
  },
  "ghi789...": {
     "Name": "chat-recommendation",
     "IPv4Address": "172.~~~~~~/16"
  }
}
```

---

## 3. 컨테이너 내부에서 접속 테스트 및 네트워크 테스트

### 3.1. `chat-recommendation` 컨테이너 내부에서 네트워크 테스트

#### MongoDB 연결 테스트

**기능(대화 추천) 컨테이너 내부 접속:**

```sh
docker exec -it chat-recommendation bash
```

**네트워크 연결 확인 (ping):**

```sh
ping -c 3 mongo-container
```

**MongoDB 접속 테스트:**

```sh
mongosh "mongodb://admin:<PASSWORD>@mongo-container:27017"
```

- `show dbs` 명령어 실행하여 데이터베이스 목록 확인 가능

#### MySQL 연결 테스트

**MongoDB 클라이언트 설치 과정처럼 MySQL도 클라이언트 설치:** 

```sh
apt update && apt install -y default-mysql-client
```

**네트워크 연결 확인 (ping):**

```sh
ping -c 3 mysql-container
```

**MySQL 접속 테스트:**

```sh
mysql -h mysql-container -u root -p
```

- 프롬프트에서 비밀번호 입력 후 `SHOW DATABASES;` 실행하여 데이터베이스 목록 확인 가능
- 테스트 시 root로 접속해 접속 테스트를 진행했지만, 실제 서비스할 때는 `chat-recommendation` 컨테이너에서 MySQL 컨테이너 접속 시 사용할 유저(보안을 고려해 DB에 대한 적절한 권한을 부여한 chat-recommendation)를 만들어 이용

```sh
mysql -h mysql-container -u chat-recommendation -p
```

---

## 4. 최종 정리

### 4.1. 네트워크 구성

- 기존 \*\*"chat-recommendation-network" 대신 "mysql-network"\*\*에 모든 컨테이너 통합
- 애플리케이션에서 각 DB 서버를 컨테이너명으로 접근 가능 (`mongo-container`, `mysql-container`)

### 4.2. 컨테이너 연동 상태

- `mongo-container`, `mysql-container`, `chat-recommendation` 모두 **"mysql-network"에 연결됨**

### 4.3. 접속 테스트

- **하나의 네트워크 내에서 MongoDB와 MySQL에 정상적으로 접근 가능**

