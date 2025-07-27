
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: paintEvent called
DEBUG: ROI selection complete with region: (13, 136, 112, 128), type: <class 'tuple'>
DEBUG: _on_region_selected called with region: (13, 136, 112, 128), type: <class 'tuple'>
DEBUG: set region successful with formatted region: (13, 136, 112, 128)
DEBUG: region_label updated
DEBUG: About to restore dialog visibility
DEBUG: Dialog visibility restored
DEBUG: selectionComplete signal emitted with region: (13, 136, 112, 128)
DEBUG: ROI close() called
DEBUG: start_selection() called
DEBUG: _update_step_from_dialog called, current region: (13, 136, 112, 128)
DEBUG: Updated step.region to: (13, 136, 112, 128) (type: <class 'tuple'>)
DEBUG: Step updated - region: (13, 136, 112, 128), search_text: ${환자명}
INFO: State changed: idle -> running
[2025-07-27 20:18:25,076] [    INFO] engine.py:106 - State changed: idle -> running
INFO: Hotkey listener started (Start: Key.f5, Pause: Key.f9, Stop: Key.esc)
[2025-07-27 20:18:25,108] [    INFO] hotkey_listener.py:93 - Hotkey listener started (Start: Key.f5, Pause: Key.f9, Stop: Key.esc)
INFO: Execution log started: C:\Users\nosky\.excel_macro_automation\execution_logs\execution_새 매크로_20250727_201825.csv
[2025-07-27 20:18:25,110] [    INFO] engine.py:162 - Execution log started: C:\Users\nosky\.excel_macro_automation\execution_logs\execution_새 매크로_20250727_201825.csv
INFO: Starting execution for 5 rows
[2025-07-27 20:18:25,111] [    INFO] engine.py:172 - Starting execution for 5 rows
INFO: Initialized progress calculator: mode=excel, total_rows=5, total_steps=4
[2025-07-27 20:18:25,112] [    INFO] progress_calculator.py:86 - Initialized progress calculator: mode=excel, total_rows=5, total_steps=4
INFO: Starting Excel workflow execution
[2025-07-27 20:18:25,112] [    INFO] engine.py:212 - Starting Excel workflow execution
INFO: Starting Excel workflow execution - Status column: '매크로_상태'
[2025-07-27 20:18:25,113] [    INFO] engine.py:645 - Starting Excel workflow execution - Status column: '매크로_상태'
INFO: Processing 5 rows with repeat mode: incomplete_only
[2025-07-27 20:18:25,114] [    INFO] engine.py:694 - Processing 5 rows with repeat mode: incomplete_only
INFO:
==================================================
[2025-07-27 20:18:25,115] [    INFO] executor.py:90 -
==================================================
INFO: 단계 실행 시작: 텍스트 검색 (ocr_text)
[2025-07-27 20:18:25,116] [    INFO] executor.py:91 - 단계 실행 시작: 텍스트 검색 (ocr_text)
INFO: ==================================================
[2025-07-27 20:18:25,117] [    INFO] executor.py:92 - ==================================================
INFO: ======== 텍스트 검색 시작 ========
[2025-07-27 20:18:25,419] [    INFO] executor.py:640 - ======== 텍스트 검색 시작 ========
INFO: 검색 텍스트: '홍길동'
[2025-07-27 20:18:25,420] [    INFO] executor.py:641 - 검색 텍스트: '홍길동'
INFO: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:25,420] [    INFO] executor.py:642 - 검색 영역: (13, 136, 112, 128)
INFO: 검색 옵션: exact_match=False, confidence=0.4
[2025-07-27 20:18:25,421] [    INFO] executor.py:643 - 검색 옵션: exact_match=False, confidence=0.4
INFO: 클릭 옵션: click_on_found=True, offset=(0, 0), double_click=True
[2025-07-27 20:18:25,421] [    INFO] executor.py:644 - 클릭 옵션: click_on_found=True, offset=(0, 0), double_click=True
INFO: 추출된 텍스트 항목: 2개
[2025-07-27 20:18:26,613] [    INFO] text_extractor_paddle.py:465 - 추출된 텍스트 항목: 2개
INFO: === OCR 텍스트 추출 결과 ===
[2025-07-27 20:18:26,614] [    INFO] text_extractor_paddle.py:468 - === OCR 텍스트 추출 결과 ===
INFO: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:26,615] [    INFO] text_extractor_paddle.py:469 - 검색 영역: (13, 136, 112, 128)
INFO: 추출된 텍스트 개수: 2개
[2025-07-27 20:18:26,615] [    INFO] text_extractor_paddle.py:470 - 추출된 텍스트 개수: 2개
INFO: 추출된 텍스트 목록:
[2025-07-27 20:18:26,616] [    INFO] text_extractor_paddle.py:473 - 추출된 텍스트 목록:
INFO:   [0] 'K1' 위치: (28, 153), 영역: (13, 141, 30, 25), 신뢰도: 1.00
[2025-07-27 20:18:26,616] [    INFO] text_extractor_paddle.py:475 -   [0] 'K1' 위치: (28, 153), 영역: (13, 141, 30, 25), 신뢰도: 1.00
INFO:   [1] 'Y' 위치: (20, 234), 영역: (14, 227, 13, 15), 신뢰도: 0.99
[2025-07-27 20:18:26,617] [    INFO] text_extractor_paddle.py:475 -   [1] 'Y' 위치: (20, 234), 영역: (14, 227, 13, 15), 신뢰도: 0.99
INFO: extract_text_from_region 실행 시간: 1.197초
[2025-07-27 20:18:26,618] [    INFO] text_extractor_paddle.py:32 - extract_text_from_region 실행 시간: 1.197초
INFO: === 텍스트 검색 시작 ===
[2025-07-27 20:18:26,618] [    INFO] text_extractor_paddle.py:549 - === 텍스트 검색 시작 ===
INFO: 찾을 텍스트: '홍길동'
[2025-07-27 20:18:26,618] [    INFO] text_extractor_paddle.py:550 - 찾을 텍스트: '홍길동'
INFO: 정규화된 텍스트: '홍길동'
[2025-07-27 20:18:26,619] [    INFO] text_extractor_paddle.py:551 - 정규화된 텍스트: '홍길동'
INFO: 검색 모드: 부분 일치
[2025-07-27 20:18:26,620] [    INFO] text_extractor_paddle.py:552 - 검색 모드: 부분 일치
WARNING: === 텍스트를 찾을 수 없음 ===
[2025-07-27 20:18:26,620] [ WARNING] text_extractor_paddle.py:600 - === 텍스트를 찾을 수 없음 ===
WARNING: 찾으려던 텍스트: '홍길동'
[2025-07-27 20:18:26,621] [ WARNING] text_extractor_paddle.py:601 - 찾으려던 텍스트: '홍길동'
WARNING: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:26,621] [ WARNING] text_extractor_paddle.py:602 - 검색 영역: (13, 136, 112, 128)
WARNING: OCR로 추출된 텍스트 개수: 2개
[2025-07-27 20:18:26,622] [ WARNING] text_extractor_paddle.py:603 - OCR로 추출된 텍스트 개수: 2개
WARNING: 가능한 원인:
[2025-07-27 20:18:26,622] [ WARNING] text_extractor_paddle.py:605 - 가능한 원인:
WARNING: 1. 텍스트가 검색 영역 밖에 있음
[2025-07-27 20:18:26,623] [ WARNING] text_extractor_paddle.py:606 - 1. 텍스트가 검색 영역 밖에 있음
WARNING: 2. OCR 인식 오류
[2025-07-27 20:18:26,625] [ WARNING] text_extractor_paddle.py:607 - 2. OCR 인식 오류
WARNING: 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
[2025-07-27 20:18:26,625] [ WARNING] text_extractor_paddle.py:608 - 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
INFO: find_text 실행 시간: 1.207초
[2025-07-27 20:18:26,628] [    INFO] text_extractor_paddle.py:32 - find_text 실행 시간: 1.207초
INFO: 텍스트를 찾지 못했습니다. 1.0초 후 재시도합니다... (시도 1/3)
[2025-07-27 20:18:26,628] [    INFO] executor.py:252 - 텍스트를 찾지 못했습니다. 1.0초 후 재시도합니다... (시도 1/3)
INFO: 추출된 텍스트 항목: 2개
[2025-07-27 20:18:28,715] [    INFO] text_extractor_paddle.py:465 - 추출된 텍스트 항목: 2개
INFO: === OCR 텍스트 추출 결과 ===
[2025-07-27 20:18:28,717] [    INFO] text_extractor_paddle.py:468 - === OCR 텍스트 추출 결과 ===
INFO: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:28,717] [    INFO] text_extractor_paddle.py:469 - 검색 영역: (13, 136, 112, 128)
INFO: 추출된 텍스트 개수: 2개
[2025-07-27 20:18:28,718] [    INFO] text_extractor_paddle.py:470 - 추출된 텍스트 개수: 2개
INFO: 추출된 텍스트 목록:
[2025-07-27 20:18:28,718] [    INFO] text_extractor_paddle.py:473 - 추출된 텍스트 목록:
INFO:   [0] 'K1' 위치: (28, 153), 영역: (13, 141, 30, 25), 신뢰도: 1.00
[2025-07-27 20:18:28,719] [    INFO] text_extractor_paddle.py:475 -   [0] 'K1' 위치: (28, 153), 영역: (13, 141, 30, 25), 신뢰도: 1.00
INFO:   [1] 'Y' 위치: (20, 234), 영역: (14, 227, 13, 15), 신뢰도: 0.99
[2025-07-27 20:18:28,719] [    INFO] text_extractor_paddle.py:475 -   [1] 'Y' 위치: (20, 234), 영역: (14, 227, 13, 15), 신뢰도: 0.99
INFO: extract_text_from_region 실행 시간: 1.090초
[2025-07-27 20:18:28,720] [    INFO] text_extractor_paddle.py:32 - extract_text_from_region 실행 시간: 1.090초
INFO: === 텍스트 검색 시작 ===
[2025-07-27 20:18:28,720] [    INFO] text_extractor_paddle.py:549 - === 텍스트 검색 시작 ===
INFO: 찾을 텍스트: '홍길동'
[2025-07-27 20:18:28,721] [    INFO] text_extractor_paddle.py:550 - 찾을 텍스트: '홍길동'
INFO: 정규화된 텍스트: '홍길동'
[2025-07-27 20:18:28,721] [    INFO] text_extractor_paddle.py:551 - 정규화된 텍스트: '홍길동'
INFO: 검색 모드: 부분 일치
[2025-07-27 20:18:28,722] [    INFO] text_extractor_paddle.py:552 - 검색 모드: 부분 일치
WARNING: === 텍스트를 찾을 수 없음 ===
[2025-07-27 20:18:28,722] [ WARNING] text_extractor_paddle.py:600 - === 텍스트를 찾을 수 없음 ===
WARNING: 찾으려던 텍스트: '홍길동'
[2025-07-27 20:18:28,723] [ WARNING] text_extractor_paddle.py:601 - 찾으려던 텍스트: '홍길동'
WARNING: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:28,723] [ WARNING] text_extractor_paddle.py:602 - 검색 영역: (13, 136, 112, 128)
WARNING: OCR로 추출된 텍스트 개수: 2개
[2025-07-27 20:18:28,724] [ WARNING] text_extractor_paddle.py:603 - OCR로 추출된 텍스트 개수: 2개
WARNING: 가능한 원인:
[2025-07-27 20:18:28,724] [ WARNING] text_extractor_paddle.py:605 - 가능한 원인:
WARNING: 1. 텍스트가 검색 영역 밖에 있음
[2025-07-27 20:18:28,725] [ WARNING] text_extractor_paddle.py:606 - 1. 텍스트가 검색 영역 밖에 있음
WARNING: 2. OCR 인식 오류
[2025-07-27 20:18:28,725] [ WARNING] text_extractor_paddle.py:607 - 2. OCR 인식 오류
WARNING: 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
[2025-07-27 20:18:28,726] [ WARNING] text_extractor_paddle.py:608 - 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
INFO: find_text 실행 시간: 1.096초
[2025-07-27 20:18:28,726] [    INFO] text_extractor_paddle.py:32 - find_text 실행 시간: 1.096초
INFO: 텍스트를 찾지 못했습니다. 1.0초 후 재시도합니다... (시도 2/3)
[2025-07-27 20:18:28,727] [    INFO] executor.py:252 - 텍스트를 찾지 못했습니다. 1.0초 후 재시도합니다... (시도 2/3)
INFO: 추출된 텍스트 항목: 2개
[2025-07-27 20:18:30,781] [    INFO] text_extractor_paddle.py:465 - 추출된 텍스트 항목: 2개
INFO: === OCR 텍스트 추출 결과 ===
[2025-07-27 20:18:30,783] [    INFO] text_extractor_paddle.py:468 - === OCR 텍스트 추출 결과 ===
INFO: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:30,783] [    INFO] text_extractor_paddle.py:469 - 검색 영역: (13, 136, 112, 128)
INFO: 추출된 텍스트 개수: 2개
[2025-07-27 20:18:30,784] [    INFO] text_extractor_paddle.py:470 - 추출된 텍스트 개수: 2개
INFO: 추출된 텍스트 목록:
[2025-07-27 20:18:30,784] [    INFO] text_extractor_paddle.py:473 - 추출된 텍스트 목록:
INFO:   [0] 'K1' 위치: (28, 153), 영역: (13, 141, 30, 25), 신뢰도: 1.00
[2025-07-27 20:18:30,785] [    INFO] text_extractor_paddle.py:475 -   [0] 'K1' 위치: (28, 153), 영역: (13, 141, 30, 25), 신뢰도: 1.00
INFO:   [1] 'Y' 위치: (20, 234), 영역: (14, 227, 13, 15), 신뢰도: 0.99
[2025-07-27 20:18:30,785] [    INFO] text_extractor_paddle.py:475 -   [1] 'Y' 위치: (20, 234), 영역: (14, 227, 13, 15), 신뢰도: 0.99
INFO: extract_text_from_region 실행 시간: 1.058초
[2025-07-27 20:18:30,786] [    INFO] text_extractor_paddle.py:32 - extract_text_from_region 실행 시간: 1.058초
INFO: === 텍스트 검색 시작 ===
[2025-07-27 20:18:30,786] [    INFO] text_extractor_paddle.py:549 - === 텍스트 검색 시작 ===
INFO: 찾을 텍스트: '홍길동'
[2025-07-27 20:18:30,787] [    INFO] text_extractor_paddle.py:550 - 찾을 텍스트: '홍길동'
INFO: 정규화된 텍스트: '홍길동'
[2025-07-27 20:18:30,787] [    INFO] text_extractor_paddle.py:551 - 정규화된 텍스트: '홍길동'
INFO: 검색 모드: 부분 일치
[2025-07-27 20:18:30,788] [    INFO] text_extractor_paddle.py:552 - 검색 모드: 부분 일치
WARNING: === 텍스트를 찾을 수 없음 ===
[2025-07-27 20:18:30,788] [ WARNING] text_extractor_paddle.py:600 - === 텍스트를 찾을 수 없음 ===
WARNING: 찾으려던 텍스트: '홍길동'
[2025-07-27 20:18:30,789] [ WARNING] text_extractor_paddle.py:601 - 찾으려던 텍스트: '홍길동'
WARNING: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:30,789] [ WARNING] text_extractor_paddle.py:602 - 검색 영역: (13, 136, 112, 128)
WARNING: OCR로 추출된 텍스트 개수: 2개
[2025-07-27 20:18:30,790] [ WARNING] text_extractor_paddle.py:603 - OCR로 추출된 텍스트 개수: 2개
WARNING: 가능한 원인:
[2025-07-27 20:18:30,790] [ WARNING] text_extractor_paddle.py:605 - 가능한 원인:
WARNING: 1. 텍스트가 검색 영역 밖에 있음
[2025-07-27 20:18:30,791] [ WARNING] text_extractor_paddle.py:606 - 1. 텍스트가 검색 영역 밖에 있음
WARNING: 2. OCR 인식 오류
[2025-07-27 20:18:30,791] [ WARNING] text_extractor_paddle.py:607 - 2. OCR 인식 오류
WARNING: 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
[2025-07-27 20:18:30,792] [ WARNING] text_extractor_paddle.py:608 - 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
INFO: find_text 실행 시간: 1.064초
[2025-07-27 20:18:30,792] [    INFO] text_extractor_paddle.py:32 - find_text 실행 시간: 1.064초
WARNING: 텍스트 검색이 5.37초 걸렸습니다. 검색 영역을 좁히는 것을 고려하세요.
[2025-07-27 20:18:30,793] [ WARNING] executor.py:258 - 텍스트 검색이 5.37초 걸렸습니다. 검색 영역을 좁히는 것을 고려하세요.
WARNING: ======== 텍스트 검색 실패 ========
[2025-07-27 20:18:30,793] [ WARNING] executor.py:673 - ======== 텍스트 검색 실패 ========
WARNING: 찾을 수 없는 텍스트: '홍길동'
[2025-07-27 20:18:30,794] [ WARNING] executor.py:674 - 찾을 수 없는 텍스트: '홍길동'
INFO: 단계 실행 완료: 텍스트 검색
[2025-07-27 20:18:30,796] [    INFO] executor.py:96 - 단계 실행 완료: 텍스트 검색
INFO:
==================================================
[2025-07-27 20:18:30,796] [    INFO] executor.py:90 -
==================================================
INFO: 단계 실행 시작: 텍스트 입력 (keyboard_type)
[2025-07-27 20:18:30,797] [    INFO] executor.py:91 - 단계 실행 시작: 텍스트 입력 (keyboard_type)
INFO: ==================================================
[2025-07-27 20:18:30,797] [    INFO] executor.py:92 - ==================================================
INFO: ======== 키보드 입력 시작 ========
[2025-07-27 20:18:30,899] [    INFO] executor.py:441 - ======== 키보드 입력 시작 ========
INFO: 현재 마우스 위치 (입력 위치): (1249, 509)
[2025-07-27 20:18:30,900] [    INFO] executor.py:442 - 현재 마우스 위치 (입력 위치): (1249, 509)
INFO: 원본 텍스트: '${환자명}${작업번호}'
[2025-07-27 20:18:30,900] [    INFO] executor.py:443 - 원본 텍스트: '${환자명}${작업번호}'
INFO: 변수 치환 사용: True
[2025-07-27 20:18:30,900] [    INFO] executor.py:444 - 변수 치환 사용: True
INFO: 사용 가능한 변수: ['작업번호', '환자명', '병력번호', '검사항목', '검사일자', '매크로_상태', '매크로_실행시간', '매크로_오류메시지']
[2025-07-27 20:18:30,901] [    INFO] executor.py:445 - 사용 가능한 변수: ['작업번호', '환자명', '병력번호', '검사항목', '검사일자', '매크로_상태', '매크로_실행시간', '매크로_오류메시지']
INFO: 치환된 텍스트: '홍길동1'
[2025-07-27 20:18:30,901] [    INFO] executor.py:450 - 치환된 텍스트: '홍길동1'
INFO: 입력 시작 - 텍스트: '홍길동1', 간격: 0.0초
[2025-07-27 20:18:30,901] [    INFO] executor.py:452 - 입력 시작 - 텍스트: '홍길동1', 간격: 0.0초
INFO: 입력 완료 - 마우스 위치: (1249, 509)
[2025-07-27 20:18:31,003] [    INFO] executor.py:457 - 입력 완료 - 마우스 위치: (1249, 509)
INFO: ======== 키보드 입력 완료 ========
[2025-07-27 20:18:31,003] [    INFO] executor.py:458 - ======== 키보드 입력 완료 ========
INFO: 단계 실행 완료: 텍스트 입력
[2025-07-27 20:18:31,004] [    INFO] executor.py:96 - 단계 실행 완료: 텍스트 입력
INFO: Row 0 completed successfully - updating status to COMPLETED
[2025-07-27 20:18:31,004] [    INFO] engine.py:760 - Row 0 completed successfully - updating status to COMPLETED
INFO: ExcelManager.update_row_status called - row: 0, status: '완료', save_immediately: True
[2025-07-27 20:18:31,005] [    INFO] excel_manager.py:342 - ExcelManager.update_row_status called - row: 0, status: '완 료', save_immediately: True
INFO: Saving file immediately after status update for row 0
[2025-07-27 20:18:31,005] [    INFO] excel_manager.py:352 - Saving file immediately after status update for row 0
INFO: File modification time before save: Sun Jul 27 20:16:40 2025
[2025-07-27 20:18:31,012] [    INFO] excel_manager.py:265 - File modification time before save: Sun Jul 27 20:16:40 2025
INFO: Status column '매크로_상태' values before save: {'미완료': 4, '완료': 1}
[2025-07-27 20:18:31,013] [    INFO] excel_manager.py:270 - Status column '매크로_상태' values before save: {'미완료': 4, '완료': 1}
INFO: File modification time after save: Sun Jul 27 20:18:31 2025
[2025-07-27 20:18:31,021] [    INFO] excel_manager.py:292 - File modification time after save: Sun Jul 27 20:18:31 2025
INFO: Status column '매크로_상태' values after save: {'미완료': 4, '완료': 1}
[2025-07-27 20:18:31,021] [    INFO] excel_manager.py:300 - Status column '매크로_상태' values after save: {'미완료': 4, '완료': 1}
INFO: Saved Excel file successfully: C:\mag\macro\demo_data.xlsx
[2025-07-27 20:18:31,022] [    INFO] excel_manager.py:302 - Saved Excel file successfully: C:\mag\macro\demo_data.xlsx
INFO:
==================================================
[2025-07-27 20:18:31,023] [    INFO] executor.py:90 -
==================================================
INFO: 단계 실행 시작: 텍스트 검색 (ocr_text)
[2025-07-27 20:18:31,024] [    INFO] executor.py:91 - 단계 실행 시작: 텍스트 검색 (ocr_text)
INFO: ==================================================
[2025-07-27 20:18:31,024] [    INFO] executor.py:92 - ==================================================
INFO: ======== 텍스트 검색 시작 ========
[2025-07-27 20:18:31,326] [    INFO] executor.py:640 - ======== 텍스트 검색 시작 ========
INFO: 검색 텍스트: '김철수'
[2025-07-27 20:18:31,332] [    INFO] executor.py:641 - 검색 텍스트: '김철수'
INFO: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:31,335] [    INFO] executor.py:642 - 검색 영역: (13, 136, 112, 128)
INFO: 검색 옵션: exact_match=False, confidence=0.4
[2025-07-27 20:18:31,338] [    INFO] executor.py:643 - 검색 옵션: exact_match=False, confidence=0.4
INFO: 클릭 옵션: click_on_found=True, offset=(0, 0), double_click=True
[2025-07-27 20:18:31,340] [    INFO] executor.py:644 - 클릭 옵션: click_on_found=True, offset=(0, 0), double_click=True
INFO: 추출된 텍스트 항목: 1개
[2025-07-27 20:18:32,453] [    INFO] text_extractor_paddle.py:465 - 추출된 텍스트 항목: 1개
INFO: === OCR 텍스트 추출 결과 ===
[2025-07-27 20:18:32,454] [    INFO] text_extractor_paddle.py:468 - === OCR 텍스트 추출 결과 ===
INFO: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:32,455] [    INFO] text_extractor_paddle.py:469 - 검색 영역: (13, 136, 112, 128)
INFO: 추출된 텍스트 개수: 1개
[2025-07-27 20:18:32,455] [    INFO] text_extractor_paddle.py:470 - 추출된 텍스트 개수: 1개
INFO: 추출된 텍스트 목록:
[2025-07-27 20:18:32,456] [    INFO] text_extractor_paddle.py:473 - 추출된 텍스트 목록:
INFO:   [0] 'K1' 위치: (28, 153), 영역: (13, 139, 31, 28), 신뢰도: 1.00
[2025-07-27 20:18:32,456] [    INFO] text_extractor_paddle.py:475 -   [0] 'K1' 위치: (28, 153), 영역: (13, 139, 31, 28), 신뢰도: 1.00
INFO: extract_text_from_region 실행 시간: 1.116초
[2025-07-27 20:18:32,457] [    INFO] text_extractor_paddle.py:32 - extract_text_from_region 실행 시간: 1.116초
INFO: === 텍스트 검색 시작 ===
[2025-07-27 20:18:32,458] [    INFO] text_extractor_paddle.py:549 - === 텍스트 검색 시작 ===
INFO: 찾을 텍스트: '김철수'
[2025-07-27 20:18:32,458] [    INFO] text_extractor_paddle.py:550 - 찾을 텍스트: '김철수'
INFO: 정규화된 텍스트: '김철수'
[2025-07-27 20:18:32,458] [    INFO] text_extractor_paddle.py:551 - 정규화된 텍스트: '김철수'
INFO: 검색 모드: 부분 일치
[2025-07-27 20:18:32,459] [    INFO] text_extractor_paddle.py:552 - 검색 모드: 부분 일치
WARNING: === 텍스트를 찾을 수 없음 ===
[2025-07-27 20:18:32,459] [ WARNING] text_extractor_paddle.py:600 - === 텍스트를 찾을 수 없음 ===
WARNING: 찾으려던 텍스트: '김철수'
[2025-07-27 20:18:32,460] [ WARNING] text_extractor_paddle.py:601 - 찾으려던 텍스트: '김철수'
WARNING: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:32,461] [ WARNING] text_extractor_paddle.py:602 - 검색 영역: (13, 136, 112, 128)
WARNING: OCR로 추출된 텍스트 개수: 1개
[2025-07-27 20:18:32,461] [ WARNING] text_extractor_paddle.py:603 - OCR로 추출된 텍스트 개수: 1개
WARNING: 가능한 원인:
[2025-07-27 20:18:32,462] [ WARNING] text_extractor_paddle.py:605 - 가능한 원인:
WARNING: 1. 텍스트가 검색 영역 밖에 있음
[2025-07-27 20:18:32,462] [ WARNING] text_extractor_paddle.py:606 - 1. 텍스트가 검색 영역 밖에 있음
WARNING: 2. OCR 인식 오류
[2025-07-27 20:18:32,463] [ WARNING] text_extractor_paddle.py:607 - 2. OCR 인식 오류
WARNING: 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
[2025-07-27 20:18:32,463] [ WARNING] text_extractor_paddle.py:608 - 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
INFO: find_text 실행 시간: 1.123초
[2025-07-27 20:18:32,464] [    INFO] text_extractor_paddle.py:32 - find_text 실행 시간: 1.123초
INFO: 텍스트를 찾지 못했습니다. 1.0초 후 재시도합니다... (시도 1/3)
[2025-07-27 20:18:32,466] [    INFO] executor.py:252 - 텍스트를 찾지 못했습니다. 1.0초 후 재시도합니다... (시도 1/3)
INFO: 추출된 텍스트 항목: 1개
[2025-07-27 20:18:34,633] [    INFO] text_extractor_paddle.py:465 - 추출된 텍스트 항목: 1개
INFO: === OCR 텍스트 추출 결과 ===
[2025-07-27 20:18:34,636] [    INFO] text_extractor_paddle.py:468 - === OCR 텍스트 추출 결과 ===
INFO: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:34,636] [    INFO] text_extractor_paddle.py:469 - 검색 영역: (13, 136, 112, 128)
INFO: 추출된 텍스트 개수: 1개
[2025-07-27 20:18:34,637] [    INFO] text_extractor_paddle.py:470 - 추출된 텍스트 개수: 1개
INFO: 추출된 텍스트 목록:
[2025-07-27 20:18:34,638] [    INFO] text_extractor_paddle.py:473 - 추출된 텍스트 목록:
INFO:   [0] 'K1' 위치: (28, 153), 영역: (13, 139, 31, 28), 신뢰도: 1.00
[2025-07-27 20:18:34,638] [    INFO] text_extractor_paddle.py:475 -   [0] 'K1' 위치: (28, 153), 영역: (13, 139, 31, 28), 신뢰도: 1.00
INFO: extract_text_from_region 실행 시간: 1.172초
[2025-07-27 20:18:34,639] [    INFO] text_extractor_paddle.py:32 - extract_text_from_region 실행 시간: 1.172초
INFO: === 텍스트 검색 시작 ===
[2025-07-27 20:18:34,639] [    INFO] text_extractor_paddle.py:549 - === 텍스트 검색 시작 ===
INFO: 찾을 텍스트: '김철수'
[2025-07-27 20:18:34,640] [    INFO] text_extractor_paddle.py:550 - 찾을 텍스트: '김철수'
INFO: 정규화된 텍스트: '김철수'
[2025-07-27 20:18:34,640] [    INFO] text_extractor_paddle.py:551 - 정규화된 텍스트: '김철수'
INFO: 검색 모드: 부분 일치
[2025-07-27 20:18:34,641] [    INFO] text_extractor_paddle.py:552 - 검색 모드: 부분 일치
WARNING: === 텍스트를 찾을 수 없음 ===
[2025-07-27 20:18:34,641] [ WARNING] text_extractor_paddle.py:600 - === 텍스트를 찾을 수 없음 ===
WARNING: 찾으려던 텍스트: '김철수'
[2025-07-27 20:18:34,642] [ WARNING] text_extractor_paddle.py:601 - 찾으려던 텍스트: '김철수'
WARNING: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:34,642] [ WARNING] text_extractor_paddle.py:602 - 검색 영역: (13, 136, 112, 128)
WARNING: OCR로 추출된 텍스트 개수: 1개
[2025-07-27 20:18:34,643] [ WARNING] text_extractor_paddle.py:603 - OCR로 추출된 텍스트 개수: 1개
WARNING: 가능한 원인:
[2025-07-27 20:18:34,643] [ WARNING] text_extractor_paddle.py:605 - 가능한 원인:
WARNING: 1. 텍스트가 검색 영역 밖에 있음
[2025-07-27 20:18:34,644] [ WARNING] text_extractor_paddle.py:606 - 1. 텍스트가 검색 영역 밖에 있음
WARNING: 2. OCR 인식 오류
[2025-07-27 20:18:34,644] [ WARNING] text_extractor_paddle.py:607 - 2. OCR 인식 오류
WARNING: 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
[2025-07-27 20:18:34,645] [ WARNING] text_extractor_paddle.py:608 - 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
INFO: find_text 실행 시간: 1.178초
[2025-07-27 20:18:34,645] [    INFO] text_extractor_paddle.py:32 - find_text 실행 시간: 1.178초
INFO: 텍스트를 찾지 못했습니다. 1.0초 후 재시도합니다... (시도 2/3)
[2025-07-27 20:18:34,646] [    INFO] executor.py:252 - 텍스트를 찾지 못했습니다. 1.0초 후 재시도합니다... (시도 2/3)
INFO: 추출된 텍스트 항목: 1개
[2025-07-27 20:18:36,686] [    INFO] text_extractor_paddle.py:465 - 추출된 텍스트 항목: 1개
INFO: === OCR 텍스트 추출 결과 ===
[2025-07-27 20:18:36,688] [    INFO] text_extractor_paddle.py:468 - === OCR 텍스트 추출 결과 ===
INFO: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:36,688] [    INFO] text_extractor_paddle.py:469 - 검색 영역: (13, 136, 112, 128)
INFO: 추출된 텍스트 개수: 1개
[2025-07-27 20:18:36,689] [    INFO] text_extractor_paddle.py:470 - 추출된 텍스트 개수: 1개
INFO: 추출된 텍스트 목록:
[2025-07-27 20:18:36,689] [    INFO] text_extractor_paddle.py:473 - 추출된 텍스트 목록:
INFO:   [0] 'K1' 위치: (28, 153), 영역: (13, 139, 31, 28), 신뢰도: 1.00
[2025-07-27 20:18:36,690] [    INFO] text_extractor_paddle.py:475 -   [0] 'K1' 위치: (28, 153), 영역: (13, 139, 31, 28), 신뢰도: 1.00
INFO: extract_text_from_region 실행 시간: 1.042초
[2025-07-27 20:18:36,690] [    INFO] text_extractor_paddle.py:32 - extract_text_from_region 실행 시간: 1.042초
INFO: === 텍스트 검색 시작 ===
[2025-07-27 20:18:36,691] [    INFO] text_extractor_paddle.py:549 - === 텍스트 검색 시작 ===
INFO: 찾을 텍스트: '김철수'
[2025-07-27 20:18:36,691] [    INFO] text_extractor_paddle.py:550 - 찾을 텍스트: '김철수'
INFO: 정규화된 텍스트: '김철수'
[2025-07-27 20:18:36,692] [    INFO] text_extractor_paddle.py:551 - 정규화된 텍스트: '김철수'
INFO: 검색 모드: 부분 일치
[2025-07-27 20:18:36,692] [    INFO] text_extractor_paddle.py:552 - 검색 모드: 부분 일치
WARNING: === 텍스트를 찾을 수 없음 ===
[2025-07-27 20:18:36,693] [ WARNING] text_extractor_paddle.py:600 - === 텍스트를 찾을 수 없음 ===
WARNING: 찾으려던 텍스트: '김철수'
[2025-07-27 20:18:36,693] [ WARNING] text_extractor_paddle.py:601 - 찾으려던 텍스트: '김철수'
WARNING: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:36,694] [ WARNING] text_extractor_paddle.py:602 - 검색 영역: (13, 136, 112, 128)
WARNING: OCR로 추출된 텍스트 개수: 1개
[2025-07-27 20:18:36,694] [ WARNING] text_extractor_paddle.py:603 - OCR로 추출된 텍스트 개수: 1개
WARNING: 가능한 원인:
[2025-07-27 20:18:36,695] [ WARNING] text_extractor_paddle.py:605 - 가능한 원인:
WARNING: 1. 텍스트가 검색 영역 밖에 있음
[2025-07-27 20:18:36,695] [ WARNING] text_extractor_paddle.py:606 - 1. 텍스트가 검색 영역 밖에 있음
WARNING: 2. OCR 인식 오류
[2025-07-27 20:18:36,696] [ WARNING] text_extractor_paddle.py:607 - 2. OCR 인식 오류
WARNING: 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
[2025-07-27 20:18:36,696] [ WARNING] text_extractor_paddle.py:608 - 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
INFO: find_text 실행 시간: 1.049초
[2025-07-27 20:18:36,697] [    INFO] text_extractor_paddle.py:32 - find_text 실행 시간: 1.049초
WARNING: 텍스트 검색이 5.36초 걸렸습니다. 검색 영역을 좁히는 것을 고려하세요.
[2025-07-27 20:18:36,698] [ WARNING] executor.py:258 - 텍스트 검색이 5.36초 걸렸습니다. 검색 영역을 좁히는 것을 고려하세요.
WARNING: ======== 텍스트 검색 실패 ========
[2025-07-27 20:18:36,700] [ WARNING] executor.py:673 - ======== 텍스트 검색 실패 ========
WARNING: 찾을 수 없는 텍스트: '김철수'
[2025-07-27 20:18:36,700] [ WARNING] executor.py:674 - 찾을 수 없는 텍스트: '김철수'
INFO: 단계 실행 완료: 텍스트 검색
[2025-07-27 20:18:36,701] [    INFO] executor.py:96 - 단계 실행 완료: 텍스트 검색
INFO:
==================================================
[2025-07-27 20:18:36,701] [    INFO] executor.py:90 -
==================================================
INFO: 단계 실행 시작: 텍스트 입력 (keyboard_type)
[2025-07-27 20:18:36,702] [    INFO] executor.py:91 - 단계 실행 시작: 텍스트 입력 (keyboard_type)
INFO: ==================================================
[2025-07-27 20:18:36,702] [    INFO] executor.py:92 - ==================================================
INFO: ======== 키보드 입력 시작 ========
[2025-07-27 20:18:36,804] [    INFO] executor.py:441 - ======== 키보드 입력 시작 ========
INFO: 현재 마우스 위치 (입력 위치): (1249, 509)
[2025-07-27 20:18:36,804] [    INFO] executor.py:442 - 현재 마우스 위치 (입력 위치): (1249, 509)
INFO: 원본 텍스트: '${환자명}${작업번호}'
[2025-07-27 20:18:36,805] [    INFO] executor.py:443 - 원본 텍스트: '${환자명}${작업번호}'
INFO: 변수 치환 사용: True
[2025-07-27 20:18:36,805] [    INFO] executor.py:444 - 변수 치환 사용: True
INFO: 사용 가능한 변수: ['작업번호', '환자명', '병력번호', '검사항목', '검사일자', '매크로_상태', '매크로_실행시간', '매크로_오류메시지']
[2025-07-27 20:18:36,805] [    INFO] executor.py:445 - 사용 가능한 변수: ['작업번호', '환자명', '병력번호', '검사항목', '검사일자', '매크로_상태', '매크로_실행시간', '매크로_오류메시지']
INFO: 치환된 텍스트: '김철수2'
[2025-07-27 20:18:36,806] [    INFO] executor.py:450 - 치환된 텍스트: '김철수2'
INFO: 입력 시작 - 텍스트: '김철수2', 간격: 0.0초
[2025-07-27 20:18:36,806] [    INFO] executor.py:452 - 입력 시작 - 텍스트: '김철수2', 간격: 0.0초
INFO: 입력 완료 - 마우스 위치: (1249, 509)
[2025-07-27 20:18:36,908] [    INFO] executor.py:457 - 입력 완료 - 마우스 위치: (1249, 509)
INFO: ======== 키보드 입력 완료 ========
[2025-07-27 20:18:36,909] [    INFO] executor.py:458 - ======== 키보드 입력 완료 ========
INFO: 단계 실행 완료: 텍스트 입력
[2025-07-27 20:18:36,910] [    INFO] executor.py:96 - 단계 실행 완료: 텍스트 입력
INFO: Row 1 completed successfully - updating status to COMPLETED
[2025-07-27 20:18:36,911] [    INFO] engine.py:760 - Row 1 completed successfully - updating status to COMPLETED
INFO: ExcelManager.update_row_status called - row: 1, status: '완료', save_immediately: True
[2025-07-27 20:18:36,912] [    INFO] excel_manager.py:342 - ExcelManager.update_row_status called - row: 1, status: '완 료', save_immediately: True
INFO: Saving file immediately after status update for row 1
[2025-07-27 20:18:36,912] [    INFO] excel_manager.py:352 - Saving file immediately after status update for row 1
INFO: File modification time before save: Sun Jul 27 20:18:31 2025
[2025-07-27 20:18:36,922] [    INFO] excel_manager.py:265 - File modification time before save: Sun Jul 27 20:18:31 2025
INFO: Status column '매크로_상태' values before save: {'미완료': 3, '완료': 2}
[2025-07-27 20:18:36,923] [    INFO] excel_manager.py:270 - Status column '매크로_상태' values before save: {'미완료': 3, '완료': 2}
INFO: File modification time after save: Sun Jul 27 20:18:36 2025
[2025-07-27 20:18:36,943] [    INFO] excel_manager.py:292 - File modification time after save: Sun Jul 27 20:18:36 2025
INFO: Status column '매크로_상태' values after save: {'미완료': 3, '완료': 2}
[2025-07-27 20:18:36,944] [    INFO] excel_manager.py:300 - Status column '매크로_상태' values after save: {'미완료': 3, '완료': 2}
INFO: Saved Excel file successfully: C:\mag\macro\demo_data.xlsx
[2025-07-27 20:18:36,945] [    INFO] excel_manager.py:302 - Saved Excel file successfully: C:\mag\macro\demo_data.xlsx
INFO:
==================================================
[2025-07-27 20:18:36,948] [    INFO] executor.py:90 -
==================================================
INFO: 단계 실행 시작: 텍스트 검색 (ocr_text)
[2025-07-27 20:18:36,949] [    INFO] executor.py:91 - 단계 실행 시작: 텍스트 검색 (ocr_text)
INFO: ==================================================
[2025-07-27 20:18:36,949] [    INFO] executor.py:92 - ==================================================
INFO: ======== 텍스트 검색 시작 ========
[2025-07-27 20:18:37,250] [    INFO] executor.py:640 - ======== 텍스트 검색 시작 ========
INFO: 검색 텍스트: '이영희'
[2025-07-27 20:18:37,256] [    INFO] executor.py:641 - 검색 텍스트: '이영희'
INFO: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:37,259] [    INFO] executor.py:642 - 검색 영역: (13, 136, 112, 128)
INFO: 검색 옵션: exact_match=False, confidence=0.4
[2025-07-27 20:18:37,261] [    INFO] executor.py:643 - 검색 옵션: exact_match=False, confidence=0.4
INFO: 클릭 옵션: click_on_found=True, offset=(0, 0), double_click=True
[2025-07-27 20:18:37,262] [    INFO] executor.py:644 - 클릭 옵션: click_on_found=True, offset=(0, 0), double_click=True
INFO: 추출된 텍스트 항목: 1개
[2025-07-27 20:18:38,303] [    INFO] text_extractor_paddle.py:465 - 추출된 텍스트 항목: 1개
INFO: === OCR 텍스트 추출 결과 ===
[2025-07-27 20:18:38,305] [    INFO] text_extractor_paddle.py:468 - === OCR 텍스트 추출 결과 ===
INFO: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:38,305] [    INFO] text_extractor_paddle.py:469 - 검색 영역: (13, 136, 112, 128)
INFO: 추출된 텍스트 개수: 1개
[2025-07-27 20:18:38,306] [    INFO] text_extractor_paddle.py:470 - 추출된 텍스트 개수: 1개
INFO: 추출된 텍스트 목록:
[2025-07-27 20:18:38,306] [    INFO] text_extractor_paddle.py:473 - 추출된 텍스트 목록:
INFO:   [0] 'K1' 위치: (28, 153), 영역: (13, 139, 31, 28), 신뢰도: 1.00
[2025-07-27 20:18:38,307] [    INFO] text_extractor_paddle.py:475 -   [0] 'K1' 위치: (28, 153), 영역: (13, 139, 31, 28), 신뢰도: 1.00
INFO: extract_text_from_region 실행 시간: 1.045초
[2025-07-27 20:18:38,307] [    INFO] text_extractor_paddle.py:32 - extract_text_from_region 실행 시간: 1.045초
INFO: === 텍스트 검색 시작 ===
[2025-07-27 20:18:38,308] [    INFO] text_extractor_paddle.py:549 - === 텍스트 검색 시작 ===
INFO: 찾을 텍스트: '이영희'
[2025-07-27 20:18:38,308] [    INFO] text_extractor_paddle.py:550 - 찾을 텍스트: '이영희'
INFO: 정규화된 텍스트: '이영희'
[2025-07-27 20:18:38,309] [    INFO] text_extractor_paddle.py:551 - 정규화된 텍스트: '이영희'
INFO: 검색 모드: 부분 일치
[2025-07-27 20:18:38,309] [    INFO] text_extractor_paddle.py:552 - 검색 모드: 부분 일치
WARNING: === 텍스트를 찾을 수 없음 ===
[2025-07-27 20:18:38,310] [ WARNING] text_extractor_paddle.py:600 - === 텍스트를 찾을 수 없음 ===
WARNING: 찾으려던 텍스트: '이영희'
[2025-07-27 20:18:38,311] [ WARNING] text_extractor_paddle.py:601 - 찾으려던 텍스트: '이영희'
WARNING: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:38,311] [ WARNING] text_extractor_paddle.py:602 - 검색 영역: (13, 136, 112, 128)
WARNING: OCR로 추출된 텍스트 개수: 1개
[2025-07-27 20:18:38,312] [ WARNING] text_extractor_paddle.py:603 - OCR로 추출된 텍스트 개수: 1개
WARNING: 가능한 원인:
[2025-07-27 20:18:38,312] [ WARNING] text_extractor_paddle.py:605 - 가능한 원인:
WARNING: 1. 텍스트가 검색 영역 밖에 있음
[2025-07-27 20:18:38,313] [ WARNING] text_extractor_paddle.py:606 - 1. 텍스트가 검색 영역 밖에 있음
WARNING: 2. OCR 인식 오류
[2025-07-27 20:18:38,313] [ WARNING] text_extractor_paddle.py:607 - 2. OCR 인식 오류
WARNING: 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
[2025-07-27 20:18:38,314] [ WARNING] text_extractor_paddle.py:608 - 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
INFO: find_text 실행 시간: 1.053초
[2025-07-27 20:18:38,315] [    INFO] text_extractor_paddle.py:32 - find_text 실행 시간: 1.053초
INFO: 텍스트를 찾지 못했습니다. 1.0초 후 재시도합니다... (시도 1/3)
[2025-07-27 20:18:38,315] [    INFO] executor.py:252 - 텍스트를 찾지 못했습니다. 1.0초 후 재시도합니다... (시도 1/3)
INFO: 추출된 텍스트 항목: 1개
[2025-07-27 20:18:40,304] [    INFO] text_extractor_paddle.py:465 - 추출된 텍스트 항목: 1개
INFO: === OCR 텍스트 추출 결과 ===
[2025-07-27 20:18:40,306] [    INFO] text_extractor_paddle.py:468 - === OCR 텍스트 추출 결과 ===
INFO: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:40,306] [    INFO] text_extractor_paddle.py:469 - 검색 영역: (13, 136, 112, 128)
INFO: 추출된 텍스트 개수: 1개
[2025-07-27 20:18:40,307] [    INFO] text_extractor_paddle.py:470 - 추출된 텍스트 개수: 1개
INFO: 추출된 텍스트 목록:
[2025-07-27 20:18:40,307] [    INFO] text_extractor_paddle.py:473 - 추출된 텍스트 목록:
INFO:   [0] 'K1' 위치: (28, 153), 영역: (13, 139, 31, 28), 신뢰도: 1.00
[2025-07-27 20:18:40,308] [    INFO] text_extractor_paddle.py:475 -   [0] 'K1' 위치: (28, 153), 영역: (13, 139, 31, 28), 신뢰도: 1.00
INFO: extract_text_from_region 실행 시간: 0.991초
[2025-07-27 20:18:40,308] [    INFO] text_extractor_paddle.py:32 - extract_text_from_region 실행 시간: 0.991초
INFO: === 텍스트 검색 시작 ===
[2025-07-27 20:18:40,309] [    INFO] text_extractor_paddle.py:549 - === 텍스트 검색 시작 ===
INFO: 찾을 텍스트: '이영희'
[2025-07-27 20:18:40,309] [    INFO] text_extractor_paddle.py:550 - 찾을 텍스트: '이영희'
INFO: 정규화된 텍스트: '이영희'
[2025-07-27 20:18:40,310] [    INFO] text_extractor_paddle.py:551 - 정규화된 텍스트: '이영희'
INFO: 검색 모드: 부분 일치
[2025-07-27 20:18:40,310] [    INFO] text_extractor_paddle.py:552 - 검색 모드: 부분 일치
WARNING: === 텍스트를 찾을 수 없음 ===
[2025-07-27 20:18:40,311] [ WARNING] text_extractor_paddle.py:600 - === 텍스트를 찾을 수 없음 ===
WARNING: 찾으려던 텍스트: '이영희'
[2025-07-27 20:18:40,311] [ WARNING] text_extractor_paddle.py:601 - 찾으려던 텍스트: '이영희'
WARNING: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:40,312] [ WARNING] text_extractor_paddle.py:602 - 검색 영역: (13, 136, 112, 128)
WARNING: OCR로 추출된 텍스트 개수: 1개
[2025-07-27 20:18:40,312] [ WARNING] text_extractor_paddle.py:603 - OCR로 추출된 텍스트 개수: 1개
WARNING: 가능한 원인:
[2025-07-27 20:18:40,313] [ WARNING] text_extractor_paddle.py:605 - 가능한 원인:
WARNING: 1. 텍스트가 검색 영역 밖에 있음
[2025-07-27 20:18:40,314] [ WARNING] text_extractor_paddle.py:606 - 1. 텍스트가 검색 영역 밖에 있음
WARNING: 2. OCR 인식 오류
[2025-07-27 20:18:40,314] [ WARNING] text_extractor_paddle.py:607 - 2. OCR 인식 오류
WARNING: 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
[2025-07-27 20:18:40,315] [ WARNING] text_extractor_paddle.py:608 - 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
INFO: find_text 실행 시간: 0.998초
[2025-07-27 20:18:40,315] [    INFO] text_extractor_paddle.py:32 - find_text 실행 시간: 0.998초
INFO: 텍스트를 찾지 못했습니다. 1.0초 후 재시도합니다... (시도 2/3)
[2025-07-27 20:18:40,316] [    INFO] executor.py:252 - 텍스트를 찾지 못했습니다. 1.0초 후 재시도합니다... (시도 2/3)
INFO: 추출된 텍스트 항목: 1개
[2025-07-27 20:18:42,347] [    INFO] text_extractor_paddle.py:465 - 추출된 텍스트 항목: 1개
INFO: === OCR 텍스트 추출 결과 ===
[2025-07-27 20:18:42,349] [    INFO] text_extractor_paddle.py:468 - === OCR 텍스트 추출 결과 ===
INFO: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:42,350] [    INFO] text_extractor_paddle.py:469 - 검색 영역: (13, 136, 112, 128)
INFO: 추출된 텍스트 개수: 1개
[2025-07-27 20:18:42,350] [    INFO] text_extractor_paddle.py:470 - 추출된 텍스트 개수: 1개
INFO: 추출된 텍스트 목록:
[2025-07-27 20:18:42,351] [    INFO] text_extractor_paddle.py:473 - 추출된 텍스트 목록:
INFO:   [0] 'K1' 위치: (28, 153), 영역: (13, 139, 31, 28), 신뢰도: 1.00
[2025-07-27 20:18:42,351] [    INFO] text_extractor_paddle.py:475 -   [0] 'K1' 위치: (28, 153), 영역: (13, 139, 31, 28), 신뢰도: 1.00
INFO: extract_text_from_region 실행 시간: 1.035초
[2025-07-27 20:18:42,352] [    INFO] text_extractor_paddle.py:32 - extract_text_from_region 실행 시간: 1.035초
INFO: === 텍스트 검색 시작 ===
[2025-07-27 20:18:42,353] [    INFO] text_extractor_paddle.py:549 - === 텍스트 검색 시작 ===
INFO: 찾을 텍스트: '이영희'
[2025-07-27 20:18:42,353] [    INFO] text_extractor_paddle.py:550 - 찾을 텍스트: '이영희'
INFO: 정규화된 텍스트: '이영희'
[2025-07-27 20:18:42,354] [    INFO] text_extractor_paddle.py:551 - 정규화된 텍스트: '이영희'
INFO: 검색 모드: 부분 일치
[2025-07-27 20:18:42,354] [    INFO] text_extractor_paddle.py:552 - 검색 모드: 부분 일치
WARNING: === 텍스트를 찾을 수 없음 ===
[2025-07-27 20:18:42,355] [ WARNING] text_extractor_paddle.py:600 - === 텍스트를 찾을 수 없음 ===
WARNING: 찾으려던 텍스트: '이영희'
[2025-07-27 20:18:42,355] [ WARNING] text_extractor_paddle.py:601 - 찾으려던 텍스트: '이영희'
WARNING: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:42,356] [ WARNING] text_extractor_paddle.py:602 - 검색 영역: (13, 136, 112, 128)
WARNING: OCR로 추출된 텍스트 개수: 1개
[2025-07-27 20:18:42,356] [ WARNING] text_extractor_paddle.py:603 - OCR로 추출된 텍스트 개수: 1개
WARNING: 가능한 원인:
[2025-07-27 20:18:42,357] [ WARNING] text_extractor_paddle.py:605 - 가능한 원인:
WARNING: 1. 텍스트가 검색 영역 밖에 있음
[2025-07-27 20:18:42,357] [ WARNING] text_extractor_paddle.py:606 - 1. 텍스트가 검색 영역 밖에 있음
WARNING: 2. OCR 인식 오류
[2025-07-27 20:18:42,358] [ WARNING] text_extractor_paddle.py:607 - 2. OCR 인식 오류
WARNING: 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
[2025-07-27 20:18:42,358] [ WARNING] text_extractor_paddle.py:608 - 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
INFO: find_text 실행 시간: 1.042초
[2025-07-27 20:18:42,359] [    INFO] text_extractor_paddle.py:32 - find_text 실행 시간: 1.042초
WARNING: 텍스트 검색이 5.10초 걸렸습니다. 검색 영역을 좁히는 것을 고려하세요.
[2025-07-27 20:18:42,359] [ WARNING] executor.py:258 - 텍스트 검색이 5.10초 걸렸습니다. 검색 영역을 좁히는 것을 고려하세요.
WARNING: ======== 텍스트 검색 실패 ========
[2025-07-27 20:18:42,360] [ WARNING] executor.py:673 - ======== 텍스트 검색 실패 ========
WARNING: 찾을 수 없는 텍스트: '이영희'
[2025-07-27 20:18:42,360] [ WARNING] executor.py:674 - 찾을 수 없는 텍스트: '이영희'
INFO: 단계 실행 완료: 텍스트 검색
[2025-07-27 20:18:42,362] [    INFO] executor.py:96 - 단계 실행 완료: 텍스트 검색
INFO:
==================================================
[2025-07-27 20:18:42,363] [    INFO] executor.py:90 -
==================================================
INFO: 단계 실행 시작: 텍스트 입력 (keyboard_type)
[2025-07-27 20:18:42,364] [    INFO] executor.py:91 - 단계 실행 시작: 텍스트 입력 (keyboard_type)
INFO: ==================================================
[2025-07-27 20:18:42,364] [    INFO] executor.py:92 - ==================================================
INFO: ======== 키보드 입력 시작 ========
[2025-07-27 20:18:42,466] [    INFO] executor.py:441 - ======== 키보드 입력 시작 ========
INFO: 현재 마우스 위치 (입력 위치): (1249, 509)
[2025-07-27 20:18:42,467] [    INFO] executor.py:442 - 현재 마우스 위치 (입력 위치): (1249, 509)
INFO: 원본 텍스트: '${환자명}${작업번호}'
[2025-07-27 20:18:42,468] [    INFO] executor.py:443 - 원본 텍스트: '${환자명}${작업번호}'
INFO: 변수 치환 사용: True
[2025-07-27 20:18:42,468] [    INFO] executor.py:444 - 변수 치환 사용: True
INFO: 사용 가능한 변수: ['작업번호', '환자명', '병력번호', '검사항목', '검사일자', '매크로_상태', '매크로_실행시간', '매크로_오류메시지']
[2025-07-27 20:18:42,469] [    INFO] executor.py:445 - 사용 가능한 변수: ['작업번호', '환자명', '병력번호', '검사항목', '검사일자', '매크로_상태', '매크로_실행시간', '매크로_오류메시지']
INFO: 치환된 텍스트: '이영희3'
[2025-07-27 20:18:42,470] [    INFO] executor.py:450 - 치환된 텍스트: '이영희3'
INFO: 입력 시작 - 텍스트: '이영희3', 간격: 0.0초
[2025-07-27 20:18:42,470] [    INFO] executor.py:452 - 입력 시작 - 텍스트: '이영희3', 간격: 0.0초
INFO: 입력 완료 - 마우스 위치: (1249, 509)
[2025-07-27 20:18:42,573] [    INFO] executor.py:457 - 입력 완료 - 마우스 위치: (1249, 509)
INFO: ======== 키보드 입력 완료 ========
[2025-07-27 20:18:42,574] [    INFO] executor.py:458 - ======== 키보드 입력 완료 ========
INFO: 단계 실행 완료: 텍스트 입력
[2025-07-27 20:18:42,575] [    INFO] executor.py:96 - 단계 실행 완료: 텍스트 입력
INFO: Row 2 completed successfully - updating status to COMPLETED
[2025-07-27 20:18:42,576] [    INFO] engine.py:760 - Row 2 completed successfully - updating status to COMPLETED
INFO: ExcelManager.update_row_status called - row: 2, status: '완료', save_immediately: True
[2025-07-27 20:18:42,576] [    INFO] excel_manager.py:342 - ExcelManager.update_row_status called - row: 2, status: '완 료', save_immediately: True
INFO: Saving file immediately after status update for row 2
[2025-07-27 20:18:42,577] [    INFO] excel_manager.py:352 - Saving file immediately after status update for row 2
INFO: File modification time before save: Sun Jul 27 20:18:36 2025
[2025-07-27 20:18:42,587] [    INFO] excel_manager.py:265 - File modification time before save: Sun Jul 27 20:18:36 2025
INFO: Status column '매크로_상태' values before save: {'완료': 3, '미완료': 2}
[2025-07-27 20:18:42,588] [    INFO] excel_manager.py:270 - Status column '매크로_상태' values before save: {'완료': 3, '미완료': 2}
INFO: File modification time after save: Sun Jul 27 20:18:42 2025
[2025-07-27 20:18:42,595] [    INFO] excel_manager.py:292 - File modification time after save: Sun Jul 27 20:18:42 2025
INFO: Status column '매크로_상태' values after save: {'완료': 3, '미완료': 2}
[2025-07-27 20:18:42,596] [    INFO] excel_manager.py:300 - Status column '매크로_상태' values after save: {'완료': 3, '미완료': 2}
INFO: Saved Excel file successfully: C:\mag\macro\demo_data.xlsx
[2025-07-27 20:18:42,596] [    INFO] excel_manager.py:302 - Saved Excel file successfully: C:\mag\macro\demo_data.xlsx
INFO:
==================================================
[2025-07-27 20:18:42,597] [    INFO] executor.py:90 -
==================================================
INFO: 단계 실행 시작: 텍스트 검색 (ocr_text)
[2025-07-27 20:18:42,599] [    INFO] executor.py:91 - 단계 실행 시작: 텍스트 검색 (ocr_text)
INFO: ==================================================
[2025-07-27 20:18:42,600] [    INFO] executor.py:92 - ==================================================
INFO: ======== 텍스트 검색 시작 ========
[2025-07-27 20:18:42,901] [    INFO] executor.py:640 - ======== 텍스트 검색 시작 ========
INFO: 검색 텍스트: '박민수'
[2025-07-27 20:18:42,902] [    INFO] executor.py:641 - 검색 텍스트: '박민수'
INFO: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:42,903] [    INFO] executor.py:642 - 검색 영역: (13, 136, 112, 128)
INFO: 검색 옵션: exact_match=False, confidence=0.4
[2025-07-27 20:18:42,904] [    INFO] executor.py:643 - 검색 옵션: exact_match=False, confidence=0.4
INFO: 클릭 옵션: click_on_found=True, offset=(0, 0), double_click=True
[2025-07-27 20:18:42,904] [    INFO] executor.py:644 - 클릭 옵션: click_on_found=True, offset=(0, 0), double_click=True
INFO: 추출된 텍스트 항목: 1개
[2025-07-27 20:18:43,911] [    INFO] text_extractor_paddle.py:465 - 추출된 텍스트 항목: 1개
INFO: === OCR 텍스트 추출 결과 ===
[2025-07-27 20:18:43,913] [    INFO] text_extractor_paddle.py:468 - === OCR 텍스트 추출 결과 ===
INFO: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:43,913] [    INFO] text_extractor_paddle.py:469 - 검색 영역: (13, 136, 112, 128)
INFO: 추출된 텍스트 개수: 1개
[2025-07-27 20:18:43,914] [    INFO] text_extractor_paddle.py:470 - 추출된 텍스트 개수: 1개
INFO: 추출된 텍스트 목록:
[2025-07-27 20:18:43,914] [    INFO] text_extractor_paddle.py:473 - 추출된 텍스트 목록:
INFO:   [0] 'K1' 위치: (28, 153), 영역: (13, 139, 31, 28), 신뢰도: 1.00
[2025-07-27 20:18:43,915] [    INFO] text_extractor_paddle.py:475 -   [0] 'K1' 위치: (28, 153), 영역: (13, 139, 31, 28), 신뢰도: 1.00
INFO: extract_text_from_region 실행 시간: 1.010초
[2025-07-27 20:18:43,915] [    INFO] text_extractor_paddle.py:32 - extract_text_from_region 실행 시간: 1.010초
INFO: === 텍스트 검색 시작 ===
[2025-07-27 20:18:43,916] [    INFO] text_extractor_paddle.py:549 - === 텍스트 검색 시작 ===
INFO: 찾을 텍스트: '박민수'
[2025-07-27 20:18:43,916] [    INFO] text_extractor_paddle.py:550 - 찾을 텍스트: '박민수'
INFO: 정규화된 텍스트: '박민수'
[2025-07-27 20:18:43,917] [    INFO] text_extractor_paddle.py:551 - 정규화된 텍스트: '박민수'
INFO: 검색 모드: 부분 일치
[2025-07-27 20:18:43,917] [    INFO] text_extractor_paddle.py:552 - 검색 모드: 부분 일치
WARNING: === 텍스트를 찾을 수 없음 ===
[2025-07-27 20:18:43,918] [ WARNING] text_extractor_paddle.py:600 - === 텍스트를 찾을 수 없음 ===
WARNING: 찾으려던 텍스트: '박민수'
[2025-07-27 20:18:43,918] [ WARNING] text_extractor_paddle.py:601 - 찾으려던 텍스트: '박민수'
WARNING: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:43,919] [ WARNING] text_extractor_paddle.py:602 - 검색 영역: (13, 136, 112, 128)
WARNING: OCR로 추출된 텍스트 개수: 1개
[2025-07-27 20:18:43,919] [ WARNING] text_extractor_paddle.py:603 - OCR로 추출된 텍스트 개수: 1개
WARNING: 가능한 원인:
[2025-07-27 20:18:43,920] [ WARNING] text_extractor_paddle.py:605 - 가능한 원인:
WARNING: 1. 텍스트가 검색 영역 밖에 있음
[2025-07-27 20:18:43,920] [ WARNING] text_extractor_paddle.py:606 - 1. 텍스트가 검색 영역 밖에 있음
WARNING: 2. OCR 인식 오류
[2025-07-27 20:18:43,921] [ WARNING] text_extractor_paddle.py:607 - 2. OCR 인식 오류
WARNING: 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
[2025-07-27 20:18:43,921] [ WARNING] text_extractor_paddle.py:608 - 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
INFO: find_text 실행 시간: 1.017초
[2025-07-27 20:18:43,922] [    INFO] text_extractor_paddle.py:32 - find_text 실행 시간: 1.017초
INFO: 텍스트를 찾지 못했습니다. 1.0초 후 재시도합니다... (시도 1/3)
[2025-07-27 20:18:43,922] [    INFO] executor.py:252 - 텍스트를 찾지 못했습니다. 1.0초 후 재시도합니다... (시도 1/3)
INFO: 추출된 텍스트 항목: 1개
[2025-07-27 20:18:45,979] [    INFO] text_extractor_paddle.py:465 - 추출된 텍스트 항목: 1개
INFO: === OCR 텍스트 추출 결과 ===
[2025-07-27 20:18:45,980] [    INFO] text_extractor_paddle.py:468 - === OCR 텍스트 추출 결과 ===
INFO: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:45,981] [    INFO] text_extractor_paddle.py:469 - 검색 영역: (13, 136, 112, 128)
INFO: 추출된 텍스트 개수: 1개
[2025-07-27 20:18:45,981] [    INFO] text_extractor_paddle.py:470 - 추출된 텍스트 개수: 1개
INFO: 추출된 텍스트 목록:
[2025-07-27 20:18:45,982] [    INFO] text_extractor_paddle.py:473 - 추출된 텍스트 목록:
INFO:   [0] 'K1' 위치: (28, 153), 영역: (13, 139, 31, 28), 신뢰도: 1.00
[2025-07-27 20:18:45,983] [    INFO] text_extractor_paddle.py:475 -   [0] 'K1' 위치: (28, 153), 영역: (13, 139, 31, 28), 신뢰도: 1.00
INFO: extract_text_from_region 실행 시간: 1.059초
[2025-07-27 20:18:45,983] [    INFO] text_extractor_paddle.py:32 - extract_text_from_region 실행 시간: 1.059초
INFO: === 텍스트 검색 시작 ===
[2025-07-27 20:18:45,984] [    INFO] text_extractor_paddle.py:549 - === 텍스트 검색 시작 ===
INFO: 찾을 텍스트: '박민수'
[2025-07-27 20:18:45,984] [    INFO] text_extractor_paddle.py:550 - 찾을 텍스트: '박민수'
INFO: 정규화된 텍스트: '박민수'
[2025-07-27 20:18:45,985] [    INFO] text_extractor_paddle.py:551 - 정규화된 텍스트: '박민수'
INFO: 검색 모드: 부분 일치
[2025-07-27 20:18:45,985] [    INFO] text_extractor_paddle.py:552 - 검색 모드: 부분 일치
WARNING: === 텍스트를 찾을 수 없음 ===
[2025-07-27 20:18:45,986] [ WARNING] text_extractor_paddle.py:600 - === 텍스트를 찾을 수 없음 ===
WARNING: 찾으려던 텍스트: '박민수'
[2025-07-27 20:18:45,986] [ WARNING] text_extractor_paddle.py:601 - 찾으려던 텍스트: '박민수'
WARNING: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:45,987] [ WARNING] text_extractor_paddle.py:602 - 검색 영역: (13, 136, 112, 128)
WARNING: OCR로 추출된 텍스트 개수: 1개
[2025-07-27 20:18:45,987] [ WARNING] text_extractor_paddle.py:603 - OCR로 추출된 텍스트 개수: 1개
WARNING: 가능한 원인:
[2025-07-27 20:18:45,988] [ WARNING] text_extractor_paddle.py:605 - 가능한 원인:
WARNING: 1. 텍스트가 검색 영역 밖에 있음
[2025-07-27 20:18:45,988] [ WARNING] text_extractor_paddle.py:606 - 1. 텍스트가 검색 영역 밖에 있음
WARNING: 2. OCR 인식 오류
[2025-07-27 20:18:45,989] [ WARNING] text_extractor_paddle.py:607 - 2. OCR 인식 오류
WARNING: 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
[2025-07-27 20:18:45,991] [ WARNING] text_extractor_paddle.py:608 - 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
INFO: find_text 실행 시간: 1.067초
[2025-07-27 20:18:45,991] [    INFO] text_extractor_paddle.py:32 - find_text 실행 시간: 1.067초
INFO: 텍스트를 찾지 못했습니다. 1.0초 후 재시도합니다... (시도 2/3)
[2025-07-27 20:18:45,992] [    INFO] executor.py:252 - 텍스트를 찾지 못했습니다. 1.0초 후 재시도합니다... (시도 2/3)
INFO: 추출된 텍스트 항목: 1개
[2025-07-27 20:18:48,025] [    INFO] text_extractor_paddle.py:465 - 추출된 텍스트 항목: 1개
INFO: === OCR 텍스트 추출 결과 ===
[2025-07-27 20:18:48,027] [    INFO] text_extractor_paddle.py:468 - === OCR 텍스트 추출 결과 ===
INFO: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:48,027] [    INFO] text_extractor_paddle.py:469 - 검색 영역: (13, 136, 112, 128)
INFO: 추출된 텍스트 개수: 1개
[2025-07-27 20:18:48,028] [    INFO] text_extractor_paddle.py:470 - 추출된 텍스트 개수: 1개
INFO: 추출된 텍스트 목록:
[2025-07-27 20:18:48,029] [    INFO] text_extractor_paddle.py:473 - 추출된 텍스트 목록:
INFO:   [0] 'K1' 위치: (28, 153), 영역: (13, 139, 31, 28), 신뢰도: 1.00
[2025-07-27 20:18:48,029] [    INFO] text_extractor_paddle.py:475 -   [0] 'K1' 위치: (28, 153), 영역: (13, 139, 31, 28), 신뢰도: 1.00
INFO: extract_text_from_region 실행 시간: 1.038초
[2025-07-27 20:18:48,030] [    INFO] text_extractor_paddle.py:32 - extract_text_from_region 실행 시간: 1.038초
INFO: === 텍스트 검색 시작 ===
[2025-07-27 20:18:48,030] [    INFO] text_extractor_paddle.py:549 - === 텍스트 검색 시작 ===
INFO: 찾을 텍스트: '박민수'
[2025-07-27 20:18:48,031] [    INFO] text_extractor_paddle.py:550 - 찾을 텍스트: '박민수'
INFO: 정규화된 텍스트: '박민수'
[2025-07-27 20:18:48,031] [    INFO] text_extractor_paddle.py:551 - 정규화된 텍스트: '박민수'
INFO: 검색 모드: 부분 일치
[2025-07-27 20:18:48,032] [    INFO] text_extractor_paddle.py:552 - 검색 모드: 부분 일치
WARNING: === 텍스트를 찾을 수 없음 ===
[2025-07-27 20:18:48,032] [ WARNING] text_extractor_paddle.py:600 - === 텍스트를 찾을 수 없음 ===
WARNING: 찾으려던 텍스트: '박민수'
[2025-07-27 20:18:48,033] [ WARNING] text_extractor_paddle.py:601 - 찾으려던 텍스트: '박민수'
WARNING: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:48,033] [ WARNING] text_extractor_paddle.py:602 - 검색 영역: (13, 136, 112, 128)
WARNING: OCR로 추출된 텍스트 개수: 1개
[2025-07-27 20:18:48,034] [ WARNING] text_extractor_paddle.py:603 - OCR로 추출된 텍스트 개수: 1개
WARNING: 가능한 원인:
[2025-07-27 20:18:48,034] [ WARNING] text_extractor_paddle.py:605 - 가능한 원인:
WARNING: 1. 텍스트가 검색 영역 밖에 있음
[2025-07-27 20:18:48,036] [ WARNING] text_extractor_paddle.py:606 - 1. 텍스트가 검색 영역 밖에 있음
WARNING: 2. OCR 인식 오류
[2025-07-27 20:18:48,037] [ WARNING] text_extractor_paddle.py:607 - 2. OCR 인식 오류
WARNING: 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
[2025-07-27 20:18:48,037] [ WARNING] text_extractor_paddle.py:608 - 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
INFO: find_text 실행 시간: 1.046초
[2025-07-27 20:18:48,038] [    INFO] text_extractor_paddle.py:32 - find_text 실행 시간: 1.046초
WARNING: 텍스트 검색이 5.13초 걸렸습니다. 검색 영역을 좁히는 것을 고려하세요.
[2025-07-27 20:18:48,038] [ WARNING] executor.py:258 - 텍스트 검색이 5.13초 걸렸습니다. 검색 영역을 좁히는 것을 고려하세요.
WARNING: ======== 텍스트 검색 실패 ========
[2025-07-27 20:18:48,039] [ WARNING] executor.py:673 - ======== 텍스트 검색 실패 ========
WARNING: 찾을 수 없는 텍스트: '박민수'
[2025-07-27 20:18:48,039] [ WARNING] executor.py:674 - 찾을 수 없는 텍스트: '박민수'
INFO: 단계 실행 완료: 텍스트 검색
[2025-07-27 20:18:48,040] [    INFO] executor.py:96 - 단계 실행 완료: 텍스트 검색
INFO:
==================================================
[2025-07-27 20:18:48,041] [    INFO] executor.py:90 -
==================================================
INFO: 단계 실행 시작: 텍스트 입력 (keyboard_type)
[2025-07-27 20:18:48,041] [    INFO] executor.py:91 - 단계 실행 시작: 텍스트 입력 (keyboard_type)
INFO: ==================================================
[2025-07-27 20:18:48,042] [    INFO] executor.py:92 - ==================================================
INFO: ======== 키보드 입력 시작 ========
[2025-07-27 20:18:48,143] [    INFO] executor.py:441 - ======== 키보드 입력 시작 ========
INFO: 현재 마우스 위치 (입력 위치): (1249, 509)
[2025-07-27 20:18:48,144] [    INFO] executor.py:442 - 현재 마우스 위치 (입력 위치): (1249, 509)
INFO: 원본 텍스트: '${환자명}${작업번호}'
[2025-07-27 20:18:48,144] [    INFO] executor.py:443 - 원본 텍스트: '${환자명}${작업번호}'
INFO: 변수 치환 사용: True
[2025-07-27 20:18:48,144] [    INFO] executor.py:444 - 변수 치환 사용: True
INFO: 사용 가능한 변수: ['작업번호', '환자명', '병력번호', '검사항목', '검사일자', '매크로_상태', '매크로_실행시간', '매크로_오류메시지']
[2025-07-27 20:18:48,145] [    INFO] executor.py:445 - 사용 가능한 변수: ['작업번호', '환자명', '병력번호', '검사항목', '검사일자', '매크로_상태', '매크로_실행시간', '매크로_오류메시지']
INFO: 치환된 텍스트: '박민수4'
[2025-07-27 20:18:48,145] [    INFO] executor.py:450 - 치환된 텍스트: '박민수4'
INFO: 입력 시작 - 텍스트: '박민수4', 간격: 0.0초
[2025-07-27 20:18:48,145] [    INFO] executor.py:452 - 입력 시작 - 텍스트: '박민수4', 간격: 0.0초
INFO: 입력 완료 - 마우스 위치: (1249, 509)
[2025-07-27 20:18:48,247] [    INFO] executor.py:457 - 입력 완료 - 마우스 위치: (1249, 509)
INFO: ======== 키보드 입력 완료 ========
[2025-07-27 20:18:48,248] [    INFO] executor.py:458 - ======== 키보드 입력 완료 ========
INFO: 단계 실행 완료: 텍스트 입력
[2025-07-27 20:18:48,249] [    INFO] executor.py:96 - 단계 실행 완료: 텍스트 입력
INFO: Row 3 completed successfully - updating status to COMPLETED
[2025-07-27 20:18:48,249] [    INFO] engine.py:760 - Row 3 completed successfully - updating status to COMPLETED
INFO: ExcelManager.update_row_status called - row: 3, status: '완료', save_immediately: True
[2025-07-27 20:18:48,250] [    INFO] excel_manager.py:342 - ExcelManager.update_row_status called - row: 3, status: '완 료', save_immediately: True
INFO: Saving file immediately after status update for row 3
[2025-07-27 20:18:48,251] [    INFO] excel_manager.py:352 - Saving file immediately after status update for row 3
INFO: File modification time before save: Sun Jul 27 20:18:42 2025
[2025-07-27 20:18:48,259] [    INFO] excel_manager.py:265 - File modification time before save: Sun Jul 27 20:18:42 2025
INFO: Status column '매크로_상태' values before save: {'완료': 4, '미완료': 1}
[2025-07-27 20:18:48,261] [    INFO] excel_manager.py:270 - Status column '매크로_상태' values before save: {'완료': 4, '미완료': 1}
INFO: File modification time after save: Sun Jul 27 20:18:48 2025
[2025-07-27 20:18:48,269] [    INFO] excel_manager.py:292 - File modification time after save: Sun Jul 27 20:18:48 2025
INFO: Status column '매크로_상태' values after save: {'완료': 4, '미완료': 1}
[2025-07-27 20:18:48,269] [    INFO] excel_manager.py:300 - Status column '매크로_상태' values after save: {'완료': 4, '미완료': 1}
INFO: Saved Excel file successfully: C:\mag\macro\demo_data.xlsx
[2025-07-27 20:18:48,270] [    INFO] excel_manager.py:302 - Saved Excel file successfully: C:\mag\macro\demo_data.xlsx
INFO:
==================================================
[2025-07-27 20:18:48,272] [    INFO] executor.py:90 -
==================================================
INFO: 단계 실행 시작: 텍스트 검색 (ocr_text)
[2025-07-27 20:18:48,272] [    INFO] executor.py:91 - 단계 실행 시작: 텍스트 검색 (ocr_text)
INFO: ==================================================
[2025-07-27 20:18:48,273] [    INFO] executor.py:92 - ==================================================
INFO: ======== 텍스트 검색 시작 ========
[2025-07-27 20:18:48,575] [    INFO] executor.py:640 - ======== 텍스트 검색 시작 ========
INFO: 검색 텍스트: '최지우'
[2025-07-27 20:18:48,580] [    INFO] executor.py:641 - 검색 텍스트: '최지우'
INFO: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:48,582] [    INFO] executor.py:642 - 검색 영역: (13, 136, 112, 128)
INFO: 검색 옵션: exact_match=False, confidence=0.4
[2025-07-27 20:18:48,582] [    INFO] executor.py:643 - 검색 옵션: exact_match=False, confidence=0.4
INFO: 클릭 옵션: click_on_found=True, offset=(0, 0), double_click=True
[2025-07-27 20:18:48,583] [    INFO] executor.py:644 - 클릭 옵션: click_on_found=True, offset=(0, 0), double_click=True
INFO: 추출된 텍스트 항목: 1개
[2025-07-27 20:18:49,586] [    INFO] text_extractor_paddle.py:465 - 추출된 텍스트 항목: 1개
INFO: === OCR 텍스트 추출 결과 ===
[2025-07-27 20:18:49,588] [    INFO] text_extractor_paddle.py:468 - === OCR 텍스트 추출 결과 ===
INFO: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:49,588] [    INFO] text_extractor_paddle.py:469 - 검색 영역: (13, 136, 112, 128)
INFO: 추출된 텍스트 개수: 1개
[2025-07-27 20:18:49,589] [    INFO] text_extractor_paddle.py:470 - 추출된 텍스트 개수: 1개
INFO: 추출된 텍스트 목록:
[2025-07-27 20:18:49,589] [    INFO] text_extractor_paddle.py:473 - 추출된 텍스트 목록:
INFO:   [0] 'K1' 위치: (28, 153), 영역: (13, 139, 31, 28), 신뢰도: 1.00
[2025-07-27 20:18:49,590] [    INFO] text_extractor_paddle.py:475 -   [0] 'K1' 위치: (28, 153), 영역: (13, 139, 31, 28), 신뢰도: 1.00
INFO: extract_text_from_region 실행 시간: 1.007초
[2025-07-27 20:18:49,590] [    INFO] text_extractor_paddle.py:32 - extract_text_from_region 실행 시간: 1.007초
INFO: === 텍스트 검색 시작 ===
[2025-07-27 20:18:49,591] [    INFO] text_extractor_paddle.py:549 - === 텍스트 검색 시작 ===
INFO: 찾을 텍스트: '최지우'
[2025-07-27 20:18:49,591] [    INFO] text_extractor_paddle.py:550 - 찾을 텍스트: '최지우'
INFO: 정규화된 텍스트: '최지우'
[2025-07-27 20:18:49,592] [    INFO] text_extractor_paddle.py:551 - 정규화된 텍스트: '최지우'
INFO: 검색 모드: 부분 일치
[2025-07-27 20:18:49,592] [    INFO] text_extractor_paddle.py:552 - 검색 모드: 부분 일치
WARNING: === 텍스트를 찾을 수 없음 ===
[2025-07-27 20:18:49,593] [ WARNING] text_extractor_paddle.py:600 - === 텍스트를 찾을 수 없음 ===
WARNING: 찾으려던 텍스트: '최지우'
[2025-07-27 20:18:49,593] [ WARNING] text_extractor_paddle.py:601 - 찾으려던 텍스트: '최지우'
WARNING: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:49,594] [ WARNING] text_extractor_paddle.py:602 - 검색 영역: (13, 136, 112, 128)
WARNING: OCR로 추출된 텍스트 개수: 1개
[2025-07-27 20:18:49,594] [ WARNING] text_extractor_paddle.py:603 - OCR로 추출된 텍스트 개수: 1개
WARNING: 가능한 원인:
[2025-07-27 20:18:49,595] [ WARNING] text_extractor_paddle.py:605 - 가능한 원인:
WARNING: 1. 텍스트가 검색 영역 밖에 있음
[2025-07-27 20:18:49,595] [ WARNING] text_extractor_paddle.py:606 - 1. 텍스트가 검색 영역 밖에 있음
WARNING: 2. OCR 인식 오류
[2025-07-27 20:18:49,596] [ WARNING] text_extractor_paddle.py:607 - 2. OCR 인식 오류
WARNING: 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
[2025-07-27 20:18:49,596] [ WARNING] text_extractor_paddle.py:608 - 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
INFO: find_text 실행 시간: 1.014초
[2025-07-27 20:18:49,597] [    INFO] text_extractor_paddle.py:32 - find_text 실행 시간: 1.014초
INFO: 텍스트를 찾지 못했습니다. 1.0초 후 재시도합니다... (시도 1/3)
[2025-07-27 20:18:49,597] [    INFO] executor.py:252 - 텍스트를 찾지 못했습니다. 1.0초 후 재시도합니다... (시도 1/3)
INFO: State changed: running -> stopping
[2025-07-27 20:18:50,497] [    INFO] engine.py:106 - State changed: running -> stopping
INFO: Stopping execution...
[2025-07-27 20:18:50,504] [    INFO] engine.py:613 - Stopping execution...
INFO: 추출된 텍스트 항목: 2개
[2025-07-27 20:18:51,675] [    INFO] text_extractor_paddle.py:465 - 추출된 텍스트 항목: 2개
INFO: === OCR 텍스트 추출 결과 ===
[2025-07-27 20:18:51,677] [    INFO] text_extractor_paddle.py:468 - === OCR 텍스트 추출 결과 ===
INFO: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:51,677] [    INFO] text_extractor_paddle.py:469 - 검색 영역: (13, 136, 112, 128)
INFO: 추출된 텍스트 개수: 2개
[2025-07-27 20:18:51,678] [    INFO] text_extractor_paddle.py:470 - 추출된 텍스트 개수: 2개
INFO: 추출된 텍스트 목록:
[2025-07-27 20:18:51,678] [    INFO] text_extractor_paddle.py:473 - 추출된 텍스트 목록:
INFO:   [0] 'K1' 위치: (28, 153), 영역: (13, 141, 30, 25), 신뢰도: 1.00
[2025-07-27 20:18:51,679] [    INFO] text_extractor_paddle.py:475 -   [0] 'K1' 위치: (28, 153), 영역: (13, 141, 30, 25), 신뢰도: 1.00
INFO:   [1] 'Y' 위치: (20, 234), 영역: (14, 227, 13, 15), 신뢰도: 0.99
[2025-07-27 20:18:51,679] [    INFO] text_extractor_paddle.py:475 -   [1] 'Y' 위치: (20, 234), 영역: (14, 227, 13, 15), 신뢰도: 0.99
INFO: extract_text_from_region 실행 시간: 1.082초
[2025-07-27 20:18:51,680] [    INFO] text_extractor_paddle.py:32 - extract_text_from_region 실행 시간: 1.082초
INFO: === 텍스트 검색 시작 ===
[2025-07-27 20:18:51,680] [    INFO] text_extractor_paddle.py:549 - === 텍스트 검색 시작 ===
INFO: 찾을 텍스트: '최지우'
[2025-07-27 20:18:51,681] [    INFO] text_extractor_paddle.py:550 - 찾을 텍스트: '최지우'
INFO: 정규화된 텍스트: '최지우'
[2025-07-27 20:18:51,681] [    INFO] text_extractor_paddle.py:551 - 정규화된 텍스트: '최지우'
INFO: 검색 모드: 부분 일치
[2025-07-27 20:18:51,682] [    INFO] text_extractor_paddle.py:552 - 검색 모드: 부분 일치
WARNING: === 텍스트를 찾을 수 없음 ===
[2025-07-27 20:18:51,682] [ WARNING] text_extractor_paddle.py:600 - === 텍스트를 찾을 수 없음 ===
WARNING: 찾으려던 텍스트: '최지우'
[2025-07-27 20:18:51,683] [ WARNING] text_extractor_paddle.py:601 - 찾으려던 텍스트: '최지우'
WARNING: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:51,683] [ WARNING] text_extractor_paddle.py:602 - 검색 영역: (13, 136, 112, 128)
WARNING: OCR로 추출된 텍스트 개수: 2개
[2025-07-27 20:18:51,684] [ WARNING] text_extractor_paddle.py:603 - OCR로 추출된 텍스트 개수: 2개
WARNING: 가능한 원인:
[2025-07-27 20:18:51,684] [ WARNING] text_extractor_paddle.py:605 - 가능한 원인:
WARNING: 1. 텍스트가 검색 영역 밖에 있음
[2025-07-27 20:18:51,685] [ WARNING] text_extractor_paddle.py:606 - 1. 텍스트가 검색 영역 밖에 있음
WARNING: 2. OCR 인식 오류
[2025-07-27 20:18:51,685] [ WARNING] text_extractor_paddle.py:607 - 2. OCR 인식 오류
WARNING: 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
[2025-07-27 20:18:51,686] [ WARNING] text_extractor_paddle.py:608 - 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
INFO: find_text 실행 시간: 1.088초
[2025-07-27 20:18:51,686] [    INFO] text_extractor_paddle.py:32 - find_text 실행 시간: 1.088초
INFO: 텍스트를 찾지 못했습니다. 1.0초 후 재시도합니다... (시도 2/3)
[2025-07-27 20:18:51,687] [    INFO] executor.py:252 - 텍스트를 찾지 못했습니다. 1.0초 후 재시도합니다... (시도 2/3)
INFO: 추출된 텍스트 항목: 2개
[2025-07-27 20:18:53,702] [    INFO] text_extractor_paddle.py:465 - 추출된 텍스트 항목: 2개
INFO: === OCR 텍스트 추출 결과 ===
[2025-07-27 20:18:53,704] [    INFO] text_extractor_paddle.py:468 - === OCR 텍스트 추출 결과 ===
INFO: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:53,704] [    INFO] text_extractor_paddle.py:469 - 검색 영역: (13, 136, 112, 128)
INFO: 추출된 텍스트 개수: 2개
[2025-07-27 20:18:53,705] [    INFO] text_extractor_paddle.py:470 - 추출된 텍스트 개수: 2개
INFO: 추출된 텍스트 목록:
[2025-07-27 20:18:53,705] [    INFO] text_extractor_paddle.py:473 - 추출된 텍스트 목록:
INFO:   [0] 'K1' 위치: (28, 153), 영역: (13, 141, 30, 25), 신뢰도: 1.00
[2025-07-27 20:18:53,706] [    INFO] text_extractor_paddle.py:475 -   [0] 'K1' 위치: (28, 153), 영역: (13, 141, 30, 25), 신뢰도: 1.00
INFO:   [1] 'Y' 위치: (20, 234), 영역: (14, 227, 13, 15), 신뢰도: 0.99
[2025-07-27 20:18:53,706] [    INFO] text_extractor_paddle.py:475 -   [1] 'Y' 위치: (20, 234), 영역: (14, 227, 13, 15), 신뢰도: 0.99
INFO: extract_text_from_region 실행 시간: 1.019초
[2025-07-27 20:18:53,707] [    INFO] text_extractor_paddle.py:32 - extract_text_from_region 실행 시간: 1.019초
INFO: === 텍스트 검색 시작 ===
[2025-07-27 20:18:53,707] [    INFO] text_extractor_paddle.py:549 - === 텍스트 검색 시작 ===
INFO: 찾을 텍스트: '최지우'
[2025-07-27 20:18:53,708] [    INFO] text_extractor_paddle.py:550 - 찾을 텍스트: '최지우'
INFO: 정규화된 텍스트: '최지우'
[2025-07-27 20:18:53,708] [    INFO] text_extractor_paddle.py:551 - 정규화된 텍스트: '최지우'
INFO: 검색 모드: 부분 일치
[2025-07-27 20:18:53,709] [    INFO] text_extractor_paddle.py:552 - 검색 모드: 부분 일치
WARNING: === 텍스트를 찾을 수 없음 ===
[2025-07-27 20:18:53,709] [ WARNING] text_extractor_paddle.py:600 - === 텍스트를 찾을 수 없음 ===
WARNING: 찾으려던 텍스트: '최지우'
[2025-07-27 20:18:53,710] [ WARNING] text_extractor_paddle.py:601 - 찾으려던 텍스트: '최지우'
WARNING: 검색 영역: (13, 136, 112, 128)
[2025-07-27 20:18:53,710] [ WARNING] text_extractor_paddle.py:602 - 검색 영역: (13, 136, 112, 128)
WARNING: OCR로 추출된 텍스트 개수: 2개
[2025-07-27 20:18:53,711] [ WARNING] text_extractor_paddle.py:603 - OCR로 추출된 텍스트 개수: 2개
WARNING: 가능한 원인:
[2025-07-27 20:18:53,711] [ WARNING] text_extractor_paddle.py:605 - 가능한 원인:
WARNING: 1. 텍스트가 검색 영역 밖에 있음
[2025-07-27 20:18:53,712] [ WARNING] text_extractor_paddle.py:606 - 1. 텍스트가 검색 영역 밖에 있음
WARNING: 2. OCR 인식 오류
[2025-07-27 20:18:53,712] [ WARNING] text_extractor_paddle.py:607 - 2. OCR 인식 오류
WARNING: 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
[2025-07-27 20:18:53,713] [ WARNING] text_extractor_paddle.py:608 - 3. 텍스트 형식 불일치 (띄어쓰기, 특수문자 등)
INFO: find_text 실행 시간: 1.025초
[2025-07-27 20:18:53,713] [    INFO] text_extractor_paddle.py:32 - find_text 실행 시간: 1.025초
WARNING: 텍스트 검색이 5.13초 걸렸습니다. 검색 영역을 좁히는 것을 고려하세요.
[2025-07-27 20:18:53,714] [ WARNING] executor.py:258 - 텍스트 검색이 5.13초 걸렸습니다. 검색 영역을 좁히는 것을 고려하세요.
WARNING: ======== 텍스트 검색 실패 ========
[2025-07-27 20:18:53,714] [ WARNING] executor.py:673 - ======== 텍스트 검색 실패 ========
WARNING: 찾을 수 없는 텍스트: '최지우'
[2025-07-27 20:18:53,715] [ WARNING] executor.py:674 - 찾을 수 없는 텍스트: '최지우'
INFO: 단계 실행 완료: 텍스트 검색
[2025-07-27 20:18:53,715] [    INFO] executor.py:96 - 단계 실행 완료: 텍스트 검색
INFO:
==================================================
[2025-07-27 20:18:53,716] [    INFO] executor.py:90 -
==================================================
INFO: 단계 실행 시작: 텍스트 입력 (keyboard_type)
[2025-07-27 20:18:53,716] [    INFO] executor.py:91 - 단계 실행 시작: 텍스트 입력 (keyboard_type)
INFO: ==================================================
[2025-07-27 20:18:53,718] [    INFO] executor.py:92 - ==================================================
INFO: ======== 키보드 입력 시작 ========
[2025-07-27 20:18:53,820] [    INFO] executor.py:441 - ======== 키보드 입력 시작 ========
INFO: 현재 마우스 위치 (입력 위치): (1249, 509)
[2025-07-27 20:18:53,820] [    INFO] executor.py:442 - 현재 마우스 위치 (입력 위치): (1249, 509)
INFO: 원본 텍스트: '${환자명}${작업번호}'
[2025-07-27 20:18:53,821] [    INFO] executor.py:443 - 원본 텍스트: '${환자명}${작업번호}'
INFO: 변수 치환 사용: True
[2025-07-27 20:18:53,821] [    INFO] executor.py:444 - 변수 치환 사용: True
INFO: 사용 가능한 변수: ['작업번호', '환자명', '병력번호', '검사항목', '검사일자', '매크로_상태', '매크로_실행시간', '매크로_오류메시지']
[2025-07-27 20:18:53,821] [    INFO] executor.py:445 - 사용 가능한 변수: ['작업번호', '환자명', '병력번호', '검사항목', '검사일자', '매크로_상태', '매크로_실행시간', '매크로_오류메시지']
INFO: 치환된 텍스트: '최지우5'
[2025-07-27 20:18:53,821] [    INFO] executor.py:450 - 치환된 텍스트: '최지우5'
INFO: 입력 시작 - 텍스트: '최지우5', 간격: 0.0초
[2025-07-27 20:18:53,822] [    INFO] executor.py:452 - 입력 시작 - 텍스트: '최지우5', 간격: 0.0초
INFO: 입력 완료 - 마우스 위치: (1249, 509)
[2025-07-27 20:18:53,924] [    INFO] executor.py:457 - 입력 완료 - 마우스 위치: (1249, 509)
INFO: ======== 키보드 입력 완료 ========
[2025-07-27 20:18:53,925] [    INFO] executor.py:458 - ======== 키보드 입력 완료 ========
INFO: 단계 실행 완료: 텍스트 입력
[2025-07-27 20:18:53,926] [    INFO] executor.py:96 - 단계 실행 완료: 텍스트 입력
INFO: Row 4 completed successfully - updating status to COMPLETED
[2025-07-27 20:18:53,926] [    INFO] engine.py:760 - Row 4 completed successfully - updating status to COMPLETED
INFO: ExcelManager.update_row_status called - row: 4, status: '완료', save_immediately: True
[2025-07-27 20:18:53,927] [    INFO] excel_manager.py:342 - ExcelManager.update_row_status called - row: 4, status: '완 료', save_immediately: True
INFO: Saving file immediately after status update for row 4
[2025-07-27 20:18:53,928] [    INFO] excel_manager.py:352 - Saving file immediately after status update for row 4
INFO: File modification time before save: Sun Jul 27 20:18:48 2025
[2025-07-27 20:18:53,935] [    INFO] excel_manager.py:265 - File modification time before save: Sun Jul 27 20:18:48 2025
INFO: Status column '매크로_상태' values before save: {'완료': 5}
[2025-07-27 20:18:53,936] [    INFO] excel_manager.py:270 - Status column '매크로_상태' values before save: {'완료': 5}
INFO: File modification time after save: Sun Jul 27 20:18:53 2025
[2025-07-27 20:18:53,944] [    INFO] excel_manager.py:292 - File modification time after save: Sun Jul 27 20:18:53 2025
INFO: Status column '매크로_상태' values after save: {'완료': 5}
[2025-07-27 20:18:53,945] [    INFO] excel_manager.py:300 - Status column '매크로_상태' values after save: {'완료': 5}
INFO: Saved Excel file successfully: C:\mag\macro\demo_data.xlsx
[2025-07-27 20:18:53,945] [    INFO] excel_manager.py:302 - Saved Excel file successfully: C:\mag\macro\demo_data.xlsx
INFO: Saving Excel file after workflow execution...
[2025-07-27 20:18:53,946] [    INFO] engine.py:785 - Saving Excel file after workflow execution...
INFO: File modification time before save: Sun Jul 27 20:18:53 2025
[2025-07-27 20:18:53,953] [    INFO] excel_manager.py:265 - File modification time before save: Sun Jul 27 20:18:53 2025
INFO: Status column '매크로_상태' values before save: {'완료': 5}
[2025-07-27 20:18:53,953] [    INFO] excel_manager.py:270 - Status column '매크로_상태' values before save: {'완료': 5}
INFO: File modification time after save: Sun Jul 27 20:18:53 2025
[2025-07-27 20:18:53,961] [    INFO] excel_manager.py:292 - File modification time after save: Sun Jul 27 20:18:53 2025
INFO: Status column '매크로_상태' values after save: {'완료': 5}
[2025-07-27 20:18:53,961] [    INFO] excel_manager.py:300 - Status column '매크로_상태' values after save: {'완료': 5}
INFO: Saved Excel file successfully: C:\mag\macro\demo_data.xlsx
[2025-07-27 20:18:53,962] [    INFO] excel_manager.py:302 - Saved Excel file successfully: C:\mag\macro\demo_data.xlsx
INFO: Excel file saved successfully: C:\mag\macro\demo_data.xlsx
[2025-07-27 20:18:53,962] [    INFO] engine.py:788 - Excel file saved successfully: C:\mag\macro\demo_data.xlsx
INFO: State changed: stopping -> idle
[2025-07-27 20:18:53,963] [    INFO] engine.py:106 - State changed: stopping -> idle
INFO: Hotkey listener stopped
[2025-07-27 20:18:53,963] [    INFO] hotkey_listener.py:108 - Hotkey listener stopped
INFO: Execution finished
[2025-07-27 20:18:53,969] [    INFO] execution_widget.py:598 - Execution finished
INFO: Requesting Excel data refresh after execution
[2025-07-27 20:18:53,970] [    INFO] execution_widget.py:603 - Requesting Excel data refresh after execution
INFO: Excel refresh requested after execution
[2025-07-27 20:18:53,971] [    INFO] main_window.py:305 - Excel refresh requested after execution
INFO: Refreshing Excel data display
[2025-07-27 20:18:53,971] [    INFO] excel_widget_redesigned.py:565 - Refreshing Excel data display
INFO: Reloading Excel file: C:\mag\macro\demo_data.xlsx
[2025-07-27 20:18:53,973] [    INFO] excel_manager.py:221 - Reloading Excel file: C:\mag\macro\demo_data.xlsx
ERROR: Failed to refresh Excel data: property 'row_count' of 'ExcelData' object has no setter
[2025-07-27 20:18:53,978] [   ERROR] excel_widget_redesigned.py:583 - Failed to refresh Excel data: property 'row_count' of 'ExcelData' object has no setter
DEBUG: _on_step_edit using actual step from macro for type: StepType.OCR_TEXT
DEBUG: _on_step_edit called for step type: StepType.OCR_TEXT
DEBUG: region_buttons_widget not yet initialized, skipping
DEBUG [load_step_data]: Loading step data - region: (13, 136, 112, 128) (type: <class 'tuple'>)
DEBUG [load_step_data]: Extracted column name '환자명' from search_text '${환자명}'
INFO: Created backup: C:\Users\nosky\.excel_macro_automation\macros\backups\11_backup_20250727_201912.json
[2025-07-27 20:19:12,784] [    INFO] macro_storage.py:264 - Created backup: C:\Users\nosky\.excel_macro_automation\macros\backups\11_backup_20250727_201912.json
DEBUG [TextSearchStep.to_dict]: Saving with region=(13, 136, 112, 128)
INFO: Saved macro: C:\mag\macro\11.json
[2025-07-27 20:19:12,788] [    INFO] macro_storage.py:85 - Saved macro: C:\mag\macro\11.json
