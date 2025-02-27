# NCP CLI 다운로드 및 설치 가이드 (For Mac)

## 1️⃣ CLI 다운로드 및 설치
### ✅ CLI 파일 다운로드 및 압축 해제(본인은 데스크탑에 다운 및 압축 해제)
```sh
cd ~/Desktop
curl -O https://cli.ncloud-docs.com/downloads/ncloud-cli-latest-mac.zip
unzip ncloud-cli-latest-mac.zip
cd CLI_1.1.23_20241121/cli_linux
```
- CLI 최신 버전을 공식 사이트에서 다운로드
- 압축을 해제하고 실행 디렉토리로 이동

## 2️⃣ 실행 권한 부여 및 환경 설정
### ✅ ncloud 실행 권한 부여
```sh
chmod +x ~/Desktop/CLI_1.1.23_20241121/cli_linux/ncloud
```
- `ncloud` 실행 파일에 실행 권한 추가

### ✅ `/usr/local/bin/`에 CLI 복사 (전역 실행 가능하게 설정)
```sh
sudo cp ~/Desktop/CLI_1.1.23_20241121/cli_linux/ncloud /usr/local/bin/ncloud
sudo chmod +x /usr/local/bin/ncloud
```
- CLI를 시스템의 전역 경로에 복사하여 어디서든 실행 가능하게 설정

## 3️⃣ Java 환경 설정 (M1/M2 Mac 호환성 문제 해결)
### ✅ 현재 시스템에 설치된 Java 버전 확인
```sh
/usr/libexec/java_home
```
#### 🔹 결과 예시:
```sh
/Library/Java/JavaVirtualMachines/jdk-22.jdk/Contents/Home
```
➡️ 본인은 Java 22가 설치되어 있음.

### ✅ ncloud 실행 스크립트에서 Java 경로 수정
```sh
vim ~/Desktop/CLI_1.1.23_20241121/cli_linux/ncloud
```
#### 🔹 기존 내용 (잘못된 경로)
```sh
#!/bin/bash
./jre8/bin/java -jar ./lib/ncloud-api-cli-1.1.23-SNAPSHOT-jar-with-dependencies.jar "$@"
```
#### 🔹 수정 후 (vim 모드에서 i 눌러 insert 모드로 내용 교체 후 :wq 통해 저장하여 시스템 Java 사용)
```sh
#!/bin/bash
/Library/Java/JavaVirtualMachines/jdk-22.jdk/Contents/Home/bin/java -jar ./lib/ncloud-api-cli-1.1.23-SNAPSHOT-jar-with-dependencies.jar "$@"
```

### ✅ ncloud 실행 가능하도록 다시 권한 설정
```sh
chmod +x ~/Desktop/CLI_1.1.23_20241121/cli_linux/ncloud
```

## 4️⃣ CLI 실행 확인
### ✅ CLI가 정상적으로 동작하는지 확인
```sh
cd ~/Desktop/CLI_1.1.23_20241121/cli_linux
./ncloud --version
```
#### 🔹 결과 예시:
```sh
pub/ncloud-cli/1.1.23 Java/22.0.2
CLI_1.1.23
```
➡️ CLI가 정상적으로 실행됨.

## 5️⃣ API 인증 설정 (NCP 계정 연동)
### ✅ `ncloud configure` 명령어 실행
```sh
ncloud configure
```
#### 🔹 입력한 값 예시:
```sh
Ncloud Access Key ID []: 복사 붙여넣기
Ncloud Secret Access Key []: 복사 붙여넣기
Ncloud API URL (default:https://ncloud.apigw.ntruss.com) []: 그냥 엔터
```
➡️ NCP 계정과 CLI 연동 완료.

## 6️⃣ 서버 목록 조회 (연결 확인)
### ✅ 현재 계정의 서버 리스트 확인
```sh
ncloud vserver getServerInstanceList
```
#### 🔹 결과 예시 (서버 2대 확인)
```json
{
  "getServerInstanceListResponse": {
    "totalRows": 2,
    "serverInstanceList": [
      {
        "serverInstanceNo": "103196756",
        "serverName": "pairing-server-msa",
        "publicIp": "110.165.17.254",
        "serverInstanceStatusName": "running"
      },
      {
        "serverInstanceNo": "103111665",
        "serverName": "pairing-server",
        "publicIp": "223.130.150.111",
        "serverInstanceStatusName": "running"
      }
    ]
  }
}
```
➡️ 서버 2개가 정상적으로 실행되고 있음.

## ✅ 최종 정리:
1️⃣ CLI 다운로드 및 압축 해제 (`curl -O` → `unzip`)
2️⃣ CLI 실행 권한 부여 (`chmod +x ncloud`)
3️⃣ 시스템 전역에서 실행 가능하도록 설정 (`sudo cp ncloud /usr/local/bin/`)
4️⃣ Java 버전 확인 및 `ncloud` 실행 스크립트 수정 (`vim ncloud`)
5️⃣ CLI 실행 테스트 (`ncloud --version`)
6️⃣ API 인증키 등록 (`ncloud configure`) 
7️⃣ 서버 목록 조회 (`ncloud vserver getServerInstanceList`)