import cv2
import numpy as np
import pyautogui

def capture_screenshot():
    # 전체 화면 스크린샷 캡처
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return screenshot

def detect_x_button_color(image, lower_hsv, upper_hsv):
    # 이미지를 HSV로 변환
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # HSV 범위에 맞는 부분을 마스크로 처리
    mask = cv2.inRange(hsv_image, lower_hsv, upper_hsv)

    # 마스크된 영역에서 컨투어(윤곽선) 검출
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 가장 큰 컨투어 선택
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        return (x, y, w, h), largest_contour
    else:
        return None, None

def main():
    # 테스트를 위해 스크린샷을 캡처
    screenshot = capture_screenshot()

    # HSV 색상 범위 설정 (여기에 실제 X 버튼의 색상 값을 넣어야 합니다)
    lower_hsv = np.array([0, 0, 200])   # 예시 값: 밝은 회색
    upper_hsv = np.array([180, 50, 255]) # 예시 값: 밝은 회색

    # 팝업창의 X 버튼을 감지
    popup_rect, contour = detect_x_button_color(screenshot, lower_hsv, upper_hsv)

    if popup_rect:
        x, y, w, h = popup_rect
        # 팝업창 영역 추출 및 표시
        popup_region = screenshot[y:y+h+50, x-50:x+w+50]  # 팝업의 영역을 확대하여 추출

        cv2.imshow('Detected Popup', popup_region)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("팝업창을 찾을 수 없습니다.")

if __name__ == "__main__":
    main()
