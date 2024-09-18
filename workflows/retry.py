# 재시도 로직
import time
import os
import sys
import pyautogui
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 루트 디렉토리 경로 설정 (src 경로로 설정)
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(root_dir)

# 절대 경로를 사용하여 모듈을 불러옴
from common.logger_manager import LoggerManager
from common.response_manager import ResponseManager
from common.utils.helper import PyAutoGuiHelper


def execute_retry():
    logger = LoggerManager.get_logger(__name__)
    res = ResponseManager()
    
    try:
        logger.info("Starting 'reset_for_po_number_search'.")
        print(f"Starting 'reset_for_po_number_search'.")
        time.sleep(5)
        
        # 현재 창 닫기
        pyautogui.click((1563,95))
        logger.info(f"Clicking 'pos_window_focus' input at position [1563,95].")

        time.sleep(1)
        
        # 모든 창 닫기
        logger.debug(f"Pressing 'alt + x' to close all windows.")
        print(f"Pressing 'alt + x' to close all windows.")
        pyautogui.hotkey('alt', 'x')
        time.sleep(1)
        
        # 모든 창 닫기
        logger.debug(f"Pressing 'alt + x' to close all windows.")
        print(f"Pressing 'alt + x' to close all windows.")
        pyautogui.hotkey('alt', 'x')
        time.sleep(1)
        
        # 모든 창 닫기
        logger.debug(f"Pressing 'alt + x' to close all windows.")
        print(f"Pressing 'alt + x' to close all windows.")
        pyautogui.hotkey('alt', 'x')
        time.sleep(1)
        
        # 상위 메뉴 탭 모두 닫기
        PyAutoGuiHelper.perform_click((214,95))
        logger.info(f"Moving to '상위 모든 메뉴 탭 닫기' menu at [214,95].")
        print(f" Moving to '상위 모든 메뉴 탭 닫기' menu at [214,95].")
        time.sleep(1)
        

        logger.info(f"'reset_for_po_number_search' completed successfully.")
        print(f"'reset_for_po_number_search' completed successfully.")
        res.add_contexts(1, "reset_for_po_number_search", "success", "reset_for_po_number_search completed successfully.")
        return res.to_json()

    except Exception as e:
        error_message = f"reset_for_po_number_search failed: {str(e)}"
        logger.error(error_message)
        res.add_contexts(1, "reset_for_po_number_search", "failed", error_message)
        return res.to_json()

# if __name__ == "__main__":
#     result = execute_retry()
#     print("Result JSON:", result)