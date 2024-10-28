import pandas as pd
import openpyxl
from pprint import pprint

def main(path):
    df = pd.read_excel(path, engine='openpyxl', header=1)
    print(f"{df}\n")
    
    read_column = [2,4,7,18]
    액티비티 = read_column[0]
    자재코드 = read_column[1]
    BOM수량 = read_column[2]
    납품예약번호 = read_column[3]
    
    액티비티_시리즈 = df.iloc[:, 액티비티].astype(str).apply(str.strip).tolist()
    자재코드_시리즈 = df.iloc[:, 자재코드].astype(str).apply(str.strip).tolist()
    BOM수량_시리즈 = df.iloc[:, BOM수량].astype(str).apply(str.strip).tolist()
    납품예약번호_시리즈 = df.iloc[:, 납품예약번호].astype(str).apply(str.strip).tolist()

    인덱스 = df.index.tolist()
    print(f"인덱스: {인덱스}\n")
    
    combined_data = list(zip(인덱스, 액티비티_시리즈, 자재코드_시리즈, BOM수량_시리즈, 납품예약번호_시리즈))
    print(f"combined_data: {combined_data}\n")
    
    
    # 납품예약번호가 'nan' 이거나 빈 문자열인 경우만 필터링
    filtered_data = [(idx, act, mat, bom) 
                    for idx, act, mat, bom, del_num in combined_data 
                    if del_num.lower() == 'nan' or del_num == '']
    
    pprint(f"filtered_data: \n {filtered_data}")
    
    return filtered_data
    
if __name__ == "__main__":
    path = r'C:\Users\123\Desktop\test\직납_직사급_Pallet_관리_20240828_171355.xlsx'
    main(path)