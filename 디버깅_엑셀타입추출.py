import pandas as pd
import openpyxl
from pprint import pprint

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
일반납품예약2 = r"C:\work\RPA_python3.7_20240824\reports\일반납품예약\일반 납품예약_20240903_134605..xlsx"


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
print(df)

read_columns = [0,3,12]

part_po_idx = read_columns[0]
cause_idx = read_columns[1]

# part_po_list = df.iloc[:, part_po_idx]
# cause_list = df.iloc[:, cause_idx]

# # NaN, 빈문자열, 공백 문자열, None, 특수 문자가 있는 행 필터링
# condition = (
#     (cause_list.isnull()) | # NaN, None 값 확인
#     (cause_list == '') |  # 빈 문자열 확인
#     (cause_list.str.isspace()) | # 공백 문자열 확인
#     (cause_list.isin(['-','N/A'])) # 특수문자 '-', 'N/A' 확인

# )
# excel_data = part_po_list[condition]
# print(f'[excel_data] : \n {excel_data}')
# print(f'\n')

# # 문자열로 변환, 공백 제거
# filtered_data = excel_data.astype(str).str.strip()
# print(f'[filtered_data] : \n {filtered_data}')
# print(f'\n')


# # matches = [ (index,value) for index,value in filtered_data.items() if value in json_list ]
# # print(f'{matches}')
# # print(f'\n')

# # po_data_list - JSON 형태의 데이터 (구조: [품번, 자재번호, bom 수량])
# po_data_list = [ 
#     ["10","SN2655HB200PUUF300",6],
#     ["1,030","SN2655HB200SUUF300",6],
#     ["750","SN2655HF513PUUF200",1],
# ]

# results = []
# for index,value in filtered_data.items():
#     for json_data in po_data_list:
#         part_po = json_data[0]
#         bom_quantity = json_data[2]
#         if value == part_po:
#             results.append((index, part_po, bom_quantity))
            
# print(results)

# matches = [ (index,value) for index,value in excel_data.items() if value in json_list ]

# # matches = excel_data[excel_data.isin(json_list)]
# print(f'{matches}')
# print(f'\n')

# excel_data_list = excel_data.astype(str).tolist()



# print(excel_data_list)

# for index, value in enumerate(excel_data):
#     print(f'{index}: {value}')
# print('\n')

# matches =  [(index,value) for index, value in enumerate(part_po_list) if pd.isnull(cause_list[index])]


# part_po_list = df.iloc[:, part_po_idx].tolist()
# print(f"part_po_list(total: {len(part_po_list)}/type: {type(part_po_list)}): \n")
# for idx, value in enumerate(part_po_list):
#     print(f"{idx}: {value}")
# print("\n")

# cause_list = df.iloc[:, cause_idx].astype(str).tolist()
# print(f"cause_list(total: {len(cause_list)}/type: {type(cause_list)}): \n")
# for idx, value in enumerate(cause_list):
#     print(f"{idx}: {value}")
# print("\n")

# real_cause_list = [ item.strip() for item in cause_list ]
# print(f"real_cause_list(total: {len(real_cause_list)}/type: {type(real_cause_list)}): \n")
# for idx, value in enumerate(real_cause_list):
#     print(f"{idx}: {value}")



# pprint 사용 예시 (리스트 전체 출력 시 가독성 향상)
# print("Pretty Printed part_po_list:")
# pprint(part_po_list)
# print("\nPretty Printed cause_list:")
# pprint(cause_list)

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
