import pandas as pd

#! 엑셀 파일의 특정 열 데이터 읽기

납품예약리스트_path = r'C:\work\납품예약리스트\납품예약_리스트(24.09.09).xlsx'
# 성공
P12XA03902 = r'C:\work\오류\script3_matching_data\P12XA03902_변경납기관리_20240912_175121.xlsx' # str

# 실패
P13PA00029 = r'C:\work\오류\script3_matching_data\P13PA00029_변경납기관리_20240912_173304.xlsx' # numpy.int64
P13PA00030 = r'C:\work\오류\script3_matching_data\P13PA00030_변경납기관리_20240912_173554.xlsx' # numpy.int64


P12XA03901 = r'C:\work\RPA_python3.7_20240824\reports\변경납기관리\변경납기관리_20240909_164620.xlsx'
ex = r'C:\work\RPA_python3.7_20240824\reports\변경납기관리\직납_직사급_Pallet_관리_20240829_204930.xlsx'

일반납품예약 = r'C:\work\RPA_python3.7_20240824\reports\일반납품예약\일반 납품예약_20240902_162150..xlsx'
일반납품예약2 = r'C:\work\RPA_python3.7_20240824\reports\일반납품예약\일반 납품예약_20240902_162606..xlsx'


#TODO SCRIPT_3
# df = pd.read_excel(P12XA03901, engine='openpyxl', sheet_name=0, header=0 )

#? 모든 컬럼 출력하기
# print(df)
# columns = df.columns
# print(f"모든 컬럼: {columns}")

#? 엑셀 데이터 출력 갯수 확인
# read_column = 8
# po_data = df.iloc[:, read_column].tolist()

# print(f"po_data(total:{len(po_data)}/type:{type(po_data)}): \n {po_data}")


#? 엑셀 데이터 타입 확인
# po_data_str = df['P/O\n품번'].astype(str)
# print(f"문자열로 변환된 P/O 품번 데이터: \n {po_data_str}")

# # 양쪽 공백 제거
# normalized_data = [ item.strip() for item in po_data_str ]

# for i in normalized_data:
#     print(f"po 데이터: [{i}] / 데이터 타입: {type(i)}")

#TODO SCRIPT_4 
df = pd.read_excel(일반납품예약2, engine='openpyxl', sheet_name=0, header=0)
read_columns = [0,3,12]

part_po_idx = read_columns[0]
cause_idx = read_columns[1]

part_po_list = df.iloc[:, part_po_idx].tolist()
print(f"part_po_list(total:{len(part_po_list)}/type:{type(part_po_list)}): \n {part_po_list}")


# po_data = df['P/O\n품번']
# print(f"P/O품번 데이터: \n {po_data}")

# for i in range(len(po_data)):
#     po = po_data.iloc[i]
#     print(f"po 데이터: {po} / 데이터 타입: {type(po)}")

# print(type(po_data))
# print(po_data.dtype)

# # 'P/O\n품번' 열의 12번째 데이터 타입 확인
# if len(po_data) > 12:  # 데이터가 충분히 있는지 확인
#     twelfth_element = po_data.iloc[12]
#     print(f"12번째 데이터: {twelfth_element}")
#     print(f"12번째 데이터의 타입: {type(twelfth_element)}")
# else:
#     print("데이터가 충분하지 않습니다.")
