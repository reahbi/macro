"""
Create test Excel data files for workflow testing
"""

import pandas as pd
from pathlib import Path

def create_healthcare_checkup_data():
    """건강검진 결과 테스트 데이터 생성"""
    data = {
        '환자번호': ['P001', 'P002', 'P003', 'P004', 'P005'],
        '이름': ['홍길동', '김영희', '박철수', '이미영', '최민수'],
        '주민번호': ['700101-1******', '850202-2******', '900303-1******', 
                  '950404-2******', '800505-1******'],
        '혈압': ['120/80', '130/85', '125/82', '140/90', '118/78'],
        '혈당': [95, 110, 98, 125, 92],
        '콜레스테롤': [180, 200, 190, 220, 175],
        '판정': ['정상', '주의', '정상', '재검', '정상']
    }
    
    df = pd.DataFrame(data)
    df.to_excel('healthcare_checkup.xlsx', index=False, sheet_name='검진결과')
    print("[OK] healthcare_checkup.xlsx created")

def create_prescription_data():
    """처방전 발행 테스트 데이터 생성"""
    data = {
        '환자번호': ['P101', 'P102', 'P103', 'P104'],
        '이름': ['박민수', '김지원', '정대한', '송미라'],
        '약품코드1': ['MED001', 'MED003', 'MED001', 'MED005'],
        '용량1': ['1T', '2T', '1T', '3T'],
        '약품코드2': ['MED002', '', 'MED004', 'MED006'],
        '용량2': ['2T', '', '1T', '2T'],
        '일수': [30, 14, 30, 7]
    }
    
    df = pd.DataFrame(data)
    df.to_excel('prescription_data.xlsx', index=False, sheet_name='처방목록')
    print("[OK] prescription_data.xlsx created")

def create_approval_data():
    """전자결재 테스트 데이터 생성"""
    data = {
        '제목': ['사무용품 구매', '회의실 예약', '출장 신청', '교육 참가'],
        '금액': [500000, 0, 300000, 150000],
        '내용': ['프린터 토너 외', '3층 대회의실', '부산 출장 2박3일', 'Python 교육'],
        '결재선1': ['김과장', '이과장', '박과장', '최과장'],
        '결재선2': ['박부장', '김부장', '이부장', '정부장'],
        '첨부파일': ['C:\\품의\\견적서1.pdf', '', 'C:\\출장\\일정표.pdf', 'C:\\교육\\안내문.pdf']
    }
    
    df = pd.DataFrame(data)
    df.to_excel('approval_data.xlsx', index=False, sheet_name='결재목록')
    print("[OK] approval_data.xlsx created")

def create_customer_update_data():
    """고객 정보 업데이트 테스트 데이터 생성"""
    data = {
        '고객번호': ['C1001', 'C1002', 'C1003', 'C1004'],
        '고객명': ['(주)한국', '(주)서울', '(주)부산', '(주)대전'],
        '신규전화': ['02-1234-5678', '02-2345-6789', '', '042-4567-8901'],
        '신규주소': ['서울시 강남구', '', '부산시 해운대구', '대전시 유성구'],
        '등급변경': ['VIP', 'GOLD', '', 'VIP'],
        '메모': ['2024년 우수고객', '신규 계약', '주소 변경', '등급 상향']
    }
    
    df = pd.DataFrame(data)
    df.to_excel('customer_update.xlsx', index=False, sheet_name='고객목록')
    print("[OK] customer_update.xlsx created")

if __name__ == "__main__":
    # 테스트 데이터 디렉토리로 이동
    import os
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # 모든 테스트 데이터 생성
    create_healthcare_checkup_data()
    create_prescription_data()
    create_approval_data()
    create_customer_update_data()
    
    print("\nAll test data files created successfully!")