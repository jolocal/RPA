from pywinauto.application import Application
import pyautogui
import time
import json
import traceback
import sys
import os
import threading
import keyboard

from typing import Tuple,Optional
from dataclasses import dataclass

import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 루트 디렉토리 경로 설정 (src 경로로 설정)
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(root_dir)

# 절대 경로를 사용하여 모듈을 불러옴
from common.logger_manager import LoggerManager
from common.response_manager import ResponseManager
from common.popup_manager import PopupManager
from common.loading_manager import LoadingIconManager
from common.utils.helper import PyAutoGuiHelper
from common.utils.keyboard_utils import CapslockHelper
from common.utils.path_utils import PathHelper
from common.ocr_popup_large_manager import PopupManager as LargePopupManager
from common.loading_icon_manager import SuperLoadingManager

@dataclass
class Step:
    task: str = ""
    app_path: str = ""
    username_key: str = ""
    auth_token: str = ""
    
    pos_user: Tuple[int, int] = (0,0)
    pos_token: Tuple[int, int] = (0,0)
    pos_login_btn: Tuple[int, int] = (0,0)
    region_popup: Optional[Tuple[int, int, int, int]] = None
    region_confirm_btn: Optional[Tuple[int, int, int, int]] = None
    
    pos_work_btn: Tuple[int, int] = (0,0)
    btn_offset: Tuple[int, int] = (0,0)

@dataclass
class Contexts:
    step_1: Step
    step_2: Step
    step_3: Step

class StartApp:
    def __init__(self, json_data: str, logger, super_loading_manager, loading_manager, large_popup_manager, res, master_mode:bool = False):
        # JSON 문자열에서 백슬래시 문자를 두 번으로 바꿉니다.
        json_data = json_data.replace('\\', '\\\\')
        self.data = json.loads(json_data)
        
        self.logger = logger
        self.super_loading_manager = super_loading_manager
        self.loading_manager = loading_manager
        self.large_popup_manager = large_popup_manager
        self.res = res
        
        self.main_window = ""
        self.app = None
        
        self.master_mode = master_mode
        print(f"master_mode in StartApp: {self.master_mode}")
        logger.debug(f"master_mode in StartApp: {self.master_mode}")

        #! 초기화 이후 모니터링 시작
        self.stop_signal = False  # stop_signal 초기화
        self.terminated = False 
        self.start_input_monitoring() # 키 입력 감지 시작
        
        # JSON 데이터를 Context 객체로 변환
        self.contexts = Contexts(
            step_1 = Step(**self.data['contexts']['step_1']),
            step_2 = Step(**self.data['contexts']['step_2']),
            step_3 = Step(**self.data['contexts']['step_3'])
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
            'start_application' : self.start_application,
            'login': self.login,
            'access_work_system': self.access_work_system
        }
        
        try:
            if step.task in task_map:
                # 작업 실행 후 결과를 확인
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

    def start_application(self, step_num: int, step: Step):
        try:
            time.sleep(5)
            self.logger.info(f"Step {step_num}: Starting application with path: {step.app_path}.")
            
            # 앱 실행
            self.app = Application(backend="uia")
            self.app.start(f"{step.app_path}")
            
            self.main_window = self.app.window(title="s-Gips")
            
            self.logger.info(f"Step {step_num}: 애플리케이션 시작")
            time.sleep(5)
            
            # 창이 나타나고 준비될 때까지 최대 3번 재시도
            for attempt in range(3):
                if self.main_window.wait('ready', timeout=180):  # 'ready' 상태는 창이 사용자 입력을 받을 준비가 된 상태를 의미
                    self.logger.info(f"Step {step_num}: 메인 윈도우 창이 준비되었습니다.")
                    self.main_window.set_focus()
                    
                    time.sleep(5)
                    self.logger.info(f"Step {step_num}: 애플리케이션이 성공적으로 시작되었습니다.")
                    return True, "Application started successfully."
                else:
                    self.logger.info(f"Step {step_num}: 메인 윈도우 창 로드 실패, 재시도 횟수: {attempt + 1}/3")
                    time.sleep(3)
                    
            # 3번의 시도가 모두 실패한 경우, master_mode 활성화
            if self.master_mode:
                self.logger.error(f"Step {step_num}: 3번의 재시도 끝에도 메인 창이 준비되지 않았습니다. master_mode를 활성화합니다.")
                time.sleep(5)  # master_mode 활성화 후 대기 시간
                if self.main_window.wait('ready', timeout=180):
                    self.logger.info(f"Step {step_num}: master_mode 활성화 후 메인 창이 준비되었습니다.")
                    self.main_window.set_focus()
                    time.sleep(5)  # 애플리케이션 안정화를 위한 추가 대기 시간
                    return True, "애플리케이션이 master_mode로 성공적으로 시작되었습니다."

            self.logger.debug(f"애플리케이션 로드 실패: 메인창이 준비되지 않았습니다.")
            return False, "Application load failed: window not ready."
        
        except Exception as e:
            error_message = f"Step {step_num}: Application start failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message
    
    def login(self, step_num:int, step:Step):
        try:
            #! JSON 데이터(아이디, 비밀번호) 확인
            if not getattr(step, 'username_key', None):
                self.logger.debug(f"Step {step_num}: 아이디 값이 없습니다. '기준정보' 파일이 열려있는지 확인해보세요. {step.username_key}")
                return False, f"Step {step_num}: username: {step.username_key}."
            if not getattr(step, 'auth_token', None):
                self.logger.debug(f"Step {step_num}: 비밀번호 값이 없습니다. '기준정보' 파일이 열려있는지 확인해보세요. {step.auth_token}")
                return False, f"Step {step_num}: auth_token: {step.auth_token}."
            
            self.logger.info(f"Step {step_num}: Starting login process with username: {step.username_key}.")     
                
            # 아이디 입력
            pyautogui.moveTo(step.pos_user)
            pyautogui.click()
            time.sleep(1)
            
            if CapslockHelper.is_capslock_on():
                self.logger.info(f"Step {step_num}: CapsLock is on. Turning it off.")
                CapslockHelper.turn_off_capslock()
                time.sleep(1)
                
            self.logger.info(f"Step {step_num}: Typing username.")
            CapslockHelper.type_with_shift(step.username_key) # 입력
            time.sleep(3)
            
            # 비밀번호 입력
            pyautogui.moveTo(step.pos_token)
            pyautogui.click()
            time.sleep(1)
            
            if CapslockHelper.is_capslock_on():
                self.logger.info(f"Step {step_num}: CapsLock is on. Turning it off.")
                CapslockHelper.turn_off_capslock()
                time.sleep(1)
                
            self.logger.info(f"Step {step_num}: Typing auth token.")
            CapslockHelper.type_with_shift(step.auth_token) # 입력
            time.sleep(3)
            
            # '로그인' 버튼 클릭
            self.logger.info(f"Step {step_num}: Clicking the login button.")
            PyAutoGuiHelper.perform_click(step.pos_login_btn)
            
            time.sleep(1)

            #!#!#!#!#!#!#!#!#!#! 로그인 팝업 감지 #!#!#!#!#!#!#!#!#!#!
            success_texts = ["최종접속시간", "IP"]
            success, detected_text = self.large_popup_manager.process_popup(
                                        success_texts,
                                        'login'
                                    )
            time.sleep(1)
            
            if success:
                self.logger.debug(f"Step {step_num}: process '로그인' popup result - success: {success}, detected_text: {detected_text}")   
                PyAutoGuiHelper.perform_click((959,578)) #! 수정필요 step.region_popup -> pos
                self.logger.info(f"Step {step_num}: '확인' 버튼 클릭 좌표:(959,578) / pos_ok_btn:(959,578)")
            else:
                self.logger.debug(f"Step {step_num}: '로그인' 팝업 감지 실패. 추출된 텍스트:'{detected_text.strip()}'")
                return False, f"Failed to process '로그인' popup. Last detected text: '{detected_text.strip()}'."

            # 안정화를 위한 대기 시간 추가
            time.sleep(1)
            
            return True, "Login completed successfully."  # 작업이 성공적으로 완료됨
            
        except Exception as e:
            error_message = f"Step {step_num}: Login failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환

            
    def access_work_system(self, step_num: int, step:Step):
        try:
            self.logger.info(f"Step {step_num}: Accessing work system.")
            
            # '업무시스템접속' 버튼 클릭
            self.logger.debug(f"Step {step_num}: Clicking on the 'work system access' button at position {step.pos_work_btn}.")
            pyautogui.moveTo(step.pos_work_btn)
            pyautogui.click()

            time.sleep(5)
            
            #!#!#!#!#!#!#!#!#!#! 업무시스템 접속시 로딩 감지 #!#!#!#!#!#!#!#!#!#!
            success, message = self.super_loading_manager.wait_for_loading_to_complete()
            self.logger.debug(f"Step {step_num}: '업무시스템 접속 로딩 감지' 결과 - success: {success}, message: {message}")  
            if not success:
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}:[마스터모드 활성화] 로딩 감지 실패, \n 30초 대기 시간 추가...")
                    time.sleep(30) 
                else:
                    return False, message  # 로딩 실패 시 반환

            self.logger.info(f"Step {step_num}: Detecting and closing popup if any.")
            close_btn_img = PathHelper.get_abs_path('src','templates','btn','close_btn.png')
            region = (0,0,917,853)
            
            success, message = PopupManager.detect_and_close_popup(close_btn_img, region=region)
            self.logger.debug(f"Step {step_num}: 업무시스템 접속 팝업 '닫기' 버튼 클릭 - success: {success}, message: {message}")    
            
            if not success:
                #! 공지사항 갯수에 맞춰 좌표값 추가 또는 삭제 필요함 
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}: [마스터모드 활성화] 팝업 '닫기'이미지 감지 실패, 예비 좌표 클릭 시작")
                    time.sleep(0.5)
                    PyAutoGuiHelper.perform_click((755,777))
                    time.sleep(0.5)
                    PyAutoGuiHelper.perform_click((640,775))
                    time.sleep(0.5)
                else:     
                    # 좌표 클릭하지 않고 false 반환        
                    time.sleep(0.5)
                    return False, message

            time.sleep(3)
            return True, "Work system accessed successfully."  # 작업이 성공적으로 완료됨
        
        except Exception as e:
            error_message = f"Step {step_num}: Work system access failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환   
    
    #########################################################################################
    
    def detect_loading(self, step_num: int, step: Step):
        try:
            if self.loading_manager.wait_for_loading_to_complete():
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
        self.res.add_contexts(step_num, task_name, "failed", error_message)
        
    #########################################################################################

def execute_sg_start_login(json_data: str):
    # 설정 파일을 미리 로드합니다.
    PathHelper.load_config() 
    
    master_mode =  PathHelper.get_config_value('master_mode',False) 
    logger = LoggerManager.get_logger(__name__)
    super_loading_manager = SuperLoadingManager()
    loading_manager = LoadingIconManager()
    large_popup_manager = LargePopupManager()
    res = ResponseManager()
    
    manager = StartApp(json_data, logger, super_loading_manager, loading_manager, large_popup_manager, res, master_mode)
    step_num = 0  # 초기화

    try:
        # 스텝 번호의 범위를 추출하고 각 스텝을 실행
        total_steps = len(manager.contexts.__annotations__)  # Contexts 클래스의 모든 스텝 필드를 카운트
        for step_num in range(1, total_steps + 1):
            step = getattr(manager.contexts, f'step_{step_num}')
            result = manager.execute_task(step_num, step)
            
            # 종료 신호가 설정되었는지 확인
            if manager.terminated:
                logger.info("Terminated by user input.")
                print("Terminated by user input.")
                return manager.force_terminate()
                
            if result is not None: # 실패 메시지가 반환되면 즉시 반환 및 종료
                logger.error(f"Error occurred at step {step_num}: {res.to_json()}")
                return res.to_json() # 현재까지의 상태와 함께 실패 응답을 반환
            
    except Exception as e:
        logger.error(f"Response on exception: {res.to_json()}")
        return res.to_json()  # 반환 후 함수 종료
    
    finally:
        manager.stop()  # 종료 시 호출하여 스레드 종료

    logger.debug(f"Process completed successfully. Response: {res.to_json()}")
    print(f"Process completed successfully. Response: {res.to_json()}")
    return res.to_json()  # 모든 스텝이 정상적으로 완료되었을 때의 반환