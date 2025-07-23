"""Create a test Excel file for verification"""

import pandas as pd

# Create test data matching the screenshot
test_data = {
    '직업번호': ['P2024001', 'P2024002', 'P2024003', 'P2024004', 'P2024005'],
    '환자명': ['홍길동', '김철수', '이영희', '박민수', '최지우'],
    '병적번호': ['MR001', 'X-Ray', 'MR002', 'CT001', 'CT002'],
    '검사항목': ['혈액검사', '흉부검사', '혈액검사', '혈액검사', '흉부검사'],
    '검사일자': ['2024-01-10', '2024-01-11', '2024-01-12', '2024-01-13', '2024-01-14'],
    '상태': ['미완료', '미완료', '미완료', '미완료', '미완료']
}

df = pd.DataFrame(test_data)
output_file = 'test_data_with_status.xlsx'

# Save to Excel
df.to_excel(output_file, index=False, sheet_name='검사목록')

print(f"Test Excel file created: {output_file}")
print(f"Please load this file in the application to test the status column functionality.")
print(f"\nExpected behavior:")
print(f"1. The existing '상태' column should be renamed to '매크로_상태'")
print(f"2. All rows should show '미완료' status")
print(f"3. '모두 미완료' button should work without errors")
print(f"4. Clicking on status cells should toggle between states")