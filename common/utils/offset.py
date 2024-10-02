import pyautogui

def get_position(prompt):
    """
    현재 마우스 위치를 가져오는 함수. 사용자가 Enter를 누를 때까지 대기합니다.

    :param prompt: 위치를 지정하는 안내 메시지
    :return: 현재 마우스 위치 좌표 (x, y)
    """
    print(prompt)
    print("마우스를 위치시키고 Enter를 누르세요...")
    keyboard.wait('enter')  # Enter 키를 누를 때까지 대기
    position = pyautogui.position()  # 현재 마우스 위치 가져오기
    print(f"저장된 위치: {position}")
    return position

def calculate_offset(position1, position2):
    """
    두 위치 간의 x, y 오프셋을 계산하는 함수.

    :param position1: 첫 번째 위치의 좌표 (x1, y1)
    :param position2: 두 번째 위치의 좌표 (x2, y2)
    :return: x 오프셋, y 오프셋
    """
    x_offset = position2[0] - position1[0]
    y_offset = position2[1] - position1[1]
    print(f"x 오프셋: {x_offset}")
    print(f"y 오프셋: {y_offset}")
    return x_offset, y_offset

def main():
    # Pallet번호 위치 저장
    pallet_position = get_position("첫 번째 위치: Pallet번호의 위치를 선택하세요.")
    
    # 체크박스 위치 저장
    checkbox_position = get_position("두 번째 위치: 체크박스의 위치를 선택하세요.")
    
    # 오프셋 계산
    calculate_offset(pallet_position, checkbox_position)

# 실행 코드
if __name__ == "__main__":
    main()
