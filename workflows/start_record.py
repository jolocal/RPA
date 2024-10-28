from pywinauto.application import Application
import keyboard
import time
import json
import traceback
import sys
import os
import threading
from typing import Tuple
from dataclasses import dataclass
import psutil  # 프로세스 확인을 위해 추가

# 루트 디렉토리 경로 설정 (src 경로로 설정)
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(root_dir)

# 절대 경로를 사용하여 모듈을 불러옴
from common.logger_manager import LoggerManager
from common.response_manager import ResponseManager
from common.utils.path_utils import PathHelper

@dataclass
class Step:
    task: str = ""
    bdcam_path: str = ""
    record_key: str = ""

@dataclass
class Contexts:
    step_1: Step

class StartRecordManager:
    def __init__(self, json_data: str, logger, res, master_mode:bool = False):
        # JSON 문자열에서 백슬래시 문자를 두 번으로 바꿉니다.
        json_data = json_data.replace('\\', '\\\\')
        self.data = json.loads(json_data)
        
        self.logger = logger
        self.res = res
        
        self.master_mode = master_mode
        print(f"master_mode in StartRecordManager: {self.master_mode}")
        logger.debug(f"master_mode in StartRecordManager: {self.master_mode}")
        
        #! 초기화 이후 모니터링 시작
        self.stop_signal = False  # stop_signal 초기화
        self.terminated = False 
        self.start_input_monitoring() # 키 입력 감지 시작
        
        # JSON 데이터를 Context 객체로 변환
        self.contexts = Contexts(
            step_1 = Step(**self.data['contexts']['step_1'])
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
        return response  # 응답을 반환하여 LabVIEW로 전송
    
    def stop(self):
        # 프로그램 종료 시 호출되는 메서드
        self.stop_signal = True  # 스레드 종료를 위한 신호 설정
    
    #TODO#############################################################################################################

    def execute_task(self, step_num, step:Step):
        task_map = {
            'start_recording': self.start_recording
        }
        
        try:
            if step.task in task_map:
                success, message = task_map[step.task](step_num, step)
                
                if success:
                    self.res.add_contexts(step_num, step.task, "success", f"{step.task} executed successfully.")
                else:
                    self.res.add_contexts(step_num, step.task, "failed", message)
                    return message
            else:
                raise ValueError(f"Unknown task: {step.task}")
            
        except Exception as e:
            self.handle_task_exception(step_num, step.task, e)
            return str(e)
            
        return None

    def start_recording(self, step_num: int, step: Step):
        try:
            self.logger.info(f"Step {step_num}: 반디캠 실행")
            
            # 반디캠 프로세스가 이미 실행 중인지 확인
            bdcam_running = False
            for proc in psutil.process_iter(['name']):
                if 'bdcam' in proc.info['name'].lower():
                    bdcam_running = True
                    self.logger.info(f"Step {step_num}: 기존 반디캠 프로세스가 실행 중입니다.")
                    print("기존 반디캠 프로세스가 실행 중입니다.")
                    break
            
            if bdcam_running:
                # 기존 녹화 중지
                self.logger.info(f"Step {step_num}: 기존 녹화를 중지합니다.")
                print("기존 녹화를 중지합니다.")
                record_key = step.record_key if step.record_key else 'f12'
                keyboard.press_and_release(record_key)
                time.sleep(3)  # 녹화 종료 대기
                
                # 프로세스 종료
                for proc in psutil.process_iter(['name']):
                    if 'bdcam' in proc.info['name'].lower():
                        self.logger.info(f"Step {step_num}: 반디캠 프로세스를 종료합니다.")
                        print("반디캠 프로세스를 종료합니다.")
                        try:
                            proc.terminate()  # 프로세스 종료
                            proc.wait(timeout=10)  # 최대 10초 대기
                        except psutil.TimeoutExpired:
                            proc.kill()  # 강제 종료
                        time.sleep(3)  # 프로세스 종료 대기
                        break
            
            # 반디캠 실행 경로 설정
            bdcam_path = step.bdcam_path if step.bdcam_path else r'C:\Program Files\Bandicam\bdcam.exe'
            
            # 반디캠 실행
            Application(backend='uia').start(bdcam_path)
            time.sleep(5)  # 프로세스 시작 대기
            
            # 실행 후 프로세스 확인
            bdcam_started = False
            for _ in range(3):  # 3번 시도
                for proc in psutil.process_iter(['name']):
                    if 'bdcam' in proc.info['name'].lower():
                        bdcam_started = True
                        break
                if bdcam_started:
                    break
                time.sleep(2)
            
            if not bdcam_started:
                error_message = "반디캠 프로세스를 시작할 수 없습니다."
                self.logger.error(f"Step {step_num}: {error_message}")
                return False, error_message
            
            # 녹화 시작
            time.sleep(2)
            record_key = step.record_key if step.record_key else 'f12'
            keyboard.press_and_release(record_key)
            time.sleep(3)  # 녹화 시작 대기
            
            self.logger.info(f"Step {step_num}: 반디캠 녹화 시작")
            print(f"반디캠 녹화 시작")
            
            return True, "Recording started successfully."
            
        except Exception as e:
            error_message = f"Step {step_num}: Failed to start recording: {str(e)}"
            self.logger.error(error_message)
            return False, error_message

    def handle_task_exception(self, step_num, task_name: str, exception: Exception):
        error_message = f"Task '{task_name}' failed with error: {str(exception)}"
        detailed_traceback = traceback.format_exc()
        self.logger.error(f"{error_message}\n{detailed_traceback}")
        self.res.add_contexts(step_num, task_name, "failed", error_message)

def execute_start_record(json_data: str):
    # 설정 파일을 미리 로드합니다.
    PathHelper.load_config()
    
    master_mode = PathHelper.get_config_value('master_mode', False)
    logger = LoggerManager.get_logger(__name__)
    res = ResponseManager()
    
    manager = StartRecordManager(json_data, logger, res, master_mode)
    step_num = 0  # 초기화

    try:
        total_steps = len(manager.contexts.__annotations__)
        for step_num in range(1, total_steps + 1):
            step = getattr(manager.contexts, f'step_{step_num}')
            result = manager.execute_task(step_num, step)
            
            # 종료 신호가 설정되었는지 확인
            if manager.terminated:
                logger.info("Terminated by user input.")
                print("Terminated by user input.")
                return manager.force_terminate()
            
            if result is not None:
                logger.error(f"Error occurred at step {step_num}: {res.to_json()}")
                return res.to_json()
            
    except Exception as e:
        logger.error(f"Response on exception: {res.to_json()}")
        return res.to_json()
    
    finally:
        manager.stop()

    logger.debug(f"Process completed successfully. Response: {res.to_json()}")
    print(f"Process completed successfully. Response: {res.to_json()}")
    return res.to_json()
