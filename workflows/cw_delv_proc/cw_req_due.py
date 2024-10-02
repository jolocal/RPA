""" po번호 검색(for문) 납기 변경 요청 스크립트 """
import os
import sys
from dataclasses import dataclass, field
from typing import List, Tuple, Dict
import traceback
import json
import time
import pyautogui
import pyperclip
import pandas as pd 

import keyboard
import threading

import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

sys.path.append(r"C:\work\RPA_python3.7_20240824\src\workflows\cw_delv_proc")

# 루트 디렉토리 경로 설정
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),'../../'))
sys.path.append(root_dir)

# 절대 경로를 사용하여 모듈을 불러옴
from common.loading_manager import LoadingIconManager
from common.logger_manager import LoggerManager
from common.response_manager import ResponseManager
from common.utils.helper import PyAutoGuiHelper
from common.utils.path_utils import PathHelper
from common.ocr_popup_manager import PopupManager

@dataclass
class Step:
    task: str = ""
    po_no: str = "" # step_1
    nego_due: str ="" # step_6
    search_str: str ="" #step_1
    comment_str: str = "" #step_7
    
    # step_1
    pos_global_search_input: Tuple[int, int] = (0,0)
    pos_deliv_res: Tuple[int, int] = (0,0)
    pos_vali_1: Tuple[int, int] = (0,0)
    
    # step_2
    pos_po_no: Tuple[int, int] = (0,0)
    pos_search_btn_1: Tuple[int, int] = (0,0)
    pos_change_due_date_mng: Tuple[int, int] = (0,0)
    pos_popup_confirm_btn_1: Tuple[int, int] = (0,0)
    pos_vali_2: Tuple[int, int] = (0,0)
    
    # step_3
    pos_search_btn_2: Tuple[int, int] = (0,0)
    pos_vali_3: Tuple[int, int] = (0,0)
    
    # step_4
    pos_excel_icon: Tuple[int, int] = (0,0)
    pos_excel_save: Tuple[int, int] = (0,0)
    
    # step_5
    part_no: List[Dict[str, str]] = field(default_factory=list)
    read_column: int = 0

    # step_6
    pos_start: Tuple[int, int] = (0,0)

    # step_7
    pos_nego_due: Tuple[int, int] = (0,0)
    pos_confirm_btn: Tuple[int, int] = (0,0)
    
    # step_8
    pos_comment: Tuple[int, int] = (0,0)
    pos_copy_select_btn: Tuple[int, int] = (0,0)
    pos_batch_input_btn: Tuple[int, int] = (0,0)
    
    # step_9
    pos_approve_btn: Tuple[int, int] = (0,0)
    
    # step_10
    pos_window_focus: Tuple[int, int] = (0,0)
    pos_menu_tab: Tuple[int, int] = (0,0)

@dataclass
class Contexts:
    step_1: Step
    step_2: Step
    step_3: Step
    step_4: Step
    step_5: Step
    step_6: Step
    step_7: Step
    step_8: Step
    step_9: Step
    step_10: Step

class CW_ReqDueManager:
    def __init__(self, json_data:str, res, logger, loading, master_mode:bool = False):
        # JSON 문자열에서 백슬래시 문자를 두 번으로 바꿉니다.
        json_data = json_data.replace('\\', '\\\\')
        self.data = json.loads(json_data, encoding='utf-8')
        
        # 받은 JSON 데이터를 로그로 남깁니다.
        logger.info("Received JSON data:")
        logger.info(json.dumps(self.data, indent=4, ensure_ascii=False))  # 보기 좋게 출력, ensure_ascii=False로 한글이 깨지지 않도록
        
        self.res = res
        self.logger = logger
        self.loading = loading
        
        self.po_no = None
        self.filepath = ""
        self.matches = None 
        
        self.master_mode = master_mode
        print(f"master_mode in StartApp: {self.master_mode}")
        logger.debug(f"master_mode in StartApp: {self.master_mode}")
        
        # JSON 데이터를 Contexts 객체로 변환
        self.contexts = Contexts(
            step_1 = Step(**self.data['contexts']['step_1']),
            step_2 = Step(**self.data['contexts']['step_2']),
            step_3 = Step(**self.data['contexts']['step_3']),
            step_4 = Step(**self.data['contexts']['step_4']),
            step_5 = Step(**self.data['contexts']['step_5']),
            step_6 = Step(**self.data['contexts']['step_6']),
            step_7 = Step(**self.data['contexts']['step_7']),
            step_8 = Step(**self.data['contexts']['step_8']),
            step_9 = Step(**self.data['contexts']['step_9']),
            step_10 = Step(**self.data['contexts']['step_10'])
        )
        
    
    def execute_task(self, step_num, step:Step):
        task_map = {
            "navigate_to_deliv_reserv_improv": self.navigate_to_deliv_reserv_improv,
            "navigate_to_deliv_mng": self.navigate_to_deliv_mng,
            "load_data_table": self.load_data_table,
            "save_and_read_excel_data": self.save_and_read_excel_data,
            "find_matching_rows": self.find_matching_rows,
            "navigate_to_matching_rows": self.navigate_to_matching_rows,
            "input_negotiation_date": self.input_negotiation_date,
            "input_incoming_goods_info": self.input_incoming_goods_info,
            "approve_changes": self.approve_changes,
            "reset_for_po_number_search": self.reset_for_po_number_search
        }

        try:
            if step.task in task_map:
                success, message =  task_map[step.task](step_num, step)
                
                if success:
                    self.res.add_contexts(step_num, step.task, "success", f"{step.task} executed successfully.")
                else:
                    # 실패 시 결과를 기록하고 반환
                    self.res.add_contexts(step_num, step.task, "failed", message)
                    return message  # 실패 메시지를 반환
                
            else:
                raise ValueError(f"Unknown task: {step.task}")
            
        except Exception as e:
            self.handle_task_exception(step_num, step.task, e)
            return str(e)  # 예외 메시지를 반환
        
        return None  # 성공적으로 실행된 경우 None 반환

        
    #TODO################################################# STEP_1 ######################################################
    
    def navigate_to_deliv_reserv_improv(self, step_num, step:Step):
        try:
            self.logger.info(f"Step {step_num}: Starting 'navigate_to_deliv_mng'.")
            time.sleep(3)
            
            # 통합검색 클릭
            PyAutoGuiHelper.perform_click(step.pos_global_search_input) #71,93
            self.logger.info(f"Step {step_num}: '통합 검색' icon clicked at position / pos_global_search_input: {step.pos_global_search_input}.")
            time.sleep(1)
            
            search_str = "개선"
            pyperclip.copy(search_str)
            self.logger.info(f"Step {step_num}: Search term '{search_str}'/'{step.search_str}' copied to clipboard.")
            
            time.sleep(3)
            
            # 입력란 클릭 후 '개선' 입력 및 엔터
            pyautogui.hotkey('ctrl', 'v')
            self.logger.info(f"Step {step_num}: Search term pasted from clipboard.")
            
            time.sleep(1)
            
            pyautogui.press('enter')
            self.logger.info(f"Step {step_num}: 'Enter' key pressed, search initiated.")
            time.sleep(3)
            
            PyAutoGuiHelper.perform_double_click(step.pos_deliv_res) # 902,479
            self.logger.info(f"Step {step_num}: '납품예약(개선)' tab clicked at position / pos_deliv_res: {step.pos_deliv_res}.") 
            
            time.sleep(3)
            success, message = self.detect_loading(step_num, step)
            self.logger.debug(f"Step {step_num}: Loading detect_loading result - success: {success}, message: {message}")  
            if not success:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}: Loading detection failed, \n Waiting for 5 seconds before retry...")
                    time.sleep(5)
                else:
                    return False, message  # 로딩 실패 시 반환
            time.sleep(5)
            
            # 새창 로드 검증  - 주(케이씨)
            PyAutoGuiHelper.perform_double_click(step.pos_vali_1) # 485,198
            self.logger.info(f"Step {step_num}: Validation area double-clicked at position {step.pos_vali_1}.")
            time.sleep(1)  
            
            pyautogui.hotkey('ctrl','c')
            self.logger.info(f"Step {step_num}: Clipboard data copied successfully.")
            time.sleep(1)
            
            # 클립보드에서 데이터 가져오기
            clipboard_data_1 = pyperclip.paste().split('\n')
            self.logger.debug(f"Step {step_num}: Clipboard data read: {clipboard_data_1}.")
            time.sleep(3)   
            
            # "(주)케이씨" 일치하는지 확인
            matched_str_1 = "(주)케이씨" 
            self.logger.debug(f"Step {step_num}: Checking if clipboard data contains the string '{matched_str_1}'.")
            
            if matched_str_1 in clipboard_data_1:
                self.logger.info(f"Step {step_num}: New window loaded successfully and contains '{matched_str_1}'.") 
                return True, "navigate_to_deliv_reserv_improv' completed successfully."
            
            else:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}: New window failed to load correctly. '{matched_str_1}' not found. \n Waiting for 5 seconds before retry...")
                    time.sleep(5)  # 5초 대기   
                    return True, "navigate_to_deliv_reserv_improv' completed successfully."
                else:
                    self.logger.error(f"Step {step_num}: New window failed to load correctly. '{matched_str_1}' not found.")
                    return False, "Failed to load the delivery reservation window"
                
        except Exception as e:
            error_message = f"Step {step_num}: navigate_to_deliv_reserv_improv failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환 
    
    #TODO################################################# STEP_2 ######################################################    
    
    def navigate_to_deliv_mng(self, step_num:int, step:Step):
        try: 
            self.logger.info(f"Step {step_num}: Starting 'search_po_num'.")
            time.sleep(3)
            
            # po_no가 제공되지 않았을 경우 처리
            if not getattr(step, 'po_no', None):
                error_message = f"Step {step_num}: PO 번호 (po_no)가 step 데이터에 없습니다."
                self.logger.error(error_message)
                return False, error_message  # 에러를 반환하고 실행 중단
            
            self.logger.info(f"Step {step_num}: 'search_po_num' 시작.")
            time.sleep(1)
                    
            # po_no가 존재하므로 프로세스를 계속 진행
            self.po_no = step.po_no # po 번호를 인스턴스 변수에 저장
            time.sleep(3)
            
            PyAutoGuiHelper.perform_double_click(step.pos_po_no) #684,198
            self.logger.info(f"Step {step_num}: PO number input field clicked at position {step.pos_po_no}.")
            time.sleep(1)
            
            pyautogui.typewrite(self.po_no) #684,198
            self.logger.info(f"Step {step_num}: PO number '{self.po_no}' entered successfully.")
            time.sleep(1)
            
            # po_no 조회 
            PyAutoGuiHelper.perform_click(step.pos_search_btn_1) # 1083,255
            self.logger.info(f"Step {step_num}: '납품예약 - 조회' clicked at position {step.pos_search_btn_1}.")
            
            time.sleep(3)
            success, message = self.detect_loading(step_num, step)
            self.logger.debug(f"Step {step_num}: Loading detect_loading result - success: {success}, message: {message}")  
            if not success:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}: Loading detection failed, \n Waiting for 5 seconds before retry...")
                    time.sleep(5) 
                else:
                    return False, message  # 로딩 실패 시 반환
            time.sleep(5)
            
            # '변경납기 관리' 클릭
            PyAutoGuiHelper.perform_click(step.pos_change_due_date_mng) # 1833,146
            self.logger.info(f"Step {step_num}: '변경납기 관리' clicked at position {step.pos_change_due_date_mng}.")
            
            time.sleep(1)
            
            # [변경납기관리] 화면으로 이동하시겠습니까?
            PyAutoGuiHelper.perform_click(step.pos_popup_confirm_btn_1) # 1046,600
            self.logger.info(f"Step {step_num}: '[변경납기관리] 화면으로 이동하시겠습니까?' popup clicked '예' at position {step.pos_popup_confirm_btn_1}.")
            
            time.sleep(3)
            success, message = self.detect_loading(step_num, step)
            self.logger.debug(f"Step {step_num}: Loading detect_loading result - success: {success}, message: {message}")  
            if not success:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}: Loading detection failed, \n Waiting for 5 seconds before retry...")
                    time.sleep(5) 
                else:
                    return False, message  # 로딩 실패 시 반환
            time.sleep(5)
            
            ########################################## 새창 로드 검증(2) - P/O 번호 조회 ##########################################
            PyAutoGuiHelper.perform_double_click(step.pos_vali_2) # 1284,158
            self.logger.info(f"Step {step_num}: Validation area double-clicked at position {step.pos_vali_2}.")
            time.sleep(5)  
            
            pyautogui.hotkey('ctrl','c')
            self.logger.info(f"Step {step_num}: Clipboard data copied successfully.")
            time.sleep(1)
            
            # 클립보드에서 데이터 가져오기
            clipboard_data_2 = pyperclip.paste().split('\n')
            self.logger.debug(f"Step {step_num}: Clipboard data read: {clipboard_data_2}.")
            time.sleep(3)   
            
            # PO_NO와 일치하는지 확인
            matched_str_2 = self.po_no  # 인스턴스 변수에 저장된 PO 번호 사용
            self.logger.debug(f"Step {step_num}: Checking if clipboard data contains the string '{self.po_no}'.")
            
            if matched_str_2 in clipboard_data_2:
                self.logger.info(f"Step {step_num}: New window loaded successfully and contains '{matched_str_2}'.")
                return True, "navigate_to_deliv_mng' completed successfully."
            
            else:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}: New window failed to load correctly. '{matched_str_2}' not found. \n Waiting for 5 seconds before retry...")
                    time.sleep(5)  # 5초 대기     
                    return True, "navigate_to_deliv_mng' completed successfully."
                else: 
                    self.logger.error(f"Step {step_num}: New window failed to load correctly. '{matched_str_2}' not found.")
                    return False, "Failed to load the delivery reservation window"
        
        except Exception as e:
            error_message = f"Step {step_num}: navigate_to_deliv_mng failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환


    #TODO################################################# STEP_3 ######################################################
    
    def load_data_table(self, step_num, step:Step):
        """ '조회' 버튼을 클릭하여 데이터 테이블 로드 확인"""
        try: 
            time.sleep(3)
            self.logger.info(f"Step {step_num}: Starting 'load_data_table'.")

            # po_no 조회 
            PyAutoGuiHelper.perform_click(step.pos_search_btn_2) # 1083,255
            self.logger.info(f"Step {step_num}: '변경납기 - 조회' clicked at position {step.pos_search_btn_2}.")
            
            time.sleep(3)
            success, message = self.detect_loading(step_num, step)
            self.logger.debug(f"Step {step_num}: Loading detect_loading result - success: {success}, message: {message}")  
            if not success:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}: Loading detection failed, \n Waiting for 5 seconds before retry...")
                    time.sleep(5)
                else:
                    return False, message
            time.sleep(5)
            
            # 테이블 로드 검증(3) - P/O 번호 조회
            PyAutoGuiHelper.perform_click(step.pos_vali_3) # 751,439
            self.logger.info(f"Step {step_num}: Validation area double-clicked at position {step.pos_vali_3}.")
            time.sleep(1)  
            
            pyautogui.hotkey('ctrl','c')
            self.logger.info(f"Step {step_num}: Clipboard data copied successfully.")
            time.sleep(1)
            
            # 클립보드에서 데이터 가져오기
            clipboard_data_3 = pyperclip.paste()
            self.logger.debug(f"Step {step_num}: Clipboard data read: {clipboard_data_3}.")
            
            time.sleep(3)   
            
            # PO_NO와 일치하는지 확인
            matched_str_3 = self.po_no  # 인스턴스 변수에 저장된 PO 번호 사용
            self.logger.debug(f"Step {step_num}: Checking if clipboard data contains the string '{self.po_no}'.")
            if matched_str_3 in clipboard_data_3:
                self.logger.info(f"Step {step_num}: New window loaded successfully and contains '{matched_str_3}'.")
                return True, "load_data_table' completed successfully."
            
            else:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}: New window failed to load correctly. '{matched_str_3}' not found. \n Waiting for 5 seconds before retry...")
                    time.sleep(5)
                    return True, (f"Step {step_num}: New window failed to load correctly. '{matched_str_3}' not found. \n Waiting for 5 seconds before retry...")
                else:
                    self.logger.error(f"Step {step_num}: New window failed to load correctly. '{matched_str_3}' not found.")
                    return False, "load_data_table failed"
            
        except Exception as e:
            error_message = f"Step {step_num}: load_data_table failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환


    #TODO################################################# STEP_4 ######################################################

    def save_and_read_excel_data(self, step_num, step:Step):
        """ 
        엑셀로 저장 및 읽어오기 
        파일 저장 로직 추가
        """
        # 엑셀 아이콘 클릭 및 저장
        try: 
            time.sleep(3)
            self.logger.info(f"Step {step_num}: Starting 'save_and_excel_data'.")
            
            PyAutoGuiHelper.perform_click(step.pos_excel_icon)
            self.logger.info(f"Step {step_num}: Excel icon clicked successfully at position / pos_excel_icon: {step.pos_excel_icon}.")
            time.sleep(3)   
            
            PyAutoGuiHelper.perform_click(step.pos_excel_save)
            self.logger.info(f"Step {step_num}: Save button clicked successfully at position / pos_excel_save: {step.pos_excel_save}.")
            
            # 로딩
            time.sleep(5)
                
            # [파일 디렉토리+파일이름+날짜+시간] 엑셀 저장
            file_directory = PathHelper.get_abs_path('reports','변경납기관리')
            filename = PyAutoGuiHelper.generate_filename("변경납기관리", "xlsx")
            self.logger.debug(f"Step {step_num}: Generated filename is {filename}.")
            
            time.sleep(1)
            self.filepath = os.path.join(file_directory, filename)
            self.logger.info(f"Step {step_num}: File path constructed: {self.filepath}.")
            
            time.sleep(1)
            PyAutoGuiHelper.save_file_with_name(self.filepath)
            self.logger.info(f"Step {step_num}: Excel file saved successfully as {self.filepath}.")
            
            # 파일 저장중........
            time.sleep(5)   
            self.logger.debug(f"Step {step_num}: Waiting for 3 seconds after saving file.")
            
            # 파일 존재 확인
            success, message = self.check_excel_exists(step_num)
            if not success:
                return False, message
            
            return True, f"Excel data saved and read successfully. File path: {self.filepath}"
            
        except Exception as e:
            error_message = f"Step {step_num}: save_and_read_excel_data failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환

    def check_excel_exists(self, step_num):
        try: 
            time.sleep(3)
            self.logger.info(f"Step {step_num}: Starting 'check_excel_exists'.")
            
            if not os.path.exists(self.filepath):
                time.sleep(1) 
                self.logger.error(f"Step {step_num}: Excel file not found at: {self.filepath}")
                return False, f"Excel file not found at: {self.filepath}"

            self.logger.info(f"Step {step_num}: Excel file confirmed to exist at: {self.filepath}.")
            
            return True, "Excel file exists."
        
        except Exception as e:
            error_message = f"Step {step_num}: check_excel_exists failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환

    #TODO################################################# STEP_5 ######################################################
    
    def find_matching_rows(self, step_num, step:Step):
        try: 
            time.sleep(3)
            self.logger.info(f"Step {step_num}: Starting 'find_matching_rows'.")

            # JSON 품번 리스트 가져옴
            row_json_po_list = step.part_no #["품번1","품번2"...]
            self.logger.debug(f"Step {step_num}: 최초 json_po_list : {row_json_po_list}")
            
            json_po_list = list(dict.fromkeys(row_json_po_list))
            self.logger.debug(f"Step {step_num}: 중복 제거 json_po_list : {json_po_list}")
            
            #? 데이터 정규화 및 검증
            # 1. 양쪽 공백 제거
            json_po_list = [ item.strip() for item in json_po_list ]
            self.logger.debug(f"Step {step_num}: json_list (P/O품번) : {json_po_list}")
            
            time.sleep(1)
            
            # 엑셀 열 데이터 읽기
            excel_po_list = self.read_column_data(step_num, step)
            self.logger.debug(f"Step {step_num}: excel 'P/O품번' index {step.read_column} list : {excel_po_list}")
            
            # 일치하는 데이터와 그 인덱스 찾기
            #? excel_po_list의 각 항목이 json_po_list에 있는지 확인하며, 인덱스와 값을 튜플로 저장함
            #? json_po_list에 중복된 값이 있어도 excel_po_list의 항목이 json_po_list에 있는지만 확인하기 때문에, JSON 리스트의 중복은 매칭에 영향을 주지 않음.
            #? 즉 JSON리스트의 중복된 항목 수와 상관없이 Excel 값이 json_po_list에 포함되는지만 따짐
            matches = [(index, value) for index, value in enumerate(excel_po_list) if value in json_po_list ]
            
            if not matches:
                self.logger.warning(f"Step {step_num}: No matching items found in column '{step.read_column}'.")
                return False, f"Step {step_num}: No matching items found in column '{step.read_column}'."

            self.logger.info(f"Step {step_num}: Found {len(matches)} matching items: {matches}")
            self.matches = matches # 튜플들의 리스트 형태 matches = [(index_1, value_1), (index_2, value_2), (index_3, value_3), ...]
            
            return True, f"'find_matching_rows' completed successfully. Found {len(matches)} matching rows."
            
        except Exception as e:
            error_message = f"Step {step_num}: find_matching_rows failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환

            
    def read_column_data(self, step_num:int, step:Step):
        try: 
            time.sleep(3)
            self.logger.info(f"Step {step_num}: Starting 'read_column_data'.")
            self.logger.info(f"Step {step_num}: Reading Excel file from {self.filepath}")

            df = pd.read_excel(self.filepath, header=0, engine='openpyxl')
            self.logger.debug(f"Step {step_num}: Excel file loaded into DataFrame.")
            time.sleep(3)
        
            #? read_column 타입 확인하기
            self.logger.debug(f"Type of step.read_column: {type(step.read_column)}")
            
            #? 열 인덱스가 데이터프레임의 열 범위 내에 있는지 확인
            if step.read_column < 0 or step.read_column >= len(df.columns):
                self.logger.error(f"Step {step_num}: Column index {step.read_column} is out of range.")
                return False, f"Step {step_num}: Column index {step.read_column} is out of range."
            
            self.logger.info(f"Step {step_num}: 'P/O품번' Column index '{step.read_column}' found in the DataFrame.")
            
            #? 열 데이터 추출 후 문자열로 변환
            column_data = df.iloc[:, step.read_column].astype(str).tolist() # iloc: pandas의 인덱싱 함수로, 위치 기반 인덱싱
            
            #? 데이터 정규화 및 검증
            # 1. 양쪽 공백 제거
            column_data = [ item.strip() for item in column_data ]
            
            self.logger.info(f"Step {step_num}: Extracted a total of {len(column_data)} entries from column 'P/O품번' (index {step.read_column}).")
            
            time.sleep(1)
            
            #? 최종 데이터 반환
            return column_data # 리스트 형식
        
        except Exception as e:
            error_message = f"Step {step_num}: read_column_data failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환

    #TODO################################################# STEP_6 ######################################################    
    
    def navigate_to_matching_rows(self, step_num, step:Step):
        """ 데이터 테이블에서 매칭된 행으로 이동하고 체크박스 선택 """
    
        try: 
            time.sleep(3)   
            self.logger.info(f"Step {step_num}: Starting 'navigate_to_matching_rows'.") 

            current_index = 0 # 초기 위치(클릭 후 이동하기 전의 인덱스)
            
            PyAutoGuiHelper.perform_click(step.pos_start) # 시작위치로 이동 840,440
            self.logger.info(f"Step {step_num}: Move to start position at {step.pos_start}.")
            
            time.sleep(1)
            
            for idx, (target_index, value) in enumerate(self.matches):
                self.logger.debug(f"Step {step_num}: Processing tuple {idx + 1}/{len(self.matches)}: Target Index = {target_index}, Value = {value}")
                
                # 이동할 칸 수를 계산해서 (현재 인덱스에서 목표 인덱스까지) 방향키로 이동
                self.logger.info(f"Step {step_num}: Moving to index {target_index} from index {current_index}")
                PyAutoGuiHelper.move_to_index(current_index, target_index)

                # 첫 번째 튜플일 때만 shift+tab
                if idx == 0:
                    self.logger.info(f"Step {step_num}: Pressing shift+tab for the first tuple")
                    pyautogui.hotkey('shift', 'tab')
                    time.sleep(1)
                
                # 체크박스 체크
                self.logger.info(f"Step {step_num}: Pressing space to check checkbox at index {target_index}")                
                pyautogui.press('space')
                time.sleep(1)
                self.logger.info(f"Step {step_num}: Checkbox checked at index {target_index} (Value: {value})")
                
                # 현재 인덱스 업데이트
                self.logger.info(f"Step {step_num}: Updating current index to {target_index}")
                current_index = target_index
                
                time.sleep(1)
                
            # 체크박스 일괄 체크 완료
            self.logger.info(f"Step {step_num}: Action performed on all {self.matches} targets checked successfully.")
            return True, "navigate_to_matching_rows' completed successfully."
        
        except Exception as e:
            error_message = f"Step {step_num}: navigate_to_matching_rows failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환


    #TODO################################################# STEP_7 ######################################################  
    
    def input_negotiation_date(self, step_num, step:Step):
        """ 협의중납기일 입력 및 일괄입력 버튼 클릭 """
        try: 
            time.sleep(3)
            self.logger.debug(f"Step {step_num}: Starting 'input_negotiation_date'.")
            
            # 협의중 납기일' 클릭 및 입력
            PyAutoGuiHelper.perform_double_click(step.pos_nego_due) #384,343
            self.logger.info(f"Step {step_num}: Clicking '협의중 납기일' input at position {step.pos_nego_due}. / pos_nego_due: {step.pos_nego_due}")
            time.sleep(1)
            
            self.logger.info(f"Step {step_num}: Typing negotiation due date: {step.nego_due}.")
            pyautogui.typewrite(step.nego_due)
            time.sleep(3)
            
            #일괄입력 클릭
            pyautogui.press('enter')
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(1)
            
            
            success_texts = ["반영","되었습니다."] # 일괄입력 단어 실패 팝업창에도 나타남.
            
            success, detected_text = PopupManager.process_popup(
                success_texts,
                'batch_input', # popup_type
            )
            
            time.sleep(1)
            
            if success:
                self.logger.debug(f"Step {step_num}: process '일괄반영' popup result - success: {success}, detected_text: {detected_text}")   
                PyAutoGuiHelper.perform_click(step.pos_confirm_btn)
                self.logger.info(f"Step {step_num}: Clicking '일괄입력 반영 되었습니다.' button at position {step.pos_confirm_btn}. / pos_confirm_btn: {step.pos_confirm_btn}")
            else:
                self.logger.debug(f"Step {step_num}: Failed to process popup. Last detected text: '{detected_text.strip()}'.")
                return False, f"Failed to process '일괄반영'popup. Last detected text: '{detected_text.strip()}'."

            time.sleep(3)
            success, message = self.detect_loading(step_num, step)
            if not success:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}: Loading detection failed, \n Waiting for 5 seconds before retry...")
                    time.sleep(15)
                    return True, "Negotiation date input and bulk input click completed successfully."
                else:
                    return False, message
            time.sleep(3)
            
            self.logger.info(f"Step {step_num}: Negotiation date input and bulk input click completed successfully.")
            return True, "Negotiation date input and bulk input click completed successfully."
            
        except Exception as e:
            error_message = f"Step {step_num}: input_negotiation_date failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환

        
        #TODO################################################# STEP_8 ###################################################### 

    def input_incoming_goods_info(self, step_num, step:Step):
        """ 물품입고예정 입력 및 선택복사 버튼 클릭 """
        try:
            time.sleep(3) 
            self.logger.info(f"Step {step_num}: Starting 'input_incoming_goods_info'.") 
            
            # "물품입고예정" 입력란 클릭
            PyAutoGuiHelper.perform_double_click(step.pos_comment)
            self.logger.info(f"Step {step_num}: Clicking 'COMMENT' input at position {step.pos_comment}. / pos_comment: {step.pos_comment}")
            time.sleep(1)

            # search_str을 유니코드에서 UTF-8로 처리하여 한글 입력
            comment_str = "물품 입고 예정"
            # 클립보드에 comment_str 복사
            pyperclip.copy(comment_str)
            self.logger.info(f"Step {step_num}: Search term '{comment_str}'/'{step.comment_str}' copied to clipboard.")
            time.sleep(3)

            pyautogui.hotkey('ctrl', 'v')
            self.logger.info(f"Step {step_num}: Search term pasted from clipboard.")
            time.sleep(1)
            
            pyautogui.press('enter')
            self.logger.info(f"Step {step_num}: 'Enter' key pressed, search initiated.")
            time.sleep(3)

            # 선택복사 버튼 클릭
            PyAutoGuiHelper.perform_click(step.pos_copy_select_btn)
            time.sleep(1)
            
            self.logger.info(f"Step {step_num}: Clicking '선택복사' btn at position {step.pos_copy_select_btn}. / pos_copy_select_btn: {step.pos_copy_select_btn}")
            return True, "input_incoming_goods_info completed successfully."
        
        except Exception as e:
            error_message = f"Step {step_num}: input_incoming_goods_info failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환

        #TODO################################################# STEP_9 ######################################################  
        
    def approve_changes(self, step_num, step:Step):
        try: 
            time.sleep(3)
            self.logger.info(f"Step {step_num}: Starting 'approve_changes'.")     
            
            # 변경승인 버튼 클릭
            time.sleep(5)
            PyAutoGuiHelper.perform_click(step.pos_approve_btn)
            self.logger.info(f"Step {step_num}: Clicking '변경승인' popup at position {step.pos_approve_btn}. / pos_approve_btn: {step.pos_approve_btn}")
            
            time.sleep(3)
            # ~건에 대하여 SHI담당자에게 납기변경요청을 하시겠습니까?
            PyAutoGuiHelper.perform_click((1044,596))
            self.logger.info(f"Step {step_num}: Clicking '납기변경요청을 하시겠습니까?' popup at position [876,1058].")
            time.sleep(3)
            
            # 저장이 완료되었습니다.
            PyAutoGuiHelper.perform_click((1072,606))
            self.logger.info(f"Step {step_num}: Clicking '저장이 완료되었습니다.' popup at position [847,1065].")

            time.sleep(3)

            return True, "approve_changes completed successfully."
            
        except Exception as e:
            error_message = f"Step {step_num}: approve_changes failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환
            
    #TODO################################################# STEP_10 ######################################################  
    
    def reset_for_po_number_search(self, step_num:int, step:Step):
        try: 
            time.sleep(3)
            self.logger.info(f"Step {step_num}: Starting 'reset_for_po_number_search'.")
            
            # 현재 창 포커스
            pyautogui.click(step.pos_window_focus)
            self.logger.info(f"Step {step_num}: Clicking 'pos_window_focus' input at position {step.pos_window_focus}. / pos_window_focus: {step.pos_window_focus}")
            time.sleep(1)
            
            # 현재 창 닫기
            for i in range(2):
                self.logger.debug(f"Step {step_num}: Pressing 'alt + x' to close all windows. (Attempt {i+1})")
                pyautogui.hotkey('alt','x', interval=1)
                
            self.logger.info(f"Step {step_num}: Finished pressing 'alt + x' {i+1} times.")

            time.sleep(1)
            
            # 상위 메뉴 탭 모두 닫기
            PyAutoGuiHelper.perform_click(step.pos_menu_tab) # 214,95
            self.logger.info(f"Step {step_num}: Moving to '모든 메뉴 탭 닫기' menu at {step.pos_menu_tab}.")

            self.logger.info(f"Step {step_num}: 'reset_for_po_number_search' completed successfully.")
            time.sleep(1)
            
            return True, "reset_for_po_number_search completed successfully."
            
        except Exception as e:
            error_message = f"Step {step_num}: reset_for_po_number_search failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환
        
    ##################################### 공통 메서드 #############################################
    def detect_loading(self, step_num: int, step: Step):
        try:
            if self.loading.wait_for_loading_to_complete():
                self.logger.info("Loading completed successfully.")
                return True, "Loading completed successfully."
            else:
                self.logger.error("Loading timeout or failed to detect loading icon.")
                error_message = "Loading detection failed or took too long."
                return False, error_message
            
        except Exception as e:
            error_message = f"Step {step_num}: Loading detection failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환 

    def handle_task_exception(self, step_num, task_name: str, exception: Exception):
        error_message = f"Task '{task_name}' failed with error: {str(exception)}"
        detailed_traceback = traceback.format_exc()
        self.logger.error(f"{error_message}\n{detailed_traceback}")
        
        if not any(context['task'] == task_name for context in self.res.response['contexts']):
            self.res.add_contexts(step_num, task_name, "failed", error_message)
    
    ###################################################################################################

def execute_cw_req_due(json_data:str):
    # 설정 파일을 미리 로드합니다.
    PathHelper.load_config()
    master_mode =  PathHelper.get_config_value('master_mode',False)
    
    logger = LoggerManager.get_logger(__name__)
    loading= LoadingIconManager()
    res = ResponseManager()
    
    step_num = 0 # 초기화
    manager = CW_ReqDueManager(json_data, res, logger, loading, master_mode)    
    
    try: 
        
        total_steps = len(manager.contexts.__annotations__) # Contexts 클래스의 모든 스텝 필드를 카운트
        for step_num in range(1, total_steps + 1):
            step = getattr(manager.contexts, f'step_{step_num}')
            result = manager.execute_task(step_num, step)
            
            if result is not None: # 실패 메시지이면
                logger.error(f"Error occurred at step {step_num}: {res.to_json()}")
                return res.to_json() # 즉시 응답
            
    except Exception:
        logger.error(f"Response on exception: {res.to_json()}")
        return res.to_json() # 오류 발생시 즉시 응답
    
    logger.debug(f"Process completed successfully. Response: {res.to_json()}")
    return res.to_json() # 모든 스텝이 정상적으로 완료되었을때 즉시 응답