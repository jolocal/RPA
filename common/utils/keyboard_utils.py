import pyautogui
import ctypes
import logging
import time
import win32gui
import win32process
import win32api
import win32con

from common.logger_manager import LoggerManager

# 로거 설정
logger = LoggerManager.get_logger(__name__)

class CapslockHelper:
    @staticmethod
    def is_capslock_on():
        """+=========================
        CapsLock 상태를 확인하는 함수
        return : 1 (on) / 0 (off)
        +========================="""    
        hllDll = ctypes.WinDLL("User32.dll")
        VK_CAPITAL = 0x14
        state =  hllDll.GetKeyState(VK_CAPITAL) & 0x0001
        logging.info(f"CapsLock is {'on' if state else 'off'}")
        return state
    
    @staticmethod
    def turn_off_capslock():
        """+=================
        CpaLock을 끄는 함수
        +================="""    
        if CapslockHelper.is_capslock_on():
            pyautogui.press('capslock')
            logging.info("CapsLock turned off")
            
    @staticmethod        
    def turn_on_capslock():
        """+=================
        CpaLock을 켜는 함수
        +================="""    
        if not CapslockHelper.is_capslock_on():
            pyautogui.press('capslock')
            logging.info("CapsLock turned on")

    @staticmethod
    def switch_to_english():
        """
        입력 언어를 영어로 변경하여 영어 키보드 레이아웃을 활성화
        """
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        hwnd = user32.GetForegroundWindow()
        hkl = user32.LoadKeyboardLayoutW("00000409", 1)  # English (United States) Keyboard Layout
        user32.ActivateKeyboardLayout(hkl, 0)
        logging.info("Switched to English input")

    @staticmethod
    def type_with_shift(value):
        """
        주어진 문자열을 입력할 때 대문자는 Shift 키를 사용하여 입력하고, 소문자는 Shift 없이 입력합니다.
        **** pyautogui.press(char) 함수는 char에 해당하는 키를 입력
        """
        result = ""
        for char in value:
            if not char.isupper(): # 소문자인경우
                pyautogui.press(char)
                result += char
            else: # 대문자인경우
                pyautogui.keyDown('shift')
                pyautogui.press(char) 
                pyautogui.keyUp('shift')
                result += char.lower() 
            time.sleep(0.1)  # 각 키 입력 후 약간의 지연 시간을 추가
    
    @staticmethod
    # 현재 키보드 레이아웃 확인
    def get_keyboard_layout():
        hwnd = win32gui.GetForegroundWindow()
        thread_id = win32api.GetWindowThreadProcessId(hwnd)[0]
        layout_id = win32api.GetKeyboardLayout(thread_id)
        return layout_id
    
    @staticmethod
    # 키보드 레이아웃 설정(예: 영어 - 미국)
    def set_keyboard_layout(lang_code='00000409'):
        hwnd = win32gui.GetForegroundWindow()
        thread_id, _ = win32process.GetWindowThreadProcessId(hwnd)
        win32api.PostThreadMessage(thread_id, win32con.WM_INPUTLANGCHANGEREQUEST, 0, int(lang_code, 16))