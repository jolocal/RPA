import pyautogui
import pandas as pd
import os
import sys
import json
import time
import pyperclip
import traceback
import pytesseract
from PIL import Image
import cv2
import numpy as np
import matplotlib.pyplot as plt

import threading
import keyboard

from datetime import datetime  # 날짜와 시간 모듈 추가

from dataclasses import dataclass, field
from typing import List, Tuple, Optional

import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 루트 디렉토리 경로 설정 (src 경로)
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(root_dir)

# 절대 경로를 사용하여 모듈을 불러옴

from common.logger_manager import LoggerManager
from common.response_manager import ResponseManager
from common.popup_manager import PopupManager
from common.loading_manager import LoadingIconManager
from common.loading_icon_manager import SuperLoadingManager
from common.utils.helper import PyAutoGuiHelper
from common.utils.path_utils import PathHelper

from common.popup_handling_manager import PopupManager
from common.ocr_popup_large_manager import PopupManager

@dataclass
class Step:
    task: str = ""
    po_no: str = ""
    read_column: int = 0
    inbound_date: str = ""
    
    pos_material_tab: Tuple[int, int] = (0, 0)
    pos_pallet_tab: Tuple[int, int] = (0, 0) #step_1 & step_7
    pos_vali: Tuple[int, int] = (0, 0) # step_1 & step_4
    
    pos_po: Tuple[int, int] = (0, 0)
    pos_status: Tuple[int, int] = (0, 0)
    status_options: List[Tuple[int, int]] = field(default_factory=list)
    pos_search_btn: Tuple[int, int] = (0, 0)
    pos_popup_btn: Tuple[int, int] = (0, 0)
    
    pos_excel: Tuple[int, int] = (0, 0)
    pos_save_btn: Tuple[int, int] = (0, 0)
    pos_start: Tuple[int, int] = (0, 0) # step_3 & step_6
    target_codes: Optional[List[str]] = field(default_factory=list)
    
    pos_pallet_btn: Tuple[int, int] = (0, 0)
    pos_yes_btn: Tuple[int, int] = (0, 0)
    # region_popup: Optional[Tuple[int, int, int, int]] = None
    # region_popup_btn: Optional[Tuple[int, int, int, int]] = None
    pos_btn_1: Tuple[int, int] = (0, 0)
    pos_btn_2: Tuple[int, int] = (0, 0)
    pos_btn_3: Tuple[int, int] = (0, 0)
    all_checkbox: Tuple[int, int] = (0, 0)
    deli_reserv_btn: Tuple[int, int] = (0, 0)
    
    pos_direct_deli: Tuple[int, int] = (0, 0)
    pos_vehicle_info: Tuple[int, int] = (0, 0)
    pos_deli_Type: Tuple[int, int] = (0, 0)
    pos_reg_vehicle_Manag: Tuple[int, int] = (0, 0)
    pos_checkbox: Tuple[int, int] = (0, 0)
    pos_confirm_btn_1: Tuple[int, int] = (0, 0)
    pos_confirm_btn_2: Tuple[int, int] = (0, 0)
    
    pos_deli_reserv_btn: Tuple[int, int] = (0, 0)
    pos_popup_close_btn: Tuple[int, int] = (0, 0)
    pos_popup_no_btn: Tuple[int, int] = (0, 0)
    
    # 거래명세서
    pos_trns_btn: Tuple[int, int] = (0, 0)  # '거래명세서출력' 진입점
    pos_all_checkbox: Tuple[int, int] = (0,0)
    
    ## 자재TAG
    pos_tag_btn: Tuple[int, int] = (0,0)
    pos_tag_print_icon: Tuple[int, int] = (0,0)
    pos_tag_confirm_btn: Tuple[int, int] = (0,0)
    pos_tag_close_btn: Tuple[int, int] = (0,0)
    ## 거래명세서
    pos_trns_print_btn: Tuple[int, int] = (0,0)
    pos_ok_btn: Tuple[int, int] = (0,0)
    pos_trns_print_icon: Tuple[int, int] = (0,0)
    pos_trns_confirm_btn_1: Tuple[int, int] = (0,0)
    pos_trns_close_btn: Tuple[int, int] = (0,0)
    
    pos_trns_confirm_btn_2: Tuple[int, int] = (0,0) # 거래명세서 팝업 나가기
    
    # 납품상세리스트
    pos_ddl_print_btn: Tuple[int, int] = (0,0)  # '납품상세리스트출력' 진입점
    pos_ddl_confirm_btn: Tuple[int, int] = (0,0)
    # 인쇄 (전체)
    pos_ddl_print_icon_1: Tuple[int, int] = (0,0)
    pos_ddl_confirm_btn_1: Tuple[int, int] = (0,0)
    # 인쇄 (4페이지)
    pos_ddl_print_icon_2: Tuple[int, int] = (0,0)
    pos_ddl_page_options_2: Tuple[int, int] = (0,0)
    pos_ddl_confirm_btn_2: Tuple[int, int] = (0,0)
    # 인쇄 (1페이지)
    pos_ddl_print_icon_3: Tuple[int, int] = (0,0)
    pos_ddl_page_options_3: Tuple[int, int] = (0,0)
    pos_ddl_confirm_btn_3: Tuple[int, int] = (0,0)

    pos_ddl_close_btn: Tuple[int, int] = (0,0)  # 납품상세리스트 나가기
    
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

class HN_ReservationManager:
    def __init__(self, json_data: str, res, logger, loading, master_mode:bool = False):
        # JSON 문자열에서 백슬래시 문자를 두 번으로 바꿉니다.
        json_data = json_data.replace('\\', '\\\\')
        self.data = json.loads(json_data)
        
        self.logger = logger
        self.res = res
        self.loading = loading
        self.master_mode = master_mode
        print(f"master_mode in StartApp: {self.master_mode}")
        logger.debug(f"master_mode in StartApp: {self.master_mode}")
        
        self.filepath = ""
        self.matches = None  # matches를 초기화
        self.total_count = None
        self.index_value_pairs = []

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
            step_8 = Step(**self.data['contexts']['step_8'])
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
            'move_to_menu' : self.move_to_menu,
            'search_po_num' : self.search_po_num,
            'find_and_input_inbound_date' : self.find_and_input_inbound_date,
            'generate_pallet' : self.generate_pallet,
            'input_vehicle_information': self.input_vehicle_information,
            'reserve_delivery': self.reserve_delivery,
            'print_invoice_and_details': self.print_invoice_and_details,
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

    ############################################# step_1 #############################################

    def move_to_menu(self, step_num:int, step:Step):
        try:
            time.sleep(5)
            self.logger.info(f"Step {step_num}: Starting 'move_to_menu'.")

            # 자재지원관리 메뉴 이동
            PyAutoGuiHelper.perform_click(step.pos_material_tab) # 75,343
            self.logger.info(f"Step {step_num}: '자재지원관리 메뉴' clicked at position {step.pos_material_tab}.")
            time.sleep(1)

            # 직납/직사급 Pallet 관리
            PyAutoGuiHelper.perform_click(step.pos_pallet_tab) # 110,680
            self.logger.info(f"Step {step_num}: '직납/직사급 Pallet 관리' clicked at position / pos_pallet_tab: {step.pos_pallet_tab}.")

            ###################### 필수 ######################
            # 필수 대기 시간
            time.sleep(5)
            success, message = self.detect_loading(step_num, step)
            self.logger.debug(f"Step {step_num}: Loading detect_loading result - success: {success}, message: {message}")  
            if not success:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}: Loading detection failed, \n Waiting for 5 seconds before retry...")
                    time.sleep(5)
                else:
                    return False, message
            time.sleep(5)
            
            # 새창 로드 검증  
            PyAutoGuiHelper.perform_double_click(step.pos_vali) #480,231
            self.logger.info(f"Step {step_num}: Validation area double-clicked at position / pos_vali: {step.pos_vali}.")
            time.sleep(1)   
            pyautogui.hotkey('ctrl','c')
            self.logger.info(f"Step {step_num}: Clipboard data copied successfully.")
            time.sleep(1)
            
            # 클립보드에서 데이터 가져오기
            clipboard_data_pallet = pyperclip.paste().split('\n')
            self.logger.debug(f"Step {step_num}: Clipboard data read: {clipboard_data_pallet}.")
            time.sleep(1)   
            
            # "(주)케이씨" 일치하는지 확인
            matched_str = "(주)케이씨" 
            self.logger.debug(f"Step {step_num}: Checking if clipboard data contains the string '(주)케이씨'.")
            
            if matched_str in clipboard_data_pallet:
                self.logger.info(f"Step {step_num}: New window loaded successfully and contains '{matched_str}'.")
                return True,"'move_to_menu' completed successfully. New window loaded successfully." 
            
            else:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}: New window failed to load correctly. '{matched_str}' not found. \n Waiting for 5 seconds before retry...")
                    time.sleep(5)  # 5초 대기     
                else: 
                    self.logger.error(f"Step {step_num}: New window failed to load correctly. '{matched_str}' not found.")
                    return False, "Failed to load the delivery reservation window"
        
        except Exception as e:
            error_message = f"Step {step_num}: move_to_menu failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환
    

    ############################################# step_2 #############################################
    
    def search_po_num(self, step_num:int, step:Step):
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
            # po_no 입력
            PyAutoGuiHelper.perform_double_click(step.pos_po)
            self.logger.info(f"Step {step_num}: PO number input field clicked at position {step.pos_po}.")
            
            time.sleep(3)   
            pyautogui.typewrite(step.po_no)
            self.logger.info(f"Step {step_num}: PO number '{step.po_no}' entered successfully.")
            
            # 진행상태 체크
            time.sleep(1)
            PyAutoGuiHelper.perform_click(step.pos_status) # 진행상태 클릭
            self.logger.info(f"Step {step_num}: '진행상태' clicked at position {step.pos_status}.")

            time.sleep(1)   
            PyAutoGuiHelper.perform_click_sequence(step.status_options) # 진행상태 옵션 체크
            self.logger.info(f"Step {step_num}: Status options {step.status_options} selected successfully.")
            
            time.sleep(1)   
            PyAutoGuiHelper.perform_click(step.pos_search_btn) # 조회 1클릭
            self.logger.info(f"Step {step_num}: '조회' button clicked at position {step.pos_search_btn}.")
            
            time.sleep(1)   
            pyautogui.click()
            self.logger.info(f"Step {step_num}: Search initiated.")
            
            # 로딩 감지
            time.sleep(3)   
            success, message = self.detect_loading(step_num, step)
            self.logger.debug(f"Step {step_num}: Loading detect_loading result - success: {success}, message: {message}")  
            if not success:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}: Loading detection failed, \n Waiting for 15 seconds before retry...")
                    time.sleep(15)
                else:
                    return False, message
            time.sleep(5)
            
            return True, "'search_po_num' completed successfully."  # 작업이 성공적으로 완료됨
        
        except Exception as e:
            error_message = f"Step {step_num}: search_po_num failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환   
    
    ############################################# step_3 #############################################
        
    def find_and_input_inbound_date(self, step_num:int, step:Step):
        try: 
            time.sleep(3)   
            self.logger.info(f"Step {step_num}: Starting 'find_and_input_inbound_date'.")
            
            # 엑셀 저장
            self.save_excel_with_index(step_num, step)
            
            # 엑셀 존재 여부 체크
            self.check_excel_exists(step_num)

            # JSON 자재코드와 엑셀 비교
            self.matches = self.compare_with_json(step_num, step)

            # 해당 자재코드로 이동 및 입고예정일 입력
            self.move_to_target_and_perform_action(step_num, step, self.matches)

            self.logger.info(f"Step {step_num}: 'find_and_input_inbound_date' completed successfully.")
            
            return True, "find_and_input_inbound_date' completed successfully."  # 작업이 성공적으로 완료됨
            
        except Exception as e:
            error_message = f"Step {step_num}: search_po_num failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환   
    
    
    ##################################### step_3 내부 메서드 #############################################

    def save_excel_with_index(self, step_num:int, step: Step):
        try: 
            time.sleep(1)
            self.logger.info(f"Step {step_num}: Starting 'save_excel_with_index'.")
            
            # 엑셀 아이콘 클릭 및 저장
            PyAutoGuiHelper.perform_click(step.pos_excel)
            self.logger.info(f"Step {step_num}: Excel icon clicked successfully at position {step.pos_excel}.")
            
            time.sleep(3)

            PyAutoGuiHelper.perform_click(step.pos_save_btn)
            self.logger.info(f"Step {step_num}: Save button clicked successfully at position {step.pos_save_btn}.")
            
            # 로딩
            time.sleep(5)
            
            # 파일 디렉토리 + 파일이름 + .xlsx   
            file_directory = PathHelper.get_abs_path('reports','직납직사급')
            filename = PyAutoGuiHelper.generate_filename("직납_직사급_Pallet_관리", "xlsx")
            self.logger.debug(f"Step {step_num}: Generated filename is {filename}.")
            
            time.sleep(1)   
            self.filepath = os.path.join(file_directory, filename)
            self.logger.info(f"Step {step_num}: File path constructed: {self.filepath}.")
            
            time.sleep(1) 
            PyAutoGuiHelper.save_file_with_name(self.filepath)
            
            # 파일 저장중........
            time.sleep(5) # 파일 저장 후, 파일 시스템이 저장을 마칠 시간 주기
            
            self.logger.info(f"Step {step_num}: Excel file saved successfully as {filename}.")
        
        except Exception as e:
            error_message = f"Step {step_num}: save_excel_with_index: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환   
    

    def check_excel_exists(self, step_num:int):
        try: 
            time.sleep(3)
            self.logger.info(f"Step {step_num}: Starting 'check_excel_exists'.")
            
            if not os.path.exists(self.filepath):
                self.logger.error(f"Step {step_num}: Excel file not found at: {self.filepath}")
                return False, f"Excel file not found at: {self.filepath}"
            
            self.logger.info(f"Step {step_num}: Excel file confirmed to exist at: {self.filepath}.")
        except Exception as e:
            error_message = f"Step {step_num}: search_po_num failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환   
    
    def compare_with_json(self, step_num:int, step: Step):
        try:
            time.sleep(1)   

            # json_list 제공되지 않았을 경우 처리
            if not getattr(step, 'target_codes', None):
                error_message = f"Step {step_num}: JSON 리스트가 step 데이터에 없습니다."
                self.logger.error(error_message)
                return False, error_message  # 에러를 반환하고 실행 중단

            json_list = step.target_codes
            print(f"json_list: {json_list}")
            self.logger.debug(f"Step {step_num}: JSON 리스트 : \n {step.target_codes}")

            time.sleep(1)   
            combined_data = self.read_column_data(step_num, step)  # 데이터 읽기
            print(f"combined_data: \n{combined_data}")
            self.logger.debug(f"Step {step_num}: combined_data : \n {combined_data}")

            time.sleep(1)
            
            # target_codes와 combined_data를 비교하여 일치하는 인덱스와 데이터를 추출
            matching_data = []
            
            for target in json_list:
                target_activity, target_material_code, target_quantity = [str(item).strip() for item in target]
                
                # combined_data에서 일치하는 항목 찾기
                for index, activity, material_code, quantity in combined_data:
                    # 모든 값을 문자열로 변환하고 공백을 제거한 후 비교
                    if (str(activity).strip() == target_activity and 
                        str(material_code).strip() == target_material_code and 
                        str(quantity).strip() == target_quantity):
                        
                        matching_data.append((index, activity, material_code, quantity))
            
            if not matching_data:
                self.logger.info(f"Step {step_num}: No matching items found in column '{step.read_column}'.")
                return False, f"Step {step_num}: No matching items found in column '{step.read_column}'."
            
            print(f"matching_data: \n {matching_data}")
            
            self.logger.info(f"Step {step_num}: Found {len(matching_data)} matching items: {matching_data}")
            return matching_data  # 성공적으로 매칭된 결과 반환return matches
        
        except Exception as e:
            error_message = f"Step {step_num}: compare_with_json failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환

    def read_column_data(self, step_num:int, step: Step):
        try:
            time.sleep(1)
            self.logger.info(f"Step {step_num}: Reading Excel file from {self.filepath}")
            
            df = pd.read_excel(self.filepath, header=0, engine='openpyxl')
            self.logger.debug(f"Step {step_num}: Excel file loaded into DataFrame: \n{df}")
            time.sleep(3)
            
            #! 수정됨 (액티비티(2), 자재코드(4), BOM수량(7) 열 입력)
            read_column = [2,4,7]
            activity = read_column[0]
            material_code = read_column[1]
            quantity = read_column[2]
            
            #! 각 열 데이터를 리스트로 변환 후 공백 제거
            activity_list = df.iloc[:, activity].astype(str).apply(str.strip).tolist()
            material_code_list = df.iloc[:, material_code].astype(str).apply(str.strip).tolist()
            quantity_list = df.iloc[:, quantity].astype(str).apply(str.strip).tolist()
            
            #! 엑셀 인덱스와 결합하여 하나의 리스트로 묶음
            index_list = df.index.tolist()
            combined_data = list(zip(index_list, activity_list, material_code_list, quantity_list))
            
            return combined_data
                        
            # #? read_column 타입 확인하기
            # self.logger.debug(f"Type of step.read_column: {type(step.read_column)}")
            # #? 열 인덱스가 데이터프레임의 열 범위 내에 있는지 확인
            # if step.read_column < 0 or step.read_column >= len(df.columns):
            #     self.logger.error(f"Step {step_num}: Column index {step.read_column} is out of range.")
            #     return False, f"Step {step_num}: Column index {step.read_column} is out of range."
            # self.logger.info(f"Step {step_num}: 'P/O품번' Column index '{step.read_column}' found in the DataFrame.")
            # #? 열 데이터 추출 후 문자열로 변환
            # column_data = df.iloc[:, step.read_column].astype(str).tolist() # iloc: pandas의 인덱싱 함수로, 위치 기반 인덱싱
            # #? 데이터 정규화 및 검증
            # 1. 양쪽 공백 제거
            # column_data = [ item.strip() for item in column_data ]
            # self.logger.info(f"Step {step_num}: Extracted a total of {len(column_data)} entries from column 'P/O품번' (index {step.read_column}).")
            # time.sleep(1)
            # #? 최종 데이터 반환
            # return column_data # 리스트 형식
        
        except Exception as e:
            error_message = f"Step {step_num}: read_column_data failed: {str(e)}"
            self.logger.error(error_message)
            return None, error_message  # 작업이 실패한 경우 None과 오류 메시지 반환

    def move_to_target_and_perform_action(self, step_num:int, step:Step, matching_data=None):
        try:
            time.sleep(3)   
            self.logger.info(f"Step {step_num}: Starting 'move_to_target_and_perform_action'.")
            
            PyAutoGuiHelper.perform_click(step.pos_start) # 시작위치로 이동
            self.logger.info(f"Step {step_num}: Move to start position at {step.pos_start}.")

            start_index = 0
            
            # matching_data에서 인덱스 값만 추출
            target_indices = [data[0] for data in matching_data]
            
            time.sleep(1)  
            for target_index in target_indices:
                time.sleep(1)
                self.logger.info(f"Step {step_num}: Moving from index {start_index} to {target_index}.")  
                
                # 인덱스로 이동 
                PyAutoGuiHelper.move_to_index(start_index, target_index)
                self.logger.info(f"Step {step_num}: move_to_index [%d] from [%d]", start_index, target_index)
                time.sleep(1)
                
                # 키보드 조작
                pyautogui.hotkey('shift', 'tab')
                self.logger.debug(f"Step {step_num}: Pressed 'shift + tab' to move to checkbox.")
                time.sleep(0.5)  # 키보드 명령어의 간격 조절 
                
                pyautogui.press('space')
                self.logger.debug(f"Step {step_num}: Pressed 'space' to toggle checkbox.")
                time.sleep(0.5) 
                
                pyautogui.press('tab')
                self.logger.debug(f"Step {step_num}: Pressed 'tab' to move to the next field.")
                time.sleep(0.5)  
                
                # 입고 예정일 입력
                self.logger.info(f"Step {step_num}: Writing inbound date '{step.inbound_date}' at target index {target_index}.")

                pyperclip.copy(step.inbound_date)
                self.logger.info(f"Step {step_num}: Search term '{step.inbound_date}' copied to clipboard.")
                time.sleep(0.5)
                
                # 입력란 클릭 후 'inbound_data' 입력
                pyautogui.hotkey('ctrl', 'v')
                self.logger.info(f"Step {step_num}: Search term pasted from clipboard.")
                time.sleep(0.5)

                start_index = target_index
                time.sleep(1)
            
            time.sleep(3)
                
            self.logger.info(f"Step {step_num}: Action performed on all {matches} targets successfully.")
            return True, f"Step {step_num}: Action performed on all {matches} targets successfully."
            
        except Exception as e:
            error_message = f"Step {step_num}: move_to_target_and_perform_action failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환

    ############################################# step_4 #############################################

    def generate_pallet(self, step_num:int, step: Step):
        try:
            time.sleep(3)   
            self.logger.info(f"Step {step_num}: Starting 'generate_pallet'.") 
            
            # '팔레트생성'버튼 클릭
            PyAutoGuiHelper.perform_click(step.pos_pallet_btn)
            self.logger.info(f"Step {step_num}: Clicking 'Pallet 생성' button at position {step.pos_pallet_btn}.")
            
            #? 대기 예상
            time.sleep(5)
            
            success_texts = ["하시겠습니까?"]
            
            success, detected_text = PopupManager.process_popup(
                success_texts,
                'pallet_creation'
            )
            
            time.sleep(1)
            
            if success:
                self.logger.debug(f"Step {step_num}: process 'Pallet생성' popup result - success: {success}, detected_text: {detected_text}")   
                PyAutoGuiHelper.perform_click(step.pos_yes_btn)
                self.logger.info(f"Step {step_num}: Clicking '예' button at position {step.pos_yes_btn}. / pos_yes_btn: {step.pos_yes_btn}")
            else:
                self.logger.debug(f"Step {step_num}: Failed to process popup. Last detected text: '{detected_text.strip()}'.")
                return False, f"Failed to process 'Pallet생성' popup. Last detected text: '{detected_text.strip()}'."

            # 로딩 감지
            time.sleep(3)   
            success, message = self.detect_loading(step_num, step)
            self.logger.debug(f"Step {step_num}: Loading detect_loading result - success: {success}, message: {message}")  
            if not success:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}: Loading detection failed, \n Waiting for 15 seconds before retry...")
                    time.sleep(15)
                else:
                    return False, message
            time.sleep(5)
            
            
            # 입력완료 클릭
            self.logger.info(f"Step {step_num}: Clicking '입력완료' button at position {step.pos_btn_1}.")
            PyAutoGuiHelper.perform_click(step.pos_btn_1)
            
            time.sleep(3)
            
            # Pallet생성 이(가) 완료되었습니다. Pallet번호 을(를) 조회조건에 복사하시겠습니까? -> "예"
            self.logger.info(f"Step {step_num}: Clicking 'Pallet 번호 복사' confirmation button at position {step.pos_btn_2}.")
            PyAutoGuiHelper.perform_click(step.pos_btn_2)
            time.sleep(3)   
            
            # 로딩 감지
            time.sleep(3)   
            success, message = self.detect_loading(step_num, step)
            self.logger.debug(f"Step {step_num}: Loading detect_loading result - success: {success}, message: {message}")  
            if not success:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}: Loading detection failed, \n Waiting for 15 seconds before retry...")
                    time.sleep(15)
                else:
                    return False, message
            time.sleep(5)
            
            
            # PO정보에 조회된 자료가 없습니다 (TODO: 더미데이터에 한해서만 해당 팝업창 뜸)\
            self.logger.info(f"Step {step_num}: Clicking 'PO정보에 조회된 자료가 없습니다' confirmation button at position {step.pos_btn_3}.")
            PyAutoGuiHelper.perform_click(step.pos_btn_3)

            time.sleep(3)
            
            # 체크박스 모두 체크
            PyAutoGuiHelper.perform_click(step.all_checkbox)
            self.logger.info(f"Step {step_num}: Selecting all checkboxes at position {step.all_checkbox}.")
            time.sleep(1)
            
            # 납품예약 이동
            PyAutoGuiHelper.perform_click(step.deli_reserv_btn)  # 납품예약 이동
            self.logger.info(f"Step {step_num}: Clicking '납품 예약' button at position {step.deli_reserv_btn}.")
            
            # 로딩 감지
            time.sleep(3)   
            success, message = self.detect_loading(step_num, step)
            self.logger.debug(f"Step {step_num}: Loading detect_loading result - success: {success}, message: {message}")  
            if not success:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}: Loading detection failed, \n Waiting for 15 seconds before retry...")
                    time.sleep(15)
                else:
                    return False, message
            time.sleep(5)
            
            # 새창 로드 검증
            self.logger.info(f"Step {step_num}: Validating new window by double-clicking at position {step.pos_vali}.")
            PyAutoGuiHelper.perform_double_click(step.pos_vali) # 517,198
            time.sleep(0.5)
            pyautogui.hotkey('ctrl','c')
            time.sleep(0.5)
            
            # 클립보드 데이터 검증
            clipboard_data_reserv = pyperclip.paste()
            self.logger.debug(f"Step {step_num}: Clipboard data: {clipboard_data_reserv}")

            # "(주)케이씨" 문자열 확인
            matched_str = "(주)케이씨"
            if matched_str in clipboard_data_reserv:
                self.logger.info(f"Step {step_num}: New window validation successful, partner matched: (주)케이씨.")
                return True, "Pallet generated and validated successfully."  # 작업이 성공적으로 완료됨
            
            else : 
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}: New window failed to load correctly. '{matched_str}' not found. \n Waiting for 15 seconds before retry...")
                    time.sleep(15)  # 15초 대기     
                    return True, "Pallet generated and validated successfully." 
                else: 
                    self.logger.error(f"Step {step_num}: New window failed to load correctly. '{matched_str}' not found.")
                    return False, "Failed to load the delivery reservation window"
        
        except Exception as e:
            error_message = f"Step {step_num}: generate_pallet failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환

                
    ############################################# step_5 #############################################
        
    def input_vehicle_information(self, step_num:int, step:Step):
        try: 
            self.logger.info(f"Step {step_num}: Starting 'input_vehicle_information'.")
            time.sleep(3)
            
            # 직사급여부 : 직납 체크
            self.logger.debug(f"Step {step_num}: Clicking '직납' at position {step.pos_direct_deli}.")
            PyAutoGuiHelper.perform_click(step.pos_direct_deli)
            time.sleep(1)
            
            # 차량정보 : 차량입력 
            self.logger.debug(f"Step {step_num}: Clicking '차량입력' at position {step.pos_vehicle_info}.")
            PyAutoGuiHelper.perform_click(step.pos_vehicle_info)
            self.logger.debug(f"Step {step_num}: Waiting for popup to load default options.")
            
            time.sleep(5) # 팝업창이 뜰때 옵션 디폴트값이 지정되어있음 시간 필요!
            
            # 납품구분 : Yard 납품
            self.logger.debug(f"Step {step_num}: Selecting 'Yard 납품' at position {step.pos_deli_Type}.")
            PyAutoGuiHelper.perform_click(step.pos_deli_Type)
            time.sleep(1)
            # 차량정보 : 정기 출입차량 관리
            self.logger.debug(f"Step {step_num}: Clicking '정기 출입차량 관리' at position {step.pos_reg_vehicle_Manag}.")
            PyAutoGuiHelper.perform_click(step.pos_reg_vehicle_Manag) 
            time.sleep(1)
            # 체크박스 체크
            self.logger.debug(f"Step {step_num}: Selecting checkbox at position {step.pos_checkbox}.")
            PyAutoGuiHelper.perform_click(step.pos_checkbox) 
            time.sleep(1)
            # 확인 버튼_1
            self.logger.debug(f"Step {step_num}: Clicking first '확인' button at position {step.pos_confirm_btn_1}.")
            PyAutoGuiHelper.perform_click(step.pos_confirm_btn_1)
            time.sleep(1)
            # 확인 버튼_2
            self.logger.debug(f"Step {step_num}: Clicking second '확인' button at position {step.pos_confirm_btn_2}.")
            PyAutoGuiHelper.perform_click(step.pos_confirm_btn_2)
            
            self.logger.info(f"Step {step_num}: 'input_vehicle_information' completed successfully.")
            
            return True, f"Step {step_num}: 'input_vehicle_information' completed successfully."  # 작업이 성공적으로 완료됨
        
        except Exception as e:
            error_message = f"Step {step_num}: move_to_target_and_perform_action failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환

        
    ############################################# step_6 #############################################  
    #! 5번째 행 이후부터 홀수 행 클릭시 그룹화됨 (5,6 그룹 / 7,8 그룹)
    #! 개별 작업이 아님
    
    #! 엑셀 데이터로 비교
    def reserve_delivery(self, step_num:int, step:Step):
        try: 
            time.sleep(3)
            self.logger.info(f"Step {step_num}: Starting 'reserve_delivery'.")
            
            # 엑셀 아이콘 클릭
            PyAutoGuiHelper.perform_click((1793,459)) 
            self.logger.info(f"Step {step_num}: Excel icon clicked successfully at position / pos_excel_icon: (1793,459)")
            
            PyAutoGuiHelper.perform_click((920,584))
            self.logger.info(f"Step {step_num}: Save button clicked successfully at position / pos_excel_save: (920,584)")
            
            # 로딩
            time.sleep(5)

            # [파일 디렉토리+파일이름+날짜+시간] 엑셀 저장
            file_directory = PathHelper.get_abs_path('reports','직납직사급납품예약')
            filename = PyAutoGuiHelper.generate_filename("직납_직사급_납품예약", "xlsx")
            self.logger.debug(f"Step {step_num}: Generated filename is {filename}.")
            
            time.sleep(1)
            reserv_filepath = os.path.join(file_directory, filename)
            self.logger.info(f"Step {step_num}: File path constructed: {reserv_filepath}.")
            
            time.sleep(1)
            PyAutoGuiHelper.save_file_with_name(reserv_filepath)
            self.logger.info(f"Step {step_num}: Excel file saved successfully as {reserv_filepath}.")
            
            # 파일 저장중........
            time.sleep(8)   
            self.logger.debug(f"Step {step_num}: Waiting for 3 seconds after saving file.")
            
            # 파일 존재 확인
            if not os.path.exists(reserv_filepath):
                time.sleep(1) 
                self.logger.error(f"Step {step_num}: Excel file not found at: {reserv_filepath}")
                return False, f"Excel file not found at: {reserv_filepath}"

            #! 엑셀파일 읽어서 행 갯수 구하기
            df = pd.read_excel(reserv_filepath, header=0, engine='openpyxl')
            self.logger.debug(f"Step {step_num}: Excel file loaded into DataFrame.")
            
            #! pallet번호 열에서 중복된 인덱스 제거, 첫번째 인덱스만 남기기
            unique_df = df.drop_duplicates(subset=['Pallet번호'], keep='first')
            self.logger.debug(f"Step {step_num}: Unique rows based on Pallet번호 obtained: {len(unique_df)}")
            
            #! 고유 인덱스와 pallet번호 튜플로 묶어 리스트 생성
            unique_indices = unique_df.index.tolist()
            unique_pallet_numbers = unique_df['Pallet번호'].tolist()
            
            #! 인덱스와 Pallet번호 값을 튜플로 묶기
            index_value_pairs = list(zip(unique_indices, unique_pallet_numbers))
            self.logger.debug(f"Step {step_num}: Index-Value pairs of unique Pallet번호: {index_value_pairs}")

            self.index_value_pairs = index_value_pairs
                    
            current_index = 0 # 초기 시작 인덱스를 0으로 가정
            # 리스트의 총 개수만큼 반복
            for index, value in index_value_pairs:
                self.logger.debug(f"Processing Pallet번호: {value} at index: {index}")
                
                time.sleep(0.5)
                # 시작위치로 이동 (첫번째 pallet번호 셀 중심)
                # PyAutoGuiHelper.perform_click(step.pos_start)
                PyAutoGuiHelper.perform_click((325, 524))
                self.logger.debug(f"Step {step_num}: Moving to start position (325, 524)")
                
                # 현재 인덱스에서 목표 인덱스로 이동
                PyAutoGuiHelper.move_to_index(current_index, index)
                self.logger.debug(f"Moving to checkbox at index {index}")

                # 체크박스로 이동
                pyautogui.hotkey('shift', 'tab')
                self.logger.debug(f"Step {step_num}: Moving to checkbox")

                #! 체크박스 체크
                pyautogui.press('space')
                
                time.sleep(0.5)

                # 납품예약 버튼 클릭
                PyAutoGuiHelper.perform_click(step.pos_deli_reserv_btn) #435,458
                self.logger.info(f"Step {step_num}: Clicking '납품 예약' button at position {step.pos_deli_reserv_btn}.")
                
                # 로딩 감지
                time.sleep(3)
                
                # 팝업창이 뜨고 '닫기' 버튼 클릭
                PyAutoGuiHelper.perform_click(step.pos_popup_close_btn) #1116,634
                self.logger.debug(f"Step {step_num}: Clicking '닫기' button on the popup at position {step.pos_popup_close_btn}.")
                
                # 로딩
                time.sleep(3)
                success_texts = ["거래명세서를", "발행하시겠습니까?"]
                
                success, detected_text = PopupManager.process_popup(
                    success_texts,
                    'generate_invoice'
                )
                
                time.sleep(1)
                if success:
                    self.logger.debug(f"Step {step_num}: process '거래명세서발행' popup result - success: {success}, detected_text: {detected_text}")   
                    PyAutoGuiHelper.perform_click(step.pos_popup_no_btn)
                    self.logger.info(f"Step {step_num}: Clicking '아니오' button at position {step.pos_popup_no_btn}. / pos_popup_no_btn: {step.pos_popup_no_btn}")
                else:
                    self.logger.debug(f"Step {step_num}: Failed to process popup. Last detected text: '{detected_text.strip()}'.")
                    return False, f"Failed to process '납품예약'popup. Last detected text: '{detected_text.strip()}'."
                
                # 5초 대기
                time.sleep(3)
                
            self.logger.info(f"Step {step_num}: 'reserve_delivery' completed successfully for all matches.")    
            return True, "'reserve_delivery' completed successfully for all matches."  # 작업이 성공적으로 완료됨
        
        except Exception as e:
            error_message = f"Step {step_num}: reserve_delivery failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환

    
    ############################################# step_7 #############################################
    def print_invoice_and_details(self, step_num:int, step:Step):
        try: 
            # 모든 matches에 대해 작업이 완료된 후 거래명세서 발행 작업 수행
            self.logger.info(f"Step {step_num}: Starting 'print_invoice_and_details'.")
            time.sleep(3)

            # 시작위치로 이동
            PyAutoGuiHelper.perform_click(step.pos_start) #328,522
            self.logger.debug(f"Step {step_num}: Clicking start position at {step.pos_start}.")
            time.sleep(0.5)
            pyautogui.hotkey('shift', 'tab')
            self.logger.debug(f"Step {step_num}: Pressing 'shift + tab'.")
            
            time.sleep(1)
            
            current_index = 0 # 초기 시작 인덱스를 0으로 가정
            # 리스트의 총 개수만큼 반복
            for index, value in self.index_value_pairs:
                self.logger.debug(f"Processing Pallet번호: {value} at index: {index}")
                # 현재 인덱스에서 목표 인덱스로 이동
                PyAutoGuiHelper.move_to_index(current_index, index)
                # 현재 체크박스를 체크
                pyautogui.press('space')
                current_index = index
                time.sleep(0.5)

            time.sleep(1)
            self.logger.info(f"Step {step_num}: All checkboxes processed successfully.")

            
            # 거래명세서출력 버튼 클릭
            PyAutoGuiHelper.perform_click(step.pos_trns_btn) # 507,458
            self.logger.info(f"Step {step_num}: Clicking '거래명세서출력' button at {step.pos_trns_btn}.")
                        
            time.sleep(3)

            loading_manager = SuperLoadingManager()
            success, message = loading_manager.wait_for_loading_to_complete() 
            self.logger.debug(f"Step {step_num}: Loading detect_loading result - success: {success}, message: {message}")  
            if not success:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}: Loading detection failed, \n Waiting for 60 seconds before retry...")
                    time.sleep(60) 
                else:
                    return False, message  # 로딩 실패 시 반환
                
            
            # 모든 체크박스 클릭
            PyAutoGuiHelper.perform_click(step.pos_all_checkbox) # 696,470
            self.logger.info(f"Step {step_num}: Clicking '모든 체크박스' at {step.pos_all_checkbox}.")
            time.sleep(1)
            
            ################################################# 자재 TAG 클릭 및 처리
            PyAutoGuiHelper.perform_click(step.pos_tag_btn) # 1039,375
            self.logger.info(f"Step {step_num}: Clicking '자재 TAG' button at {step.pos_tag_btn}.")
            
            time.sleep(3)

            loading_manager = SuperLoadingManager()
            success, message = loading_manager.wait_for_loading_to_complete() 
            self.logger.debug(f"Step {step_num}: Loading detect_loading result - success: {success}, message: {message}")  
            if not success:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}: Loading detection failed, \n Waiting for 60 seconds before retry...")
                    time.sleep(60) 
                else:
                    return False, message  # 로딩 실패 시 반환
            
            # 닫기
            PyAutoGuiHelper.perform_click(step.pos_tag_close_btn) # 1422,909
            self.logger.info(f"pos_tag_close_btn: %s" % step.pos_tag_close_btn)
            
            time.sleep(3)

            
            #TODO################################################ 거래 명세서 출력 #TODO################################################
            PyAutoGuiHelper.perform_click(step.pos_trns_print_btn) # 737,373
            self.logger.info(f"Step {step_num}: Clicking '거래명세서 출력' button at {step.pos_trns_print_btn}.")
            
            time.sleep(3)

            loading_manager = SuperLoadingManager()
            success, message = loading_manager.wait_for_loading_to_complete() 
            self.logger.debug(f"Step {step_num}: Loading detect_loading result - success: {success}, message: {message}")  
            if not success:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}: Loading detection failed, \n Waiting for 60 seconds before retry...")
                    time.sleep(60) 
                else:
                    return False, message  # 로딩 실패 시 반환

            ################################################# 전체페이지 1부 인쇄
            PyAutoGuiHelper.perform_click(step.pos_trns_print_icon) # 520,169
            self.logger.info(f"Step {step_num}: Clicking '인쇄 아이콘' at {step.pos_trns_print_icon}.")
            
            # 대기
            time.sleep(3)
            
            PyAutoGuiHelper.perform_click(step.pos_trns_confirm_btn_1) # 1080,633
            self.logger.info(f"Step {step_num}: Clicking '확인' button for printing at {step.pos_trns_confirm_btn_1}.")
            
            time.sleep(5)
            
            ################################################# 창 닫기
            PyAutoGuiHelper.perform_click(step.pos_trns_close_btn) # 1422,909
            self.logger.info(f"Step {step_num}: Closing '거래명세서' window at {step.pos_trns_close_btn}.")
            
            time.sleep(1)
            
            PyAutoGuiHelper.perform_click(step.pos_trns_confirm_btn_2) # 1311,718
            self.logger.info(f"Step {step_num}: Clicking '확인' button to confirm close at {step.pos_trns_confirm_btn_2}.")
            
            time.sleep(3)
            
            #TODO################################################ 납품 상세 리스트 출력 #TODO################################################
            PyAutoGuiHelper.perform_click(step.pos_ddl_print_btn) # 596,457
            self.logger.info(f"Step {step_num}: Clicking '납품상세리스트 출력' button at {step.pos_ddl_print_btn}.")
            
            time.sleep(3)
            
            # 납품상세리스트 을(를) 출력 하시겠습니까?
            PyAutoGuiHelper.perform_click(step.pos_ddl_confirm_btn) # 1054,601
            self.logger.info(f"Step {step_num}: Confirming '납품상세리스트 출력 을(를) 출력 하시겠습니까?' at {step.pos_ddl_confirm_btn}.")
            
            # 로딩 감지
            time.sleep(3)   
            success, message = self.detect_loading(step_num, step)
            self.logger.debug(f"Step {step_num}: Loading detect_loading result - success: {success}, message: {message}")  
            if not success:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}: Loading detection failed, \n Waiting for 60 seconds before retry...")
                    time.sleep(60)
                else:
                    return False, message
            time.sleep(5)
            
            ################################################# 전체페이지 1부 인쇄
            PyAutoGuiHelper.perform_click(step.pos_ddl_print_icon_1) # 520,169
            self.logger.info(f"Step {step_num}: Clicking '인쇄 아이콘' at {step.pos_ddl_print_icon_1}.")
            time.sleep(3)
            
            PyAutoGuiHelper.perform_click(step.pos_ddl_confirm_btn_1) # 1080,633
            self.logger.info(f"Step {step_num}: Clicking '확인' button for printing at {step.pos_ddl_confirm_btn_1}.")
            
            time.sleep(5)
            
            ################################################# 4페이지 모아찍기 1부 인쇄
            PyAutoGuiHelper.perform_click(step.pos_ddl_print_icon_2) # 520,169
            self.logger.info(f"Step {step_num}: Clicking '인쇄 아이콘' at {step.pos_ddl_print_icon_2}.")
            time.sleep(3)
            
            PyAutoGuiHelper.perform_click(step.pos_ddl_page_options_2) # 1177,505 # 4페이지 옵션
            self.logger.info(f"Step {step_num}: Selecting '인쇄 옵션' at {step.pos_ddl_page_options_2}.")
            time.sleep(1)
            
            pyautogui.press('down', presses=2, interval=0.5) # 4페이지 모아찍기
            self.logger.debug(f"Step {step_num}: Pressing 'down' to select '4페이지 모아찍기'.")
            time.sleep(1)
            
            pyautogui.press('enter')
            self.logger.debug(f"Step {step_num}: Pressing 'enter' to confirm selection.")
            time.sleep(1)
            
            PyAutoGuiHelper.perform_click(step.pos_ddl_confirm_btn_2) # 1080,633
            self.logger.info(f"Step {step_num}: Clicking '확인' button for printing at {step.pos_ddl_confirm_btn_2}.")
            
            time.sleep(5)
            
            ################################################# 1페이지 모아찍기 1부
            PyAutoGuiHelper.perform_click(step.pos_ddl_print_icon_3) # 520,169
            self.logger.info(f"Step {step_num}: Clicking '1페이지 모아찍기' at {step.pos_ddl_print_icon_2}.")
            time.sleep(3)
            
            PyAutoGuiHelper.perform_click(step.pos_ddl_page_options_3) # 1177,505 # 1페이지 옵션
            self.logger.info(f"Step {step_num}: Selecting '인쇄 옵션' at {step.pos_ddl_print_icon_3}.")
            time.sleep(1)
            pyautogui.press('up', presses=2, interval=0.5) # 1페이지 모아찍기
            self.logger.debug(f"Step {step_num}: Pressing 'down' to select '4페이지 모아찍기'.")
            time.sleep(1)
            pyautogui.press('enter')
            self.logger.debug(f"Step {step_num}: Pressing 'enter' to confirm selection.")
            time.sleep(1)
            
            PyAutoGuiHelper.perform_click(step.pos_ddl_confirm_btn_3) # 1080,633
            self.logger.info(f"Step {step_num}: Clicking '확인' button for printing at {step.pos_ddl_confirm_btn_2}.")
            time.sleep(5)
            
            ################################################# 닫기 
            PyAutoGuiHelper.perform_click(step.pos_ddl_close_btn) # 1422,909
            self.logger.info(f"Step {step_num}: Closing '납품상세리스트출력' window at {step.pos_ddl_close_btn}.")
            time.sleep(5)
            
            self.logger.info(f"Step {step_num}: 'print_invoice_and_details' completed successfully.")
            return True, "print_invoice_and_details completed successfully."
        
        except Exception as e:
            error_message = f"Step {step_num}: print_invoice_and_details failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환

        
    ############################################# step_8 #############################################    
    def reset_for_po_number_search(self, step_num:int, step:Step):
        try:
            time.sleep(3)
            self.logger.info(f"Step {step_num}: Starting 'reset_for_po_number_search'.")
            pyautogui.click()
            time.sleep(1)
            
            # 모든 창 닫기
            self.logger.debug(f"Step {step_num}: Pressing 'alt + x' to close all windows.")
            pyautogui.hotkey('alt', 'x')
            time.sleep(1)
            
            # 모든 창 닫기
            self.logger.debug(f"Step {step_num}: Pressing 'alt + x' to close all windows.")
            pyautogui.hotkey('alt', 'x')
            time.sleep(1)

            # 상위 메뉴 탭 모두 닫기
            PyAutoGuiHelper.perform_click(step.pos_menu_tab)
            self.logger.info(f"Step {step_num}: Moving to '상위 모든 메뉴 탭 닫기' menu at {step.pos_menu_tab}.")
            time.sleep(1)
            
            self.logger.info(f"Step {step_num}: 'reset_for_po_number_search' completed successfully.")
            return True, "reset_for_po_number_search completed successfully."

        except Exception as e:
            error_message = f"Step {step_num}: reset_for_po_number_search failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message

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

def execute_hn_delv_proc(json_data: str):
    # 설정 파일을 미리 로드합니다.
    PathHelper.load_config()
    
    master_mode = PathHelper.get_config_value('master_mode', False)
    logger = LoggerManager.get_logger(__name__)
    loading = LoadingIconManager()
    res = ResponseManager()

    step_num = 0  # 초기화
    manager = HN_ReservationManager(json_data, res, logger, loading, master_mode)  
    
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