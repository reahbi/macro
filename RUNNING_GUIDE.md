# Excel Macro Automation 실행 가이드

## 🚀 빠른 시작

### 1. 가상환경 활성화
```bash
source venv/bin/activate
```

### 2. 애플리케이션 실행
```bash
python run_simple.py
```

또는

```bash
./start_gui.sh
```

## ⚙️ 실행 환경 확인

### WSL2 GUI 지원 확인
```bash
# DISPLAY 환경 변수 확인
echo $DISPLAY
# 출력: :0 또는 :0.0

# X11 소켓 확인
ls /tmp/.X11-unix/
# 출력: X0
```

### Python 환경 확인
```bash
# 가상환경 활성화 상태 확인
which python
# 출력: /home/nosky/macro/venv/bin/python

# PyQt5 설치 확인
python -c "import PyQt5; print('PyQt5 OK')"
```

## 🔧 문제 해결

### GUI가 표시되지 않을 때

1. **WSLg 업데이트**
   ```bash
   wsl --update
   ```

2. **X11 관련 패키지 설치**
   ```bash
   sudo apt-get update
   sudo apt-get install x11-apps
   
   # 테스트
   xclock  # 시계가 표시되면 정상
   ```

3. **한글 폰트 설치** (이미 설치됨)
   ```bash
   sudo apt-get install fonts-nanum fonts-noto-cjk
   ```

### "tkinter" 경고 메시지
- PyAutoGUI의 의존성 때문에 나타나는 메시지로 무시해도 됩니다
- 우리 앱은 PyQt5를 사용하므로 tkinter가 필요하지 않습니다

### Import 오류 발생 시
```bash
# run_main.py 대신 run_simple.py 사용
python run_simple.py
```

## 📁 실행 파일 설명

- `run_main.py`: 자동 import 패치 기능이 있는 메인 실행 파일
- `run_simple.py`: 간단한 실행 파일 (import 문제 시 사용)
- `start_gui.sh`: 셸 스크립트 실행 파일

## 💡 팁

1. **첫 실행 시**
   - EasyOCR 모델을 다운로드하므로 시간이 걸릴 수 있습니다
   - 인터넷 연결이 필요합니다

2. **성능 향상**
   - ROI(관심 영역)를 지정하여 OCR/이미지 검색 속도 향상
   - 불필요한 단계는 비활성화

3. **디버깅**
   - 로그 파일 확인: `logs/` 디렉토리
   - 설정 파일: `~/.excel_macro_automation/settings.yaml`

## 🎯 다음 단계

1. Excel 파일 불러오기 (Excel 탭)
2. 매크로 단계 추가 (Editor 탭)
3. 매크로 실행 (Run 탭)

자세한 사용법은 `CURRENT_STATUS.md` 참조