import pandas as pd
import numpy as np

# 엑셀 파일 읽기
성공case_1 =  r"C:\Users\123\Desktop\일반납품예약\성공\P12XA03905.xlsx"  # 실제 파일 경로로 변경하세요

실패case_1 = r"C:\Users\123\Desktop\일반납품예약\실패\P12XA03281.xlsx"
실패case_2 = r"C:\Users\123\Desktop\일반납품예약\실패\P13PA00030.xlsx"

실패case_3 = r"C:\Users\123\Desktop\일반납품예약\실패\P13PA00086.xlsx"

df = pd.read_excel(실패case_3, header=0, engine='openpyxl')
print(f"모든 데이터: {df}")

# P/O품번, 납품예약불가사유, 납품예약번호 열을 문자열로 변환
part_po_row = df.iloc[:, 0]  # po품번을 문자열로 변환
cause_row = df.iloc[:, 3]  # 납품예약불가사유를 문자열로 변환
reserv_num_row = df.iloc[:, 10] # 납품예약번호를 문자열로 변환


condition = (
    (cause_row.isnull()) |  # NaN, None 값 확인
    (cause_row == '')  # 빈 문자열 확인
)

# condition = (
#     cause_row.isnull() & reserv_num_row.isnull()
# )

excel_data = part_po_row[condition]
print(f'excel_data: \n {excel_data}')



# print(f'cause_row type: {cause_row.isnull()} {cause_row.dtype}')
# print(f'reserv_num_row type: {reserv_num_row.dtype}')

# # cause_row 조건 설정
# condition = (
#     (cause_row.isnull()) |  # NaN, None 값 확인
#     (cause_row == '') |  # 빈 문자열 확인
#     (cause_row.str.isspace()) |  # 공백 문자열 확인
#     (cause_row.isin(['-', 'N/A']))  # 특수문자 '-', 'N/A' 확인
# )

# # reserv_num_row 조건 설정
# reserv_condition = (
#     (reserv_num_row.isnull()) |  # NaN, None 값 확인
#     (reserv_num_row == '') |  # 빈 문자열 확인
#     (reserv_num_row.str.isspace())  # 공백 문자열 확인
# )

# # 조건을 만족하는 P/O품번 추출
# excel_data = part_po_row[condition & reserv_condition]

# print(f"excel_data: \n{excel_data}")



# # P/O품번, 납품예약불가사유 열 데이터 선택
# part_po_row = df.iloc[:, 0] # po품번
# cause_row = df.iloc[:, 3] # 납품예약불가사유
# reserv_num_row = df.iloc[:, 10] # 납품예약번호

# condition = (
#     (cause_row.isnull()) | # NaN, None 값 확인
#     (cause_row == '') |  # 빈 문자열 확인
#     (cause_row.str.isspace()) | # 공백 문자열 확인
#     (cause_row.isin(['-','N/A'])) # 특수문자 '-', 'N/A' 확인
# )

# reserv_condition = (
#     (reserv_num_row.isnull()) | # NaN, None 값 확인
#     (reserv_num_row == '') |  # 빈 문자열 확인
#     (reserv_num_row.str.isspace()) # 공백 문자열 확인
# )

# excel_data = part_po_row[condition & reserv_condition]

# print(f"excel_data: \n {excel_data}")



# combined_condition  = (
#     ((cause_row.isnull()) | (cause_row.astype(str) == '') | (cause_row.astype(str).apply(lambda x: x.isspace()))) &
#     ((reserv_num_row.isnull()) | (reserv_num_row.astype(str) == '') | (reserv_num_row.astype(str).apply(lambda x: x.isspace())))
# )

# # 두 조건을 모두 충족하는 품번 데이터 추출
# excel_data = part_po_row[combined_condition]

# print(f">>>>>>>>> 납품예약불가사유, 납품예약번호가 없는 p/o 품번: \n\n {excel_data} \n\n")

# # 중복된 품번 제거 (인덱스가 낮은 첫 번째 p/o 번호만 남김)
# excel_data_unique = excel_data.drop_duplicates(keep='first')

# print(f">>>>>>>>> 납품예약불가사유, 납품예약번호가 없는 중복 제거된 p/o 품번: \n\n {excel_data_unique}")







# 데이터 정제
# df = df.replace(['', ' ', np.nan], np.nan)  # 빈 문자열과 공백을 NaN으로 변환
# df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)  # 문자열 앞뒤 공백 제거

# # 빈 값이 있는 행 찾기
# empty_rows = df[df.isnull().any(axis=1)]

# # 결과 출력
# print(f"전체 행 수: {len(df)}")
# print(f"빈 값이 있는 행 수: {len(empty_rows)}")

# # 빈 값이 있는 행의 데이터 출력
# print("\n빈 값이 있는 행의 데이터:")
# pd.set_option('display.max_columns', None)  # 모든 열 표시
# pd.set_option('display.width', None)  # 행 너비 제한 해제
# print(empty_rows)

# # 특정 행의 데이터를 자세히 보기
# def view_row_details(row_index):
#     print(f"\n{row_index}번 행의 상세 데이터:")
#     row_data = empty_rows.loc[row_index]
#     for column, value in row_data.items():
#         print(f"{column}: {value}")

# # 예시: 첫 번째 빈 값이 있는 행의 상세 데이터 보기
# if not empty_rows.empty:
#     first_empty_row_index = empty_rows.index[0]
#     view_row_details(first_empty_row_index)

# # 사용자 입력으로 특정 행 보기
# while True:
#     user_input = input("\n상세히 볼 행의 인덱스를 입력하세요 (종료하려면 'q' 입력): ")
#     if user_input.lower() == 'q':
#         break
#     try:
#         row_index = int(user_input)
#         if row_index in empty_rows.index:
#             view_row_details(row_index)
#         else:
#             print("해당 인덱스는 빈 값이 있는 행이 아닙니다.")
#     except ValueError:
#         print("유효한 숫자를 입력하세요.")