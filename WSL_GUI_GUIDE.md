# WSL에서 Excel Macro Automation 실행 가이드

## Windows 11 (WSL2 + WSLg)

Windows 11에서는 WSLg가 기본 지원되므로 추가 설정 없이 GUI 앱을 실행할 수 있습니다.

### 1. 필요한 라이브러리 설치
```bash
# WSL 터미널에서 실행
sudo apt update
sudo apt install -y python3-pyqt5 \
    libxcb-xinerama0 libxcb-icccm4 libxcb-image0 \
    libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 \
    libxcb-xfixes0 libxcb-shape0 libgl1-mesa-glx
```

### 2. 애플리케이션 실행
```bash
cd /home/nosky/macro
python3 test_gui.py
```

## Windows 10 (WSL2 + X Server)

Windows 10에서는 X Server를 별도로 설치해야 합니다.

### 1. X Server 설치
- **VcXsrv** 다운로드: https://sourceforge.net/projects/vcxsrv/
- 또는 **X410** (Microsoft Store에서 구매)

### 2. X Server 설정 및 실행
1. VcXsrv 실행 (XLaunch)
2. 설정:
   - Display number: 0
   - "Disable access control" 체크
   - "Native opengl" 체크 해제

### 3. WSL 환경 변수 설정
```bash
# .bashrc 또는 .zshrc에 추가
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0
export LIBGL_ALWAYS_INDIRECT=1
```

### 4. 애플리케이션 실행
```bash
source ~/.bashrc  # 환경변수 적용
cd /home/nosky/macro
python3 test_gui.py
```

## 문제 해결

### Qt platform plugin "xcb" 오류
```bash
# 추가 라이브러리 설치
sudo apt install -y qt5-default libqt5gui5 libqt5core5a libqt5widgets5
```

### OpenGL 관련 오류
```bash
export LIBGL_ALWAYS_SOFTWARE=1
```

### 한글 폰트 문제
```bash
sudo apt install -y fonts-nanum fonts-noto-cjk
```

## 현재 구현 상태

### ✅ 구현 완료
1. **Excel 통합** (T-002)
   - 파일 드래그 앤 드롭
   - 시트 선택 및 미리보기
   - 열 매핑 UI

2. **매크로 에디터** (T-003)
   - 드래그 앤 드롭 단계 편집
   - 시각적 단계 표시
   - 변수 치환 지원

3. **실행 엔진** (T-004)
   - 멀티스레드 실행
   - 핫키 지원
   - 진행률 표시

4. **이미지 인식** (T-005)
   - OpenCV 기반 매칭
   - ROI 선택 UI
   - DPI 스케일링 지원

### ❌ 미구현
- OCR 텍스트 인식 (T-006)
- 조건문 로직 (T-007)
- 매크로 저장/불러오기 (T-008)
- 고급 로깅 (T-009)

## 실제 애플리케이션 실행

import 문제를 해결한 후:
```bash
python3 main.py
```

또는 import 문제를 우회하여 실행:
1. 모든 상대 import를 절대 import로 변경
2. 또는 PYTHONPATH 설정:
   ```bash
   export PYTHONPATH=/home/nosky/macro/src:$PYTHONPATH
   cd /home/nosky/macro
   python3 -m main
   ```