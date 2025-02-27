## ✅ NCP 서버에 SSH 접속 성공 (Ubuntu 22.04, root 로그인 완료)

### 1. SSH 키 파일을 사용하여 NCP 서버에 접속 시도
```sh
ssh -i ~/.ssh/RSA_PRIVATE_KEY root@XXX.XXX.XX.254
```
- `-i` 옵션을 사용하여 개인 키(`.pem`) 파일을 지정
- `root@<서버 IP>` 형식으로 NCP 서버의 퍼블릭 IP(`110.165.17.254`) 입력

---

### 2. 초기 접속 시 보안 경고 발생
```vbnet
The authenticity of host 'XXX.XXX.XX.254' can't be established.
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```
- 서버의 호스트 키가 처음으로 등록될 때 나타나는 메시지
- `yes` 입력 후 엔터

---

### 3. SSH 키 파일 권한 문제 발생
```python
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@         WARNING: UNPROTECTED PRIVATE KEY FILE!          @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
Permissions 0644 for '/Users/khb43/.ssh/RSA_PRIVATE_KEY' are too open.
```
- SSH 키 파일의 권한이 너무 개방적(0644), 보안 정책상 접속 차단됨
- 키 파일 권한을 조정해야 SSH 접속 가능

---

### 4. SSH 키 파일 권한 수정
```sh
chmod 600 ~/.ssh/pairing-server-authorization.pem
```
- `chmod 600` 명령어를 실행하여 소유자만 읽고 쓸 수 있도록 권한 변경
- `ls -l` 명령어로 변경된 파일 권한 확인:
```sh
-rw------- 1 khb43 staff 1675  2 28 02:27 /Users/khb43/.ssh/RSA_PRIVATE_KEY
```
- 정상적으로 `-rw------- (600)` 권한이 적용됨

---

### 5. SSH 접속 재시도 및 성공
```sh
ssh -i ~/.ssh/RSA_PRIVATE_KEY root@XXX.XXX.XX.254
```
- 이번에는 비밀번호 입력 없이 정상적으로 접속됨

---

### 6. NCP 서버 접속 성공 메시지 출력
```css
Welcome to Ubuntu 22.04.5 LTS (GNU/Linux 5.15.0-94-generic x86_64)
```
- 운영 체제: Ubuntu 22.04.5 LTS
- 호스트 네임: Naver Cloud Platform Server
- 프롬프트가 나타나면 `root` 계정으로 정상 로그인 완료

```sh
root@XXXXXXXXXXX756:~#
```

---

## 📌 최종 정리
✅ SSH 키 파일 권한 문제 해결 (`chmod 600` 적용)  
✅ SSH 재시도 후 정상 접속 (`ssh -i <키파일> root@<서버 IP>`)  
✅ NCP 서버(Ubuntu 22.04)에 `root` 계정으로 로그인 성공 🚀

