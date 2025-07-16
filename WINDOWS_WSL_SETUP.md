# Windows + VSCode + WSL2 환경에서 GUI 실행하기

## 🖥️ Windows에서 X Server 설치 및 실행

### 방법 1: VcXsrv 사용 (권장)

1. **VcXsrv 다운로드 및 설치**
   - https://sourceforge.net/projects/vcxsrv/
   - 설치 후 "XLaunch" 실행

2. **VcXsrv 설정**
   - Display settings: Multiple windows
   - Client startup: Start no client
   - Extra settings: 
     - ✅ Clipboard
     - ✅ Primary Selection
     - ✅ Native opengl
     - ✅ **Disable access control** (중요!)

3. **Windows 방화벽 허용**
   - VcXsrv가 방화벽 허용 요청하면 "허용" 클릭

### 방법 2: MobaXterm 사용

1. **MobaXterm 다운로드**
   - https://mobaxterm.mobatek.net/
   - Home Edition (무료) 사용

2. **X server 자동 시작**
   - MobaXterm 실행하면 자동으로 X server 시작됨

## 🐧 WSL2 설정

### 1. DISPLAY 환경 변수 설정

```bash
# ~/.bashrc 또는 ~/.zshrc에 추가
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0
export LIBGL_ALWAYS_INDIRECT=1
```

또는 임시로 설정:

```bash
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0
```

### 2. 현재 설정 확인

```bash
echo $DISPLAY
# 출력 예: 172.x.x.x:0.0
```

## 🚀 애플리케이션 실행

### 1. X Server 확인
```bash
# Windows에서 VcXsrv 또는 MobaXterm이 실행 중인지 확인
# 시스템 트레이에 X 아이콘이 있어야 함
```

### 2. 테스트
```bash
# X11 앱 테스트
sudo apt-get install x11-apps
xeyes  # 눈이 따라다니는 창이 나타나면 성공!
```

### 3. Excel Macro Automation 실행
```bash
source venv/bin/activate
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0
python run_simple.py
```

## 🔧 문제 해결

### "cannot connect to X server" 오류

1. **Windows IP 확인**
   ```bash
   cat /etc/resolv.conf | grep nameserver
   # nameserver 뒤의 IP 주소 확인
   ```

2. **수동으로 DISPLAY 설정**
   ```bash
   export DISPLAY=<Windows-IP>:0.0
   # 예: export DISPLAY=172.31.32.1:0.0
   ```

3. **VcXsrv 재시작**
   - Windows에서 VcXsrv 종료 후 다시 시작
   - "Disable access control" 옵션 확인

### "Authorization required" 오류

```bash
# X 인증 비활성화 (보안상 로컬에서만 사용)
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0
xhost +
```

### WSLg 사용 (Windows 11)

Windows 11 + WSL2 최신 버전에서는 WSLg가 기본 지원됩니다:

```bash
# WSL 업데이트
wsl --update

# WSL 재시작
wsl --shutdown
# Windows에서 다시 WSL 실행

# DISPLAY 확인
echo $DISPLAY
# :0 또는 :0.0이면 WSLg 사용 중
```

## 📝 실행 스크립트

`run_windows_wsl.sh` 생성:

```bash
#!/bin/bash
# Windows + WSL2 환경 실행 스크립트

echo "Windows + WSL2 환경에서 Excel Macro Automation 실행"
echo "=================================================="

# DISPLAY 설정
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0
echo "DISPLAY 설정: $DISPLAY"

# 가상환경 활성화
source venv/bin/activate

# Python 실행
python run_simple.py
```

## ✅ 체크리스트

- [ ] Windows에 X Server (VcXsrv 또는 MobaXterm) 설치
- [ ] X Server 실행 중 (시스템 트레이 확인)
- [ ] VcXsrv에서 "Disable access control" 체크
- [ ] WSL에서 DISPLAY 환경변수 설정
- [ ] xeyes 또는 xclock으로 테스트 성공

모든 항목을 확인했다면 GUI가 정상적으로 표시됩니다!