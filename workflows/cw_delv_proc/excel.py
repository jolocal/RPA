import pandas as pd

# 엑셀 파일 경로
file_path = r'C:\work\RPA_python3.7_20240824\reports\직납직사급\일반 납품예약.xlsx'

# 엑셀 파일 읽기
df = pd.read_excel(file_path, header=None, engine='openpyxl')


# 열 이름 출력
print(df.head())