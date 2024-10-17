import json
import os
import sys
import pytesseract
import time
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# 루트 디렉토리 경로 설정
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),'../../'))
sys.path.append(root_dir)

# 절대 경로를 사용하여 모듈을 불러옴
from common.logger_manager import LoggerManager
from common.response_manager import ResponseManager
from common.loading_manager import LoadingIconManager
from common.loading_icon_manager import SuperLoadingManager
from common.utils.path_utils import PathHelper
from common.ocr_popup_manager import PopupManager


from cw_req_due import CW_ReqDueManager


# 예시 JSON 데이터를 준비합니다. 사용자가 직접 입력할 수 있습니다.
json_data = {
    "contexts": {
        "step_1": {
            "task": "navigate_to_deliv_reserv_improv",
            "pos_global_search_input": [71, 93],
            "search_str":"개선",
            "pos_deliv_res": [902, 479],
            "pos_vali_1": [485, 198]
        },
        "step_2": {
            "pos_po_no": [684, 198],
            "task": "navigate_to_deliv_mng",
            "po_no": "P12XA03901",
            "pos_search_btn_1": [1083, 255],
            "pos_change_due_date_mng": [1833, 146],
            "pos_popup_confirm_btn_1": [1046, 600],
            "pos_vali_2": [1284, 158]
        },
        "step_3": {
            "task": "load_data_table",
            "pos_search_btn_2": [1083, 255],
            "pos_vali_3": [751, 439]
        },
        "step_4": {
            "task": "save_and_read_excel_data",
            "pos_excel_icon": [1792, 374],
            "pos_excel_save": [915, 578]
        },
        "step_5": {
            "task": "find_matching_rows",
            "part_no":  [
                "10","30","190","200","230"
            ],
            "read_column": 8
        },
        "step_6": {
            "task": "navigate_to_matching_rows",
            "pos_start": [815, 439]
        },
        "step_7": {
            "task": "input_negotiation_date",
            "pos_nego_due": [384, 343],
            "nego_due": "20240903",
            #! 추가
            "pos_confirm_btn": [1075,600]
        },
        "step_8": {
            "task": "input_incoming_goods_info",
            "pos_comment": [630, 343],
            "comment_str":"물품 입고 예정",
            "pos_copy_select_btn": [836, 342]
        },
        "step_9": {
            "task": "approve_changes",
            "pos_approve_btn": [1840, 108]
        },
        "step_10": {
            "task": "reset_for_po_number_search",
            #! 추가
            "pos_window_focus": [1563,95],
            "pos_menu_tab": [214,95]
        }
    }
}


# JSON 데이터를 문자열로 변환
json_data_str = json.dumps(json_data)
master_mode = PathHelper.get_config_value('master_mode',False)
# CW_ReqDueManager 객체를 생성합니다.
logger = LoggerManager.get_logger(__name__)
loading = LoadingIconManager()
super_loading_manager = SuperLoadingManager()
res = ResponseManager()
manager = CW_ReqDueManager(json_data_str, res, logger, super_loading_manager, loading, master_mode)

# 원하는 스텝 넘버를 지정합니다.
step_num = 2
step = manager.contexts.step_2  # 원하는 스텝에 맞게 변경하세요.

# 개별 메서드를 호출하여 테스트합니다.
time.sleep(3)
print("1- start")
manager.navigate_to_deliv_reserv_improv(1, manager.contexts.step_1)
print("1- end")
print("2- start")
manager.navigate_to_deliv_mng(2, manager.contexts.step_2)
print("2- end")
print("3- start")
manager.load_data_table(3, manager.contexts.step_3)
print("3- end")
print("4- start")
manager.save_and_read_excel_data(4, manager.contexts.step_4)
print("4- end")
print("5- start")
manager.find_matching_rows(5, manager.contexts.step_5)
print("5- end")
print("6- start")
manager.navigate_to_matching_rows(6, manager.contexts.step_6)
print("6- end")
print("7- start")
manager.input_negotiation_date(7, manager.contexts.step_7)
print("7- end")
print("8- start")
manager.input_incoming_goods_info(8, manager.contexts.step_8)
print("8- end")
print("9- start")
manager.approve_changes(9, manager.contexts.step_9)
print("9- end")
print("10- start")
manager.reset_for_po_number_search(10, manager.contexts.step_10)
print("10- end")