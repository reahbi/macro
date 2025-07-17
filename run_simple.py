#!/usr/bin/env python3
"""
가장 단순한 실행 스크립트
"""

import sys
import os

# src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 메인 실행
from main import main
main()