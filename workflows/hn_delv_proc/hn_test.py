import json
import os
import sys
import time
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# 루트 디렉토리 경로 설정
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),'../../'))
sys.path.append(root_dir)

# 절대 경로를 사용하여 모듈을 불러옴
from common.logger_manager import LoggerManager
from common.response_manager import ResponseManager
from common.popup_manager import PopupManager
from common.loading_manager import LoadingIconManager
from common.loading_icon_manager import SuperLoadingManager
from common.utils.helper import PyAutoGuiHelper
from common.utils.keyboard_utils import CapslockHelper
from common.utils.path_utils import PathHelper

from hn_delv_proc import HN_ReservationManager


json_data = {
    "contexts": {
        "step_1": {
            "task": "move_to_menu",
            "pos_material_tab":[75, 343],
            "pos_pallet_tab": [110, 680],
            "pos_vali": [480, 231]
        },
        "step_2": {
            "task": "search_po_num",
            "po_no": "P12XA03904",
            "pos_po": [443, 183],
            "pos_status": [1149, 182],
            "status_options": [
                [962, 228],
                [962, 250],
                [962, 273],
                [962, 295]
            ],
            "pos_search_btn": [1161, 313],
            "pos_popup_btn": [1075, 599] 
        },
        "step_3": {
            "task": "find_and_input_inbound_date",
            "pos_excel": [1175, 440],
            "pos_save_btn": [916, 580],
            #! 수정
            "read_column": 4,
            "pos_start": [724, 502],
            #! 수정
            "target_codes": [
                ["HH391PUUF200", "Q2471CT01ZL00001", "3"],
                ["HH391SUUF200","Q2471CT020L00001","3"],
                ["HH392PUUF200","Q2471CT01ZL00001","1"],
                ["HH392SUUF200","Q2471CT020L00001","1"]
            ],
            "inbound_date": "20240930"
        },
        "step_4": {
            "task": "generate_pallet",
            "pos_pallet_btn": [516, 410],
            #! pos_btn 좌표값 변경
            "pos_yes_btn":[1059,597],
            "pos_btn_1": [1260, 785],
            "pos_btn_2": [1046, 604],
            "pos_btn_3": [1075, 600],
            "all_checkbox": [266, 475],
            "deli_reserv_btn": [680, 413],
            "pos_vali": [484, 197]
        },
        "step_5": {
            "task": "input_vehicle_information",
            "pos_direct_deli": [563, 302],
            "pos_vehicle_info": [346, 719],
            "pos_deli_Type": [687, 430],
            "pos_reg_vehicle_Manag": [722, 631],
            "pos_checkbox": [708, 464],
            "pos_confirm_btn_1": [1173, 719],
            "pos_confirm_btn_2": [1273, 794]
        },
        "step_6": {
            "task": "reserve_delivery",
            "pos_start": [328, 522],
            "pos_deli_reserv_btn": [436, 457],
            "pos_popup_close_btn": [1115, 633],
            "pos_popup_no_btn": [1102, 600]
        },
        "step_7": {
            "task": "print_invoice_and_details",
            "pos_start": [328, 522],
            "pos_trns_btn":[501,458],
            "pos_all_checkbox":[695,470],
            "pos_tag_btn":[1039,375],
            #! pos_tag_print_icon 없어짐
            "pos_tag_close_btn":[1422,909],
            "pos_trns_print_btn":[737,373],
            "pos_ok_btn":[1003,569],
            "pos_trns_print_icon":[520,169],
            "pos_trns_confirm_btn_1":[1080,633],
            "pos_trns_close_btn":[1422,909],
            "pos_trns_confirm_btn_2":[1311,718],
            "pos_ddl_print_btn":[596,457],
            "pos_ddl_confirm_btn":[1054,601],
            
            "pos_ddl_print_icon_1":[520,169],
            "pos_ddl_confirm_btn_1":[1080,633],
            "pos_ddl_print_icon_2":[520,169],
            #! _2 로 수정됨
            "pos_ddl_page_options_2":[1177,505],
            "pos_ddl_confirm_btn_2":[1080,633],
            "pos_ddl_print_icon_3":[520,169],
            #! pos_ddl_page_options_3 추가됨
            "pos_ddl_page_options_3":[1177,505],
            "pos_ddl_confirm_btn_3":[1080,633],
            "pos_ddl_close_btn":[1422,909]
        },
        "step_8": {
            "task": "reset_for_po_number_search",
            "pos_pallet_tab": [375, 65],
            "pos_menu_tab":[214,95]
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
manager = HN_ReservationManager(json_data_str, res, logger, super_loading_manager, loading, master_mode)

# 원하는 스텝 넘버를 지정합니다.
step_num = 2
step = manager.contexts.step_2  # 원하는 스텝에 맞게 변경하세요.


# 개별 메서드를 호출하여 테스트합니다.
print("1 = start")
manager.move_to_menu(1, manager.contexts.step_1)
print("1 - end")

print("2 - start")
manager.search_po_num(2, manager.contexts.step_2)
print("2 - end")

print("3 - start")
manager.find_and_input_inbound_date(3, manager.contexts.step_3)
print("3 - end")

print("4 - start")
manager.generate_pallet(4, manager.contexts.step_4)
print("4 - end")

print("5 - start")
manager.input_vehicle_information(5, manager.contexts.step_5)
print("5 - end")

time.sleep(3)
print("6 - start")
manager.reserve_delivery(6, manager.contexts.step_6)
print("6 - end")

time.sleep(2)
print("7 - start")
manager.print_invoice_and_details(7, manager.contexts.step_7)
print("7 - end")

print("8 - start")
manager.reset_for_po_number_search(8, manager.contexts.step_8)
print("8 - end")

