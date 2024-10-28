import pandas as pd
import logging

class TestStep:
    def __init__(self, part_no, read_column):
        self.part_no = part_no
        self.read_column = read_column

class TestRPA:
    def __init__(self, filepath):
        self.filepath = filepath
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)

    def read_column_data(self, step_num, step):
        df = pd.read_excel(self.filepath, engine='openpyxl')
        column_data = df.iloc[:, step.read_column].tolist()
        return list(enumerate(column_data))  # 인덱스와 값을 함께 반환

    def find_matching_rows(self, step_num, step):
        try: 
            self.logger.info(f"Step {step_num}: Starting 'find_matching_rows'.")

            row_json_po_list = step.part_no
            self.logger.debug(f"Step {step_num}: 최초 json_po_list : {row_json_po_list}")
            
            json_po_list = list(dict.fromkeys(row_json_po_list))
            self.logger.debug(f"Step {step_num}: 중복 제거 json_po_list : {json_po_list}")
            
            json_po_list = [str(item).strip() for item in json_po_list]
            self.logger.debug(f"Step {step_num}: json_list (P/O품번) : {json_po_list}")
            
            excel_po_list = self.read_column_data(step_num, step)
            self.logger.debug(f"Step {step_num}: excel 'P/O품번' index {step.read_column} list : {excel_po_list}")
            
            matches = [(index, value) for index, value in excel_po_list if str(value) in json_po_list]
            
            if not matches:
                self.logger.warning(f"Step {step_num}: No matching items found in column '{step.read_column}'.")
                return False, f"Step {step_num}: No matching items found in column '{step.read_column}'."

            df_matches = pd.DataFrame(matches, columns=['index', 'value'])
            unique_matches = df_matches.drop_duplicates(subset='value', keep='last')
            final_matches = list(unique_matches.itertuples(index=False, name=None))

            self.logger.info(f"Step {step_num}: Found {len(final_matches)} unique matching items: {final_matches}")
            self.matches = final_matches

            return True, f"'find_matching_rows' completed successfully. Found {len(final_matches)} unique matching rows."
            
        except Exception as e:
            error_message = f"Step {step_num}: find_matching_rows failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message

# 테스트 실행
if __name__ == "__main__":
    # 테스트용 엑셀 파일 경로
    excel_path = r"C:\Users\123\Desktop\P12XA03903.xlsx"
    
    # 테스트용 JSON 품번 리스트
    test_json_list = ["250", "250", "260", "260", "330", "340", "910"]
    
    # TestRPA 인스턼스 생성
    test_rpa = TestRPA(excel_path)
    
    # TestStep 인스턴스 생성 (read_column은 P/O품번이 있는 열의 인덱스로 설정, 여기서는 8)
    test_step = TestStep(test_json_list, read_column=8)
    
    # find_matching_rows 메서드 테스트
    success, message = test_rpa.find_matching_rows(1, test_step)
    
    print(f"Test result: {'Success' if success else 'Failure'}")
    print(f"Message: {message}")
    if success:
        print(f"Matches found: {test_rpa.matches}")