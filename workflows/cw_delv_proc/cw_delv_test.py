import json
import os
import sys
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
from common.utils.helper import PyAutoGuiHelper
from common.utils.keyboard_utils import CapslockHelper
from common.utils.path_utils import PathHelper


from cw_delv_inv import CW_ReservationManager


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
            "task": "load_po_table_data",
            "pos_po_no": [684, 198],
            # "po_no": "P13PA00030",
            "po_no": "P137A02138",
            "pos_search_btn_1": [1083, 255],
            "region_table": [253,448,1644,249]
        },
        "step_3":{
            "task": "input_vehicle_information",
            "pos_vehicle_info": [347,751],
            "pos_deli_Type": [687,431],
            "pos_reg_vehicle_Manag": [713,631],
            "pos_checkbox":[708,464],
            "pos_confirm_btn_1": [1173,720],
            "pos_confirm_btn_2": [1274,794],
            "pos_infopop_close_btn": [1426,870]
        },
        "step_4":{
            "task": "save_and_verify_excel",
            "pos_excel_icon": [1794,497],
            "pos_excel_save": [915,579]
        },
        "step_5":{
            "task": "find_matching_rows",
            "po_data_list": [
                    ["230","SN2655HB200PUUF300",6],
                    ["240","SN2655HB200SUUF300",6],
                    ["480","SN2655HF513PUUF200",1],
                    ["290","SN2655HF513SUUF200",1]
                    # ["50","SN2642HB121PUUF100",30],
                    # ["60","SN2642HB121PUUF100",25],
                    # ["90","SN2642HB141PUUF100",28],
                    # ["100","SN2642HB141PUUF100",23],
                    # ["110","SN2642HB151PUUF100",34],
                    # ["120","SN2642HB151PUUF100",28],
                    # ["390","SN2642HF11APUUF100",3],
                    # ["400","SN2642HF11APUUF100",3],
                    # ["700","SN2642HS121PUUF100",15],
                    # ["710","SN2642HS121PUUF100",15],
                    # ["720","SN2642HS131PUUF100",18],
                    # ["730","SN2642HS131PUUF100",18],
                ],
            "read_columns": [0,3,12]
        },
        "step_6":{
            "task": "navigate_to_matcing_rows",
            "pos_start": [1753,555]
        },
        "step_7":{
            "task": "reserve_delivery",
            "pos_deli_reserv_btn":[352,490],
            "pos_popup_ok_btn":[1046,600],
            "pos_all_checkbox":[695,469],
            "pos_tag":[1038,375],
            "pos_popup_close_btn_2":[1422,909]
        },
        "step_8":{
            "task": "print_invoice",
            "pos_trns_btn":[737,373],
            "pos_trns_print_icon":[520,169],
            "pos_trns_confirm_btn_1":[1079,634],
            "pos_trns_close_btn":[1422,909],
            "pos_trns_confirm_btn_2":[1311,710]
        },
        "step_9":{
            "task": "reset_for_po_number_search",
            "pos_window_focus":[1563,95],
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
res = ResponseManager()
manager = CW_ReservationManager(json_data_str, res, logger, loading, master_mode)


# 원하는 스텝 넘버를 지정합니다.
step_num = 2
step = manager.contexts.step_2  # 원하는 스텝에 맞게 변경하세요.

# 개별 메서드를 호출하여 테스트합니다.

print("1- start")
manager.navigate_to_deliv_reserv_improv(1, manager.contexts.step_1)
print("1- end")

print("2 - start")
manager.load_po_table_data(2, manager.contexts.step_2)
print("2- end")

print("3 - start")
manager.input_vehicle_information(3, manager.contexts.step_3)
print("3- end")

print("4 - start")
manager.save_and_verify_excel(4, manager.contexts.step_4)
print("4- end")

print("5 - start")
manager.find_matching_rows(5, manager.contexts.step_5)
print("5- end")

print("6 - start")
manager.navigate_to_matching_rows(6, manager.contexts.step_6)
print("6- end")

print("7 - start")
manager.reserve_delivery(7, manager.contexts.step_7)
print("7- end")

print("8 - start")
manager.print_invoice(8, manager.contexts.step_8)
print("8- end")

print("9 - start")
manager.reset_for_po_number_search(9, manager.contexts.step_9)
print("9- end")