import json
import os
import sys
import time
import pytesseract
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 루트 디렉토리 경로 설정
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),'../'))
sys.path.append(root_dir)

# 절대 경로를 사용하여 모듈을 불러옴
from common.logger_manager import LoggerManager
from common.response_manager import ResponseManager
from common.popup_manager import PopupManager
from common.loading_manager import LoadingIconManager
from common.utils.helper import PyAutoGuiHelper
from common.utils.keyboard_utils import CapslockHelper
from common.utils.path_utils import PathHelper

# sg_start_login.py에 있는 StartApp 클래스를 임포트
from workflows.sg_start_login import StartApp

# 예시 JSON 데이터를 준비합니다. 사용자가 직접 입력할 수 있습니다.
json_data = {
    "contexts": {
        "step_1": {
            "task": "start_application",
            "app_path": "C:/Program Files (x86)/TOBESOFT/XPLATFORM/9.2/XPlatform.exe -K SGIPS_PROD -X https://www.s-gips.co.kr/ep/ui/SHI_SGIPS_ITR.xadl"
        },
        "step_2": {
            "task": "login",
            "pos_user": [1177,48],
            "username_key": "A0003139A",
            "pos_token": [1285,48],
            "auth_token": "c7715cat@@",
            "pos_login_btn": [1360,50],
            "region_popup": [759,460,403,142],
            "region_confirm_btn": [937,569,46,19]
        },
        "step_3": {
            "task": "access_work_system",
            "pos_work_btn": [1417, 48],
            "region_popup": [0,0,799,798],
            "btn_offset": [21,10]
        }
    }
}

# JSON 데이터를 문자열로 변환
json_data_str = json.dumps(json_data)

# CW_ReqDueManager 객체를 생성합니다.
logger = LoggerManager.get_logger(__name__)
loading_manager = LoadingIconManager()
res = ResponseManager()
master_mode =  PathHelper.get_config_value('master_mode',False)

manager = StartApp(json_data_str, logger, loading_manager, res, master_mode)

# 원하는 스텝 넘버를 지정합니다.
step_num = 2
step = manager.contexts.step_2  # 원하는 스텝에 맞게 변경하세요.

# 개별 메서드를 호출하여 테스트합니다.
print("start")
manager.start_application(1, manager.contexts.step_1)
print("end")
time.sleep(1)
print("start")
manager.login(2, manager.contexts.step_2)
print("end")
time.sleep(1)
print("start")
manager.access_work_system(3, manager.contexts.step_3)
print("end")