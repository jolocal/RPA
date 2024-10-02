import pyautogui
import pyperclip
import time
from datetime import datetime
from typing import List, Tuple
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class PyAutoGuiHelper:
    @staticmethod
    def perform_click(position: Tuple[int, int]):
        pyautogui.moveTo(*position)
        time.sleep(0.5)
        pyautogui.click()
        time.sleep(0.5)

    @staticmethod
    def perform_click_sequence(positions: List[Tuple[int, int]]):
        for pos in positions:
            time.sleep(0.1)
            PyAutoGuiHelper.perform_click(pos)

    @staticmethod
    def perform_double_click(position: Tuple[int, int]):
        pyautogui.moveTo(*position)
        time.sleep(0.5)
        pyautogui.doubleClick()
        time.sleep(0.5)

    @staticmethod
    def generate_filename(prefix: str, extension: str) -> str:
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{current_time}.{extension}"

    @staticmethod
    def save_file_with_name(filepath: str):
        pyperclip.copy(filepath)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(0.5)

    @staticmethod
    def move_to_index(current_index: int, target_index: int):
        # 이동할 칸 수 계산 (현재 인덱스에서 목표 인덱스까지)
        move_steps = target_index - current_index
        direction = 'down' if move_steps > 0 else 'up'
        time.sleep(0.5)
        
        # abs() 함수는 숫자의 절댓값을 반환
        for _ in range(abs(move_steps)):
            pyautogui.press(direction)
            time.sleep(0.5)