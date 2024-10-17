import os
import sys
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
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

# 루트 디렉토리 경로 설정
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),'../../'))
sys.path.append(root_dir)

# 절대 경로를 사용하여 모듈을 불러옴
from common.logger_manager import LoggerManager
from common.response_manager import ResponseManager

from common.loading_manager import LoadingIconManager
from common.loading_icon_manager import SuperLoadingManager

from common.utils.helper import PyAutoGuiHelper
from common.utils.path_utils import PathHelper

from common.popup_handling_manager import PopupManager
from common.ocr_popup_large_manager import PopupManager

@dataclass
class Step:

    task: str = ""
    search_str: str = ""
    po_no: str = ""
    
    # step_1
    pos_global_search_input: Tuple[int, int] = (0,0)
    pos_deliv_res: Tuple[int, int] = (0,0)
    pos_vali_1: Tuple[int, int] = (0,0)
    
    # step_2
    pos_po_no: Tuple[int, int] = (0,0)
    pos_search_btn_1: Tuple[int, int] = (0,0)
    region_table: Optional[Tuple[int, int, int, int]] = None
    
    # step_3
    pos_vehicle_info: Tuple[int, int] = (0,0)
    pos_deli_Type: Tuple[int, int] = (0,0)
    pos_reg_vehicle_Manag: Tuple[int, int] = (0,0)
    pos_checkbox: Tuple[int, int] = (0,0)
    pos_confirm_btn_1: Tuple[int, int] = (0,0)
    pos_confirm_btn_2: Tuple[int, int] = (0,0)
    pos_infopop_close_btn: Tuple[int, int] = (0,0)
    
    # step_4
    pos_excel_icon: Tuple[int, int] = (0,0)
    pos_excel_save: Tuple[int, int] = (0,0)
    
    # step_5
    po_data_list: List[Tuple[str, str, int]] = field(default_factory=list)  # 품번(str), 자재번호(str), boom수량(int)을 가지는 리스트
    read_columns: List[int] = field(default_factory=lambda: [0, 3, 12]) # 열 인덱스의 리스트 (예: [0, 3, 12])
    
    # step_6
    pos_start: Tuple[int, int] = (0,0)
    
    # step_7
    pos_deli_reserv_btn: Tuple[int, int] = (0,0)
    pos_popup_ok_btn: Tuple[int, int] = (0,0)
    pos_all_checkbox: Tuple[int, int] = (0,0)
    pos_tag: Tuple[int, int] = (0,0)
    pos_popup_close_btn_2: Tuple[int, int] = (0,0)
    
    # step_8
    pos_trns_btn: Tuple[int, int] = (0,0)
    pos_trns_print_icon: Tuple[int, int] = (0,0)
    pos_trns_confirm_btn_1: Tuple[int, int] = (0,0)
    pos_trns_close_btn: Tuple[int, int] = (0,0)
    pos_trns_confirm_btn_2: Tuple[int, int] = (0,0)
    
    # step_9
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
    
class CW_ReservationManager:
    def __init__(self, json_data: str, res, logger, super_loading_manager, loading, master_mode:bool = False):
        # JSON 문자열에서 백슬래시 문자를 두 번으로 바꿉니다.
        json_data = json_data.replace('\\', '\\\\')
        self.data = json.loads(json_data, encoding='utf-8')
        
        logger.info("Received JSON data:")
        logger.info(json.dumps(self.data, indent=4, ensure_ascii=False))
        
        self.logger = logger
        self.res = res
        
        self.loading = loading
        self.super_loading_manager = super_loading_manager
        
        self.master_mode = master_mode
        print(f"master_mode in StartApp: {self.master_mode}")
        logger.debug(f"master_mode in StartApp: {self.master_mode}")

        self.po_no = ""
        self.filepath = ""
        self.results = []
        
        #! 초기화 이후 모니터링 시작
        self.stop_signal = False  # stop_signal 초기화
        self.terminated = False 
        self.start_input_monitoring() # 키 입력 감지 시작

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
        )

    #TODO#################################################강제종료################################################
    
    def start_input_monitoring(self):
        """ 비동기 키 입력 감지 스레드 시작 """
        input_thread = threading.Thread(target=self.monitor_key_input, daemon = True)
        input_thread.start()
        
    def monitor_key_input(self):
        """ 키 입력을 감지하여 특정 키 입력 시 강제 종료 """
        self.logger.debug(f"모니터링 시작: 특정 키('q') 입력시 강제 종료합니다.")
        keyboard.add_hotkey('shift+q', self.force_terminate)
        
        # 스레드가 종료될 때까지 무한 대기, 대기 중에 종료 신호가 있으면 루프 종료
        while not self.stop_signal:
            time.sleep(0.1) # CPU 점유율을 낮추기 위해 짧은 대기
    
    def force_terminate(self):
        """ 강제 종료를 처리하는 메서드 """
        self.logger.info("사용자가 'Shift + Q' 키를 입력하여 프로세스를 강제 종료합니다.")
        print("사용자가 'Shift + Q' 키를 입력하여 프로세스를 강제 종료합니다.")
        
        self.stop_signal = True # 스레드 종료를 위해 stop_signal을 True로 설정
        self.terminated = True  # 종료 신호 설정
        
        # 응답을 준비하여 LabVIEW에 보내기
        self.res.add_contexts(0, "force_terminate", "exit", "Process terminated by user input (Shift + Q).")
        response = self.res.to_json()  # 응답을 호출한 곳에 반환하여 LabVIEW로 전송
        print(f"{response}")
        # 응답 반환 후 메인 스레드에서 직접 종료 실행
        os._exit(0)  # 프로그램을 강제로 종료
        #? 랩뷰로 전송 가는지 체크 (아마 안갈거임)
        return response  # 응답을 반환하여 LabVIEW로 전송
    
    def stop(self):
        # 프로그램 종료 시 호출되는 메서드
        self.stop_signal = True  # 스레드 종료를 위한 신호 설정
    
    #TODO#############################################################################################################

    def execute_task(self, step_num, step:Step):    
        task_map = {
            'navigate_to_deliv_reserv_improv' : self.navigate_to_deliv_reserv_improv,
            'load_po_table_data' : self.load_po_table_data,
            'input_vehicle_information': self.input_vehicle_information,
            'save_and_verify_excel': self.save_and_verify_excel,
            'find_matching_rows': self.find_matching_rows,
            'navigate_to_matching_rows': self.navigate_to_matching_rows,
            'reserve_delivery': self.reserve_delivery,
            'print_invoice': self.print_invoice,
            'reset_for_po_number_search': self.reset_for_po_number_search
        }
        
        try:
            if step.task in task_map:
                success, message = task_map[step.task](step_num, step)
                
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
            self.logger.info(f"Step {step_num}: Search term '{step.search_str}' copied to clipboard.")
            
            time.sleep(3)
            
            # 입력란 클릭 후 '개선' 입력 및 엔터
            pyautogui.hotkey('ctrl', 'v')
            self.logger.info(f"Step {step_num}: Search term pasted from clipboard.")
            time.sleep(0.5)
            pyautogui.press('enter')
            self.logger.info(f"Step {step_num}: 'Enter' key pressed, search initiated.")
            
            time.sleep(0.5)
            
            PyAutoGuiHelper.perform_double_click(step.pos_deliv_res) # 902,479
            self.logger.info(f"Step {step_num}: '납품예약(개선)' tab clicked at position / pos_deliv_res: {step.pos_deliv_res}.") 
            
            success, message =  self.super_loading_manager.wait_for_loading_to_complete()
            self.logger.debug(f"Step {step_num}: '납품예약' 버튼 클릭 로딩 감지 결과 - success: {success}, message: {message}")
            if not success:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}:[마스터모드 활성화] 로딩 감지 실패, \n 30초 대기 시간 추가...")
                    time.sleep(30) 
                else:
                    return False, message 
            
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
                self.logger.info(f"Step {step_num}: New window loaded successfully and contains '{matched_str_1}', 'navigate_to_deliv_reserv_improv' completed successfully.")
                return True, "navigate_to_deliv_reserv_improv' completed successfully."
                
            else:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}: New window failed to load correctly. '{matched_str_1}' not found. \n Waiting for 5 seconds before retry...")
                    time.sleep(5)  # 5초 대기     
                    return True, "navigate_to_deliv_reserv_improv successfully." 
                else:
                    self.logger.error(f"Step {step_num}: New window failed to load correctly. '{matched_str_1}' not found.")
                    return False, "Failed to load the delivery reservation window"

        except Exception as e:
            error_message = f"Step {step_num}: navigate_to_deliv_reserv_improv failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환 
    
    #TODO################################################# STEP_2 ######################################################
    
    def load_po_table_data(self, step_num:int, step:Step):
        try: 
            self.logger.info(f"Step {step_num}: Starting 'search_po_num'.")
            time.sleep(3)
            
            # po_no가 제공되지 않았을 경우 처리
            if not getattr(step, 'po_no', None):
                error_message = f"Step {step_num}: PO 번호 (po_no)가 step 데이터에 없습니다."
                self.logger.error(error_message)
                return False, error_message  # 에러를 반환하고 실행 중단
            
            self.logger.info(f"Step {step_num}: 'search_po_num' 시작.")
            time.sleep(0.5)
            
            # po_no 입력
            self.po_no = step.po_no # po 번호를 인스턴스 변수에 저장
            self.logger.debug(f"Step {step_num}: po_no: {self.po_no}")
            
            PyAutoGuiHelper.perform_double_click(step.pos_po_no) #684,198
            self.logger.info(f"Step {step_num}: PO number input field clicked at position {step.pos_po_no}.")
            time.sleep(0.5)
            
            pyautogui.typewrite(self.po_no) #684,198
            self.logger.info(f"Step {step_num}: PO number '{self.po_no}' entered successfully.")
            
            time.sleep(1)

            # po_no 조회 
            PyAutoGuiHelper.perform_click(step.pos_search_btn_1) # 1083,255
            self.logger.info(f"Step {step_num}: '납품예약 - 조회' clicked at position {step.pos_search_btn_1}.")
            
            success, message =  self.super_loading_manager.wait_for_loading_to_complete()
            self.logger.debug(f"Step {step_num}: '납품예약' 버튼 클릭 로딩 감지 결과 - success: {success}, message: {message}")
            if not success:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}:[마스터모드 활성화] 로딩 감지 실패, \n 30초 대기 시간 추가...")
                    time.sleep(30) 
                else:
                    return False, message 
            
            # PO조회 후 테이블 로드 검증 (최대 10번 시도, 각 시도 사이 3초 대기)
            if self.loading.wait_for_table_load(step.region_table, image_key="empty_table_image"):
                print(f"테이블 데이터 로드 성공")
                self.logger.info(f"Step {step_num}: Table data successfully loaded.")

                return True, "load_po_table_data completed successfully."
            
            else:
                if self.master_mode:
                    print(f"테이블 데이터 로드 실패")
                    self.logger.error(f"Step {step_num}: Failed to load table data. \n Waiting for 5 seconds before retry...")
                    time.sleep(10)
                    return True, "load_po_table_data completed successfully."
                else:
                    print(f"테이블 데이터 로드 실패")
                    self.logger.error(f"Step {step_num}: Failed to load table data.")
                    return False, "Failed to load table data."

        except Exception as e:
            error_message = f"Step {step_num}: load_po_table_data failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환   
        
        
    #TODO################################################# STEP_3 ######################################################
    
    def input_vehicle_information(self, step_num:int, step:Step):
        try:
            time.sleep(3)
            self.logger.info(f"Step {step_num}: Starting 'input_vehicle_information'.")
            
            # 차량입력
            PyAutoGuiHelper.perform_click(step.pos_vehicle_info) # 345,751
            self.logger.info(f"Step {step_num}: Clicking '차량입력' at pos_vehicle_info: {step.pos_vehicle_info}.")
            
            success, message =  self.super_loading_manager.wait_for_loading_to_complete()
            self.logger.debug(f"Step {step_num}: '납품예약' 버튼 클릭 로딩 감지 결과 - success: {success}, message: {message}")
            if not success:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}:[마스터모드 활성화] 로딩 감지 실패, \n 30초 대기 시간 추가...")
                    time.sleep(30) 
                else:
                    return False, message 
            
            # yard선택 687,431
            PyAutoGuiHelper.perform_click(step.pos_deli_Type) # 687,431
            self.logger.info(f"Step {step_num}: Clicking 'YARD 선택' at pos_deli_Type: {step.pos_deli_Type}.")
            
            time.sleep(0.5)
            
            # 정기 출입차량 관리 713,631
            PyAutoGuiHelper.perform_click(step.pos_reg_vehicle_Manag) # 713,63
            self.logger.info(f"Step {step_num}: Clicking '정기 출입차량 관리' at pos_reg_vehicle_Manag: {step.pos_reg_vehicle_Manag}.")

            success, message =  self.super_loading_manager.wait_for_loading_to_complete()
            self.logger.debug(f"Step {step_num}: '납품예약' 버튼 클릭 로딩 감지 결과 - success: {success}, message: {message}")
            if not success:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}:[마스터모드 활성화] 로딩 감지 실패, \n 30초 대기 시간 추가...")
                    time.sleep(30) 
                else:
                    return False, message 
            
            # 체크박스 체크 708,464
            PyAutoGuiHelper.perform_click(step.pos_checkbox) # 708,464
            self.logger.info(f"Step {step_num}: Clicking '체크박스 체크' at pos_checkbox: {step.pos_checkbox}.")
            time.sleep(0.5)
            
            # 확인 1173,720
            PyAutoGuiHelper.perform_click(step.pos_confirm_btn_1) # 1173,720
            self.logger.info(f"Step {step_num}: Clicking '확인' at pos_confirm_btn_1: {step.pos_confirm_btn_1}.")
            time.sleep(0.5)
            
            # 차량정보 팝업 나가기 확인 1274,794
            PyAutoGuiHelper.perform_click(step.pos_confirm_btn_2) # 1274,794
            self.logger.info(f"Step {step_num}: Clicking '[차량정보 팝업]확인' at pos_confirm_btn_2: {step.pos_confirm_btn_2}.")
            
            # 팝업뜸 대기
            success, message =  self.super_loading_manager.wait_for_loading_to_complete()
            self.logger.debug(f"Step {step_num}: '납품예약' 버튼 클릭 로딩 감지 결과 - success: {success}, message: {message}")
            if not success:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}:[마스터모드 활성화] 로딩 감지 실패, \n 30초 대기 시간 추가...")
                    time.sleep(30) 
                else:
                    return False, message 
                
            #info 팝업 나가기 '닫기' 1426,870
            PyAutoGuiHelper.perform_click(step.pos_infopop_close_btn) # 1426,870
            self.logger.info(f"Step {step_num}: Clicking 'Info 팝업 닫기' at pos_infopop_close_btn: {step.pos_infopop_close_btn}.")
            time.sleep(1)
            
            return True, "input_vehicle_information completed successfully."
            
        except Exception as e:
            error_message = f"Step {step_num}: reset_for_po_number_search failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message
                
    #TODO################################################# STEP_4 ######################################################
    
    def save_and_verify_excel(self, step_num:int, step:Step):
        try: 
            time.sleep(3)
            self.logger.info(f"Step {step_num}: Starting 'save_and_verify_excel'.")
            
            # 엑셀 아이콘 클릭 1794,491
            PyAutoGuiHelper.perform_click(step.pos_excel_icon) # 1426,870
            self.logger.info(f"Step {step_num}: Clicking '엑셀 아이콘' at pos_excel_icon: {step.pos_excel_icon}.")
            
            # 대기 시간 
            time.sleep(3)
            
            # 엑셀 다운로드 저장 클릭 915,579 
            PyAutoGuiHelper.perform_click(step.pos_excel_save) # 1426,870
            self.logger.info(f"Step {step_num}: Clicking '엑셀 다운로드' at pos_excel_save: {step.pos_excel_save}.")
            
            success, message =  self.super_loading_manager.wait_for_loading_to_complete()
            self.logger.debug(f"Step {step_num}: '납품예약' 버튼 클릭 로딩 감지 결과 - success: {success}, message: {message}")
            if not success:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}:[마스터모드 활성화] 로딩 감지 실패, \n 30초 대기 시간 추가...")
                    time.sleep(30) 
                else:
                    return False, message 
            
            #일반납품예약
            file_directory = PathHelper.get_abs_path('reports','일반납품예약')
            filename = PyAutoGuiHelper.generate_filename('일반 납품예약','.xlsx')
            self.logger.debug(f"Step {step_num}: Generated filename is {filename}.")
            time.sleep(0.5)
            
            self.filepath = os.path.join(file_directory, filename)
            self.logger.info(f"Step {step_num}: File path constructed: {self.filepath}.")
            
            time.sleep(0.5)
            PyAutoGuiHelper.save_file_with_name(self.filepath)
            self.logger.info(f"Step {step_num}: Excel file saved successfully as {self.filepath}.")
            
            time.sleep(1)
            
            # 파일 존재 확인, 재시도 로직 추가
            success, message =  self.check_excel_exists(step_num, self.filepath, max_attempts=5)
            self.logger.info(f"Step {step_num}: {message}")
            if not success:
                return False, "File not found after saving attempt."
            
            return True, "save_and_verify_excel' completed successfully." 

        except Exception as e:
            error_message = f"Step {step_num}: save_and_verify_excel failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message
        
    def check_excel_exists(self, step_num, file_path, max_attempts=5):
        try:
            """ 파일이 존재하는지 재시도 하며 확인 """
            attempts = 0
            while attempts < max_attempts:
                if os.path.exists(file_path):
                    return True, "File found"
                else:
                    time.sleep(3)
                    attempts += 1
            return False, "File not found after multiple attempts"

        except Exception as e:
            error_message = f"Step {step_num}: check_excel_exists failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message

    #TODO################################################# STEP_5 ######################################################
    
    def find_matching_rows(self, step_num, step:Step):
        try:
            time.sleep(3)
            self.logger.info(f"Step {step_num}: Starting 'find_matching_rows'.")
            
            df = pd.read_excel(self.filepath, engine='openpyxl', sheet_name=0, header=0)
            time.sleep(0.5)
            
            # JSON 데이터로부터 열 인덱스와 po_data_list를 받음
            read_columns = step.read_columns  # [0, 3, 12] 
            # 엑셀 파일에서 지정된 열 읽어오기
            print(f"Step {step_num}: Reading specified columns {read_columns} from Excel file at {self.filepath}")
            #? read_column 타입 확인하기
            self.logger.debug(f"Step {step_num}: Type of read_columns: {type(read_columns)}")
            
            #? 데이터 프레임 열 범위 내에 있는지 확인
            invalid_columns = [ col for col in read_columns if col < 0 or col >= len(df.columns)]
            if invalid_columns:
                self.logger.error(f"Step {step_num}: Invalid column indices found: {invalid_columns}")
                return False, f"Step {step_num}: Column indices {invalid_columns} are out of range."
            self.logger.info(f"Step {step_num}: All columns are within valid range.")
            
            #? 열 데이터 추출후 납품예약불가사유가 없는 데이터 필터링
            part_po_idx = read_columns[0]
            cause_idx = read_columns[1]
            reserv_num_idx = 10
            
            # P/O품번, 납품예약불가사유 열 데이터 선택 (pandas.Series 객체 타입)
            part_po_row = df.iloc[:, part_po_idx]         # po품번
            cause_row = df.iloc[:, cause_idx]             # 납품예약불가사유
            reserv_num_row = df.iloc[:, reserv_num_idx]   # 납품예약번호

            #! 납품예약불가사유, 납품예약번호 결측값 찾기
            combined_condition = (
                cause_row.isnull() & reserv_num_row.isnull()
            )
            
            #!!!!!!!! isnull()외에 사용자에 의해 공백 또는 빈문자열이 들어갔을 경우 아래 코드 사용
            # part_po_idx = df.iloc[:, 0] # po품번
            # cause_row = df.iloc[:, 3] # 납품예약불가사유
            # reserv_num_row = df.iloc[:, 10] # 납품예약번호
            
            # # cause_row와 reserv_num_row를 문자열로 변환하기 전에 결측치 처리
            # cause_row_str = cause_row.fillna('').astype(str) # NaN 값을 빈 문자열로 변환 후 문자열로 변환
            # reserv_num_row_str = reserv_num_row.fillna('').astype(str)
            
            # # cause_row 조건 설정
            # condition = (
            #     (cause_row_str == '') |             # 빈 문자열 확인
            #     (cause_row_str.isspace()) |         #공백 문자열 확인
            #     (cause_row_str.isin(['-','N/A']))   # 특수 문자 '-','N/A' 확인
            # )
            # # reserv_num_row 조건 설정
            # reserv_condition = (
            #     (reserv_num_row_str == '') |  # 빈 문자열 확인
            #     (reserv_num_row_str.str.isspace())  # 공백 문자열 확인
            # )
            # # 조건을 만족하는 P/O품번 추출
            # excel_data = part_po_row[condition & reserv_condition]
            
    
            # 두 조건을 모두 충족하는 품번 데이터 추출
            Extracted_data = part_po_row[combined_condition] # excel data: 인덱스 품번
            self.logger.debug(f"납품예약불가사유, 납품예약번호가 없는 데이터 추출: \n {Extracted_data}")
            
            # 중복된 품번 제거 (인덱스가 낮은 첫 번째 p/o 번호만 남김)
            Extracted_data_unique = Extracted_data.drop_duplicates(keep='first')
            self.logger.debug(f"추출된 데이터 중, 차수(인덱스)가 낮은 데이터 추출(중복X): \n {Extracted_data_unique}")            
            
            # 문자열로 변환
            Extracted_data_unique = Extracted_data_unique.astype(str)

            #? JSON 데이터 (P/O품번, 자재번호, BOM수량)
            po_data_list =  step.po_data_list
            self.logger.debug(f"Step {step_num}: 납품 예약 리스트(JSON 데이터) (type{type(po_data_list)}): \n {po_data_list}")
            
            #! PO품번 기준 중복 제거 및 BOM수량 합산 (딕셔너리)
            bom_sum_data = {}
            for item in po_data_list:
                part_po = item[0] # PO품번
                bom_quantity = item[2] # BOM수량
                if part_po in bom_sum_data:
                    self.logger.debug(f"PO품번 {part_po}가 이미 존재합니다. BOM 수량 {bom_quantity}를 추가합니다.")
                    bom_sum_data[part_po] += bom_quantity # 이미 존재하면 수량을 누적
                else:
                    self.logger.debug(f"PO품번 {part_po}가 존재하지 않습니다. BOM 수량 {bom_quantity}로 초기화합니다.")
                    bom_sum_data[part_po] = bom_quantity  # 처음 등장하면 수량을 초기화

            #! json데이터에서 중복을 제거하고 bom수량을 합산한 결과
            #! 키는 p/o품번이고 값은 해당 품번의 합산된 bom수량
            result_dict = {key: bom_sum_data[key] for key in bom_sum_data}
            self.logger.info(f"BOM 수량을 합산한 최종 납품예약 리스트(type:dict): {result_dict}")
            
            # Extracted_data_unique와 result_dict 데이터 비교
            self.results = []
            for index, part_po in Extracted_data_unique.items():
                if part_po in result_dict:
                    bom_quantity = result_dict[part_po]
                    self.logger.debug(f"PO 품번 {part_po}가 인덱스 {index}에서 발견되었습니다. BOM 수량: {bom_quantity}.")
                    self.results.append((index, part_po, bom_quantity))
                    
            self.logger.debug(f"Step {step_num}: 매칭된 P/O 품번과 BOM 수량: \n {self.results}")

            # 매칭되는 데이터가 없는 경우 
            if not self.results:
                self.logger.info(f"Step {step_num}: No matching results found")
                return False, f"Step {step_num}: No matching results found."

            # 리스트 형태의 튜플 반환 [ (인덱스,'P/O품번',BOM수량),(인덱스,'P/O품번',BOM수량),...]
            return True, f"Step {step_num}: matching results: {self.results}"

        except Exception as e:
            error_message = f"Step {step_num}: find_matching_rows failed: {str(e)}"
            print(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환
        
    #TODO################################################# STEP_6 ######################################################
        
    def navigate_to_matching_rows(self, step_num:int, step:Step):
        try:
            time.sleep(3)
            self.logger.info(f"Step {step_num}: Starting 'navigate_to_matching_rows'.")
            
            # 시작 위치로 이동
            PyAutoGuiHelper.perform_click(step.pos_start)
            self.logger.info(f"Step {step_num}: Moved to start position at {step.pos_start}.")
            
            current_index = 0
            for result in self.results:
                # results 튜플에서 추출
                index, _, bom_quantity = result
                
                # 인덱스를 정수로 변환하여 이동에 문제 없도록 처리
                target_index = int(index)
                bom_quantity = str(bom_quantity)
                
                # 인덱스로 이동
                PyAutoGuiHelper.move_to_index(current_index, target_index)
                self.logger.info(f"Step {step_num}: Moving from index {current_index} to {target_index}.")
                time.sleep(0.5)
                
                # 현재 셀 값 복사
                pyautogui.hotkey('ctrl','c')
                time.sleep(0.5)
                
                #클립보드에 복사된 값을 읽음
                cell_value = pyperclip.paste().strip()
                self.logger.debug(f"Step {step_num} cell_value: {cell_value} type: {type(cell_value)}")
                time.sleep(0.5)
                
                if cell_value == "0":
                    # 비활성화 상태
                    self.logger.debug(f"Step {step_num}: Target cell is inactive. Skipping...")
                else:
                    # 활성화 상태로 간주하고 수량 입력
                    pyautogui.hotkey('ctrl','a')
                    time.sleep(0.5)
                    pyautogui.write(bom_quantity)
                    self.logger.info(f"Step {step_num}: Bom quantity [{bom_quantity}] input at index {target_index}.")
                    
                # 체크박스 체크
                pyautogui.hotkey('shift', 'tab')
                time.sleep(0.5)
                pyautogui.press('space')
                self.logger.info(f"Step {step_num}: Checkbox checked at index {target_index}.")
                
                # 수량입력으로 다시 이동
                pyautogui.press('right', presses=22)
                time.sleep(0.5)
                
                current_index = target_index
                time.sleep(0.5)
                
            self.logger.info(f"Step {step_num}: Action performed on all matching rows successfully.")
            return True, "Action performed on all matching rows successfully."

        except Exception as e:
            error_message = f"Step {step_num}: compare_with_json failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환
    
    #TODO################################################# STEP_7 ######################################################
    
    def reserve_delivery(self, step_num:int, step:Step):
        try:
            time.sleep(3)   
            self.logger.info(f"Step {step_num}: Starting 'reserve_delivery'.") 

            # 납품예약 버튼 클릭
            PyAutoGuiHelper.perform_click(step.pos_deli_reserv_btn) # 1426,870
            self.logger.info(f"Step {step_num}: Clicking '납품예약' button at pos_deli_reserv_btn: {step.pos_deli_reserv_btn}.")

            success, message =  self.super_loading_manager.wait_for_loading_to_complete()
            self.logger.debug(f"Step {step_num}: '납품예약' 버튼 클릭 로딩 감지 결과 - success: {success}, message: {message}")
            if not success:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}:[마스터모드 활성화] 로딩 감지 실패, \n 30초 대기 시간 추가...")
                    time.sleep(30) 
                else:
                    return False, message 

            success_texts = ["거래명세서를", "발행하시겠습니까?"]
            
            success, detected_text = PopupManager.process_popup(
                success_texts,
                'generate_invoice'
            )
            
            
            if success:
                self.logger.debug(f"Step {step_num}: process '납품예약' popup result - success: {success}, detected_text: {detected_text}")   
                PyAutoGuiHelper.perform_click(step.pos_popup_ok_btn)
                self.logger.info(f"Step {step_num}: Clicking '거래명세서를 발행하시겠습니까?.' button at position {step.pos_popup_ok_btn}. / pos_popup_ok_btn: {step.pos_popup_ok_btn}")
            else:
                self.logger.debug(f"Step {step_num}: Failed to process popup. Last detected text: '{detected_text.strip()}'.")
                return False, f"Failed to process '납품예약'popup. Last detected text: '{detected_text.strip()}'."

            success, message =  self.super_loading_manager.wait_for_loading_to_complete()
            self.logger.debug(f"Step {step_num}: '납품예약' 버튼 클릭 로딩 감지 결과 - success: {success}, message: {message}")
            if not success:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}:[마스터모드 활성화] 로딩 감지 실패, \n 30초 대기 시간 추가...")
                    time.sleep(30) 
                else:
                    return False, message 

            # 체크박스 모두 체크
            PyAutoGuiHelper.perform_click(step.pos_all_checkbox) # 1426,870
            self.logger.info(f"Step {step_num}: Clicking '체크박스 클릭' at pos_all_checkbox: {step.pos_all_checkbox}.")
            time.sleep(0.5)
            
            # 자재TAG 클릭
            max_retries = 3
            for attempt in range(max_retries):
                success, message = self.super_loading_manager.wait_for_loading_to_complete()
                if success:
                    break # 성공하면 반복 종료
                self.logger.debug(f"Step {step_num}: Retry attempt {attempt + 1} - Waiting for loading to complete")
                time.sleep(3)  # 재시도 대기 시간

            # 재시도 횟수 초과 시 종료 로직
            if not success:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}: 마스터모드 활성화 - 최대 시도 횟수 초과, 시스템 종료를 시도합니다.")
                    pyautogui.hotkey('shift', 'q')  # 종료 단축키 시도
                return False, "Maximum retry limit reached, process terminated."
            
            # 닫기 클릭
            PyAutoGuiHelper.perform_click(step.pos_popup_close_btn_2) # 1426,870
            self.logger.info(f"Step {step_num}: Clicking '팝업 닫기' button at pos_popup_close_btn_2: {step.pos_popup_close_btn_2}.")
            
            self.logger.info(f"Step {step_num}: reserve_delivery' completed successfully.")
            return True, "reserve_delivery' completed successfully." 
            
        except Exception as e:
            error_message = f"Step {step_num}: move_to_target_and_perform_action failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환

    #TODO################################################# STEP_8 ######################################################
    
    def print_invoice(self, step_num:int, step:Step):
        try:
            time.sleep(3)   
            self.logger.info(f"Step {step_num}: Starting 'print_invoice'.") 

            # 거래명세서출력 버튼 클릭
            PyAutoGuiHelper.perform_click(step.pos_trns_btn) # 1426,870
            self.logger.info(f"Step {step_num}: Clicking '거래명세서출력' button at pos_trns_btn: {step.pos_trns_btn}.")
            
            max_retries = 3
            for attempt in range(max_retries):
                success, message = self.super_loading_manager.wait_for_loading_to_complete()
                if success:
                    break # 성공하면 반복 종료
                self.logger.debug(f"Step {step_num}: Retry attempt {attempt + 1} - Waiting for loading to complete")
                time.sleep(3)  # 재시도 대기 시간

            # 재시도 횟수 초과 시 종료 로직
            if not success:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}: 마스터모드 활성화 - 최대 시도 횟수 초과, 시스템 종료를 시도합니다.")
                    pyautogui.hotkey('shift', 'q')  # 종료 단축키 시도
                return False, "Maximum retry limit reached, process terminated."
            
            # 파일 저장 아이콘 클릭
            PyAutoGuiHelper.perform_click((497,174))
            self.logger.info(f"Step {step_num}: '파일 저장' 아이콘 클릭 (497,174)")
            
            time.sleep(1)

            # 매개변수가 틀립니다 팝업 처리
            PyAutoGuiHelper.perform_click((994,584))
            self.logger.info(f"Step {step_num}: '매개변수가 틀립니다' 팝업 처리 (994,584)")

            # 파일 저장 경로 입력란 클릭
            PyAutoGuiHelper.perform_double_click((834,579))
            self.save_pdf_file(step_num, step, entity_name='중앙창고_거래명세서', po_no=self.po_no)
            time.sleep(1)

            # 매개변수가 틀립니다 팝업 처리
            PyAutoGuiHelper.perform_click((994,584))

            time.sleep(3)

            # 프린트 아이콘 클릭
            PyAutoGuiHelper.perform_click(step.pos_trns_print_icon) # 1426,870
            self.logger.info(f"Step {step_num}: Clicking '프린트 아이콘' at pos_trns_print_icon: {step.pos_trns_print_icon}.")
            
            # 대기
            success, message =  self.super_loading_manager.wait_for_loading_to_complete()
            self.logger.debug(f"Step {step_num}: '납품예약' 버튼 클릭 로딩 감지 결과 - success: {success}, message: {message}")
            if not success:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}:[마스터모드 활성화] 로딩 감지 실패, \n 30초 대기 시간 추가...")
                    time.sleep(30) 
                else:
                    return False, message 
            
            # 전체페이지 프린트 확인 클릭
            PyAutoGuiHelper.perform_click(step.pos_trns_confirm_btn_1) # 1426,870
            self.logger.info(f"Step {step_num}: Clicking '전체페이지 1부 인쇄 확인'button at pos_trns_confirm_btn_1: {step.pos_trns_confirm_btn_1}.")
            
            # 프린트 대기열 추가시간
            time.sleep(5)
            
            # 닫기 클릭
            PyAutoGuiHelper.perform_click(step.pos_trns_close_btn) # 1426,870
            self.logger.info(f"Step {step_num}: Clicking '팝업 닫기'button at pos_trns_close_btn: {step.pos_trns_close_btn}.")
            
            time.sleep(0.5)
            
            # 확인 클릭
            PyAutoGuiHelper.perform_click(step.pos_trns_confirm_btn_2) # 1426,870
            self.logger.info(f"Step {step_num}: Clicking '팝업 닫기'button at pos_trns_confirm_btn_2: {step.pos_trns_confirm_btn_2}.")
            time.sleep(0.5)
            
            self.logger.info(f"Step {step_num}: 'print_invoice' completed successfully.")
            return True, "print_invoice completed successfully."
            
        except Exception as e:
            error_message = f"Step {step_num}: move_to_target_and_perform_action failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환

    #TODO################################################# STEP_9 ######################################################
    
    def reset_for_po_number_search(self, step_num:int, step:Step):
        try: 
            time.sleep(3)
            self.logger.info(f"Step {step_num}: Starting 'reset_for_po_number_search'.")
            
            # 현재 창 포커스
            pyautogui.click(step.pos_window_focus)
            self.logger.info(f"Step {step_num}: Clicking 'pos_window_focus' input at position {step.pos_window_focus}. / pos_window_focus: {step.pos_window_focus}")
            
            # 현재 창 닫기
            for i in range(2):
                self.logger.debug(f"Step {step_num}: Pressing 'alt + x' to close all windows. (Attempt {i+1})")
                pyautogui.hotkey('alt','x', interval=0.5)
                
            self.logger.info(f"Step {step_num}: Finished pressing 'alt + x' {i+1} times.")

            time.sleep(0.5)
            
            # 상위 메뉴 탭 모두 닫기
            PyAutoGuiHelper.perform_click(step.pos_menu_tab) # 214,95
            self.logger.info(f"Step {step_num}: Moving to '모든 메뉴 탭 닫기' menu at {step.pos_menu_tab}.")
            
            self.logger.info(f"Step {step_num}: 'reset_for_po_number_search' completed successfully.")
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

def execute_cw_delv_inv(json_data: str):
    # 설정 파일을 미리 로드합니다.
    PathHelper.load_config()

    master_mode = PathHelper.get_config_value('master_mode',False)
    logger = LoggerManager.get_logger(__name__)
    loading = LoadingIconManager()
    super_loading_manager = SuperLoadingManager()
    res = ResponseManager()

    step_num = 0  # 초기화    
    manager = CW_ReservationManager(json_data, res, logger, super_loading_manager, loading, master_mode) 
    
    try: 
        total_steps = len(manager.contexts.__annotations__) # Contexts 클래스의 모든 스텝 필드를 카운트
        for step_num in range(1, total_steps + 1):
            step = getattr(manager.contexts, f'step_{step_num}')
            result = manager.execute_task(step_num, step)
            
            # 종료 신호가 설정되었는지 확인
            if manager.terminated:
                logger.info("Terminated by user input.")
                print("Terminated by user input.")
                return manager.force_terminate()
            
            if result is not None: # 실패 메시지이면
                logger.error(f"Error occurred at step {step_num}: {res.to_json()}")
                return res.to_json() # 즉시 응답
            
    except Exception:
        logger.error(f"Response on exception: {res.to_json()}")
        return res.to_json() # 오류 발생시 즉시 응답
    
    finally:
        manager.stop()  # 종료 시 호출하여 스레드 종료
    
    logger.debug(f"Process completed successfully. Response: {res.to_json()}")
    return res.to_json() # 모든 스텝이 정상적으로 완료되었을때 즉시 응답
    