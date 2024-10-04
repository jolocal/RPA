import pyautogui


# def print_mouse_position():
#     """=====================================
#     import mss (left, top, width, height)
#     ====================================="""
#     print("마우스를 캡처 영역의 왼쪽 상단 모서리에 이동시키고, Enter 키를 누르세요.")
#     input()  # 사용자가 마우스를 이동시키고 Enter 키를 누르기를 기다림
#     left, top = pyautogui.position()  # 현재 마우스 위치를 얻음
#     print(f"캡처 영역의 왼쪽 상단 좌표: ({left}, {top})")  # 좌표 출력

#     print("마우스를 캡처 영역의 오른쪽 하단 모서리에 이동시키고, Enter 키를 누르세요.")
#     input()  # 사용자가 마우스를 이동시키고 Enter 키를 누르기를 기다림
#     right, bottom = pyautogui.position()  # 현재 마우스 위치를 얻음
#     print(f"캡처 영역의 오른쪽 하단 좌표: ({right}, {bottom})")  # 좌표 출력

#     # 좌표 유효성 검사
#     if right <= left or bottom <= top:
#         print("잘못된 좌표입니다. 'right'는 'left'보다 커야 하며, 'bottom'은 'top'보다 커야 합니다.")
#         return

#     # 캡처 영역의 폭과 높이를 계산
#     width = right - left
#     height = bottom - top

#     # 캡처 영역의 좌표와 크기를 출력
#     print(f"캡처 영역의 위치와 크기: (left: {left}, top: {top}, width: {width}, height: {height})")

# if __name__ == "__main__":
#     try:
#         print("Press Ctrl+C to stop tracking.")
#         print_mouse_position()
#     except KeyboardInterrupt:
#         print("\n프로그램이 중단되었습니다.")




# def print_x_y_position():
#     """=====================================
#     print x, y 
#     ====================================="""
#     print("마우스를 원하는 위치에 이동시키고, Enter 키를 누르세요.")
#     input()
#     x, y = pyautogui.position()
#     print(f"x, y 좌표: ({x}, {y})")  # 좌표 출력


# if __name__ == "__main__":
#     print("Press Ctrl+C to stop tracking.")
#     print_x_y_position()




if __name__ == "__main__":
    while True:
        print(pyautogui.position())


# def print_mouse_position():
    
    
#     """=====================================
#     +---------- 현재 사용중 +----------
#     import pyautogui (x, y, width, height)
#     ====================================="""
#     print("마우스를 팝업 창의 왼쪽 상단 모서리에 이동시키고, Enter 키를 누르세요.")
#     input()  # 사용자가 마우스를 이동시키고 Enter 키를 누르기를 기다림
#     left, top = pyautogui.position()  # 현재 마우스 위치를 얻음
#     print(f"팝업 창의 왼쪽 상단 좌표: ({left}, {top})")  # 좌표 출력

#     print("마우스를 팝업 창의 오른쪽 하단 모서리에 이동시키고, Enter 키를 누르세요.")
#     input()  # 사용자가 마우스를 이동시키고 Enter 키를 누르기를 기다림
#     right, bottom = pyautogui.position()  # 현재 마우스 위치를 얻음
#     print(f"팝업 창의 오른쪽 하단 좌표: ({right}, {bottom})")  # 좌표 출력


#     # 좌표 유효성 검사
#     if right <= left or bottom <= top:
#         print("잘못된 좌표입니다. 'right'는 'left'보다 커야 하며, 'bottom'은 'top'보다 커야 합니다.")
#         return
    



#     # 팝업 창의 폭과 높이를 계산
#     width = right - left
#     height = bottom - top

#     # 팝업 창의 좌표 (x, y, width, height)를 출력
#     print(f"팝업 창의 위치와 크기: (x: {left}, y: {top}, width: {width}, height: {height})")
    
# if __name__ == "__main__":
#     print("Press Ctrl+C to stop tracking.")
#     print_mouse_position()


# def print_mouse_position():

    """==================================================
    from PIL import ImageGrab (left, top, right, bottom)
    =================================================="""
#     print("마우스를 캡처 영역의 왼쪽 상단 모서리에 이동시키고, Enter 키를 누르세요.")
#     input()  # 사용자가 마우스를 이동시키고 Enter 키를 누르기를 기다림
#     left, top = pyautogui.position()  # 현재 마우스 위치를 얻음
#     print(f"캡처 영역의 왼쪽 상단 좌표: ({left}, {top})")  # 좌표 출력

#     print("마우스를 캡처 영역의 오른쪽 하단 모서리에 이동시키고, Enter 키를 누르세요.")
#     input()  # 사용자가 마우스를 이동시키고 Enter 키를 누르기를 기다림
#     right, bottom = pyautogui.position()  # 현재 마우스 위치를 얻음
#     print(f"캡처 영역의 오른쪽 하단 좌표: ({right}, {bottom})")  # 좌표 출력

#     # 좌표 유효성 검사
#     if right <= left or bottom <= top:
#         print("잘못된 좌표입니다. 'right'는 'left'보다 커야 하며, 'bottom'은 'top'보다 커야 합니다.")
#         return

#     # 캡처 영역의 좌표와 크기를 출력
#     print(f"캡처 영역의 위치와 크기: (left: {left}, top: {top}, right: {right}, bottom: {bottom})")

# if __name__ == "__main__":
#     try:
#         print("Press Ctrl+C to stop tracking.")
#         print_mouse_position()
#     except KeyboardInterrupt:
#         print("\n프로그램이 중단되었습니다.")

"""
라이브러리	호환성	성능	주요 기능	사용 목적
Pillow	윈도우, 맥	빠름	이미지 처리, 화면 캡처	이미지 처리와 캡처
pyautogui	윈도우, 맥, 리눅스	중간	자동화 작업, 화면 캡처	자동화 작업
mss	윈도우, 맥, 리눅스	매우 빠름	다중 모니터 지원, 화면 캡처	성능 중시 캡처 작업
"""
