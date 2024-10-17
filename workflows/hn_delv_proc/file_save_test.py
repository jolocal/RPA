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

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),'../../'))

def save_pdf_file(po_no):
    # PDF 저장 경로 생성
    pdf_save_path = PathHelper.get_desktop_save_path('중국법인', po_no)
    print(f"PDF 파일을 저장할 경로: {pdf_save_path}")
    
    # PyAutoGuiHelper를 통해 PDF 파일로 저장
    PyAutoGuiHelper.save_file_with_name(pdf_save_path)
    print(f"파일이 성공적으로 저장되었습니다: {pdf_save_path}")

def some_method():

    PyAutoGuiHelper.perform_click((497,174))
    PyAutoGuiHelper.perform_click((994,584))


    # time.sleep(20)
    # # # 재시도 횟수 초과 시 종료 로직
    # # if not success:
    # #     if self.master_mode:
    # #         self.logger.debug(f"Step {step_num}: 마스터모드 활성화 - 최대 시도 횟수 초과, 시스템 종료를 시도합니다.")
    # #         pyautogui.hotkey('shift', 'q')  # 종료 단축키 시도
    # #     return False, "Maximum retry limit reached, process terminated."

    # # 파일 C:\Users\IPC\Desktop\RPA\처리완료\중국법인\20241008\p1235.pdf

    PyAutoGuiHelper.perform_double_click((834,579))
    po_no='p1235'
    save_pdf_file(po_no)
    PyAutoGuiHelper.perform_click((994,584))

if __name__ == "__main__":
    time.sleep(1)
    some_method()