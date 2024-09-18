from pywinauto.application import Application
import pywinauto
import pyautogui
import time
import json
import traceback
import sys
import os
import pytesseract
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
    def __init__(self, json_data:str, logger,loading_manager, res, master_mode:bool = False):
        """
        StartApp 초기화 메서드
        Args:
            json_data: JSON 형식의 데이터
            logger: 로거 객체
            loading_manager: 로딩 매니저 객체
            res: 응답 매니저 객체
            master_mode: 팝업 감지 실패 시 좌표를 클릭할지 여부를 결정하는 플래그
        """
        
        # JSON 문자열에서 백슬래시 문자를 두 번으로 바꿉니다.
        json_data = json_data.replace('\\', '\\\\')
        self.data = json.loads(json_data)
        
        self.logger = logger
        self.res = res
        self.loading_manager = loading_manager
        self.main_window = ""
        self.app = None
        self.master_mode = master_mode
        print(f"master_mode in StartApp: {self.master_mode}")
        logger.debug(f"master_mode in StartApp: {self.master_mode}")

        
        # JSON 데이터를 Context 객체로 변환
        self.contexts = Contexts(
            step_1 = Step(**self.data['contexts']['step_1']),
            step_2 = Step(**self.data['contexts']['step_2']),
            step_3 = Step(**self.data['contexts']['step_3'])
        )
        
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
            
            self.logger.info(f"Step {step_num}: Application started, waiting for the main window to be ready.")
            time.sleep(5)
            
            # 창이 나타나고 준비될 때까지 기다림
            if self.main_window.wait('ready', timeout=180):  # 'ready' 상태는 창이 사용자 입력을 받을 준비가 된 상태를 의미
                self.logger.info(f"Step {step_num}: Main window is ready.")
                self.main_window.set_focus()
                time.sleep(5)  # 애플리케이션 안정화를 위한 추가 대기 시간
            else:
                return False, "Application load failed: window not ready."

            return True, "Application started successfully."  # 작업이 성공적으로 완료됨
        
        except Exception as e:
            error_message = f"Step {step_num}: Application start failed: {str(e)}"
            self.logger.error(error_message)
            
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환
    
    def login(self, step_num:int, step:Step):
        try:
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
            
            # PyAutoGuiHelper.perform_click(step.pos_token) # 이동
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
            time.sleep(5)
            
            # 로그인 '팝업' 감지
            self.logger.info(f"Step {step_num}: Checking for login popups.")
            popup_success, message =  PopupManager.detect_and_handle_popup_with_ocr(
                                            self.master_mode,
                                            region_popup = step.region_popup,
                                            region_btn = step.region_confirm_btn,
                                            target_texts = ["최종접속시간", "IP"],
                                            failure_texts= ["FAILED", "로그인", "정보가","맞지 않습니다."],
                                            max_attempts = 5
                                        )
                                        
            if not popup_success:
                self.logger.error(f"Popup handling failed: {message}")
                return False, message  # 팝업 처리 실패 시 False와 오류 메시지 반환
            
            time.sleep(1)
            
            return True, "Login completed successfully."  # 작업이 성공적으로 완료됨
            
        except Exception as e:
            error_message = f"Step {step_num}: Login failed: {str(e)}"
            self.logger.error(error_message)
            return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환

            
    def access_work_system(self, step_num: int, step:Step):
        try:
            time.sleep(5)
            self.logger.info(f"Step {step_num}: Accessing work system.")
            
            # '업무시스템접속' 버튼 클릭
            self.logger.debug(f"Step {step_num}: Clicking on the 'work system access' button at position {step.pos_work_btn}.")
            pyautogui.moveTo(step.pos_work_btn)
            pyautogui.click()

            self.logger.debug(f"Step {step_num}: Waiting for 20 seconds for system stabilization.")
            
            time.sleep(10) # 안정화를 위한 대기 시간 추가
            
            # 로딩 감지
            success, message = self.detect_loading(step_num, step)
            self.logger.debug(f"Step {step_num}: Loading detect_loading result - success: {success}, message: {message}")  
            if not success:
                if self.click_on_fail:
                    self.logger.debug(f"Step {step_num}: Loading detection failed, \n Waiting for 5 seconds before retry...")
                    time.sleep(5)
                else:
                    return False, message
            time.sleep(5)

            self.logger.info(f"Step {step_num}: Detecting and closing popup if any.")
            close_btn_img = PathHelper.get_abs_path('src','templates','btn','close_btn.png')
            region = (0,0,917,853)
            
            popup_success, popup_message = PopupManager.detect_and_close_popup(close_btn_img, region=region)
            self.logger.debug(f"Step {step_num}: Loading detect_and_close_popup result - success: {success}, message: {message}")    
            
            if not popup_success:
                #! 공지사항 갯수에 맞춰 좌표값 추가 또는 삭제 필요함 
                if self.master_mode:
                    self.logger.debug(f"Step {step_num}: Popup detection failed, clicking fallback coordinates.")
                    time.sleep(1)
                    PyAutoGuiHelper.perform_click((755,777))
                    time.sleep(1)
                    PyAutoGuiHelper.perform_click((640,775))
                    time.sleep(1)
                else:     
                    # 좌표 클릭하지 않고 false 반환        
                    time.sleep(1)
                    return False, popup_message

            time.sleep(5)

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
    loading_manager = LoadingIconManager()
    res = ResponseManager()
    
    manager = StartApp(json_data, logger, loading_manager, res, master_mode)
    step_num = 0  # 초기화

    try:
        # 스텝 번호의 범위를 추출하고 각 스텝을 실행
        total_steps = len(manager.contexts.__annotations__)  # Contexts 클래스의 모든 스텝 필드를 카운트
        for step_num in range(1, total_steps + 1):
            step = getattr(manager.contexts, f'step_{step_num}')
            result = manager.execute_task(step_num, step)
            if result is not None: # 실패 메시지가 반환되면 즉시 반환 및 종료
                return res.to_json() # 현재까지의 상태와 함께 실패 응답을 반환
            
    except Exception as e:
        return res.to_json()  # 반환 후 함수 종료

    return res.to_json()  # 모든 스텝이 정상적으로 완료되었을 때의 반환