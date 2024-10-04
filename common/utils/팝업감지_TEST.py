import cv2
import numpy as np
import pyautogui
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 스크린샷을 찍고 이미지로 변환
def take_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return screenshot

# 특정 영역에서 팝업창을 감지하는 함수
def detect_popup(image):
    # 팝업창이 자주 나타나는 영역A00
    # region_x_start = 800
    # region_y_start = 450
    # region_x_end = 1350
    # region_y_end = 650
    
    # script_4:거래명세서발행
    region_x_start = 724
    region_y_start = 474
    region_x_end = region_x_start + 698
    region_y_end = region_y_start + 166
    
    # 해당 영역을 추출
    region_of_interest = image[region_y_start:region_y_end, region_x_start:region_x_end]
    
    # 그레이스케일로 변환
    gray = cv2.cvtColor(region_of_interest, cv2.COLOR_BGR2GRAY)
    
    # 가우시안 블러 적용 (노이즈 감소)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 경계선 검출
    edged = cv2.Canny(blurred, 50, 150)
    
    # 외곽선(컨투어) 찾기
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # 가장 큰 외곽선을 팝업창으로 가정
        popup_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(popup_contour)
        
        # 팝업창의 위치를 원래 이미지 좌표로 변환
        x += region_x_start
        y += region_y_start
        
        # 팝업창 영역에 사각형 그리기 (디버깅용)
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # 팝업 영역만 잘라서 반환
        popup_region = image[y:y+h, x:x+w]
        
        return image, popup_region
    else:
        print("팝업창을 찾을 수 없습니다.")
        return image, None

# OCR을 통해 텍스트를 추출하는 함수
def extract_text_from_popup(popup_region):
    # 이미지 전처리: 그레이스케일, 이진화, 대비 조정
    gray = cv2.cvtColor(popup_region, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # 이미지 확대 (텍스트가 작을 경우)
    scale_factor = 2
    enlarged_image = cv2.resize(binary_image, (0, 0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)
    
    # Tesseract 설정
    custom_config = r'--oem 3 --psm 6'
    
    # OCR을 통해 텍스트 추출
    text = pytesseract.image_to_string(enlarged_image, lang='kor+eng', config=custom_config)
    return text

# 추출된 텍스트를 분석하여 성공/실패 여부 판단 및 버튼 클릭
def analyze_and_click(text):
    # "Pallet생성 하시겠습니까?" 부분을 유연하게 인식
    if "Pallet" in text and "하시겠습니까" in text:
        print("성공: 'Pallet생성 하시겠습니까?' 버튼을 클릭합니다.")
        # '예' 버튼 클릭 (예상 위치에 따라 조정 필요)
        pyautogui.click(x=950, y=620)  # 예시 좌표
    elif "실패" in text or "오류" in text:
        print("실패: '아니오' 버튼을 클릭합니다.")
        # '아니오' 버튼 클릭 (예상 위치에 따라 조정 필요)
        pyautogui.click(x=1050, y=620)  # 예시 좌표
    else:
        print("결과를 알 수 없습니다.")

# 메인 실행 함수
def main():
    screenshot = take_screenshot()
    image_with_popup, popup_region = detect_popup(screenshot)
    
    if popup_region is not None:
        # 팝업창이 감지된 전체 화면을 표시
        cv2.imshow("Detected Popup", image_with_popup)
        
        # 'q' 키를 누르면 창이 닫힙니다.
        while True:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()
        
        # 팝업창 영역에서 텍스트 추출
        text = extract_text_from_popup(popup_region)
        print("추출된 텍스트:", text)
        
        # 텍스트 분석 및 버튼 클릭
        analyze_and_click(text)
    else:
        print("팝업창이 감지되지 않았습니다.")

if __name__ == "__main__":
    main()
