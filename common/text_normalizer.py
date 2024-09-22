import re

def normalize_for_pallet_creation(text):
    # Success
    text = re.sub(r'히터생성', 'Pallet생성', text)
    text = re.sub(r'a', '예', text)
    text = re.sub(r'마니모', '아니오', text)
    text = re.sub(r'9인','확인',text)
    
    # Failed    
    text = re.sub(r'대상미', '대상이', text)
    text = re.sub(r'미(가)', '이(가)', text)
    text = re.sub(r'존재하지 많습니다.','존재하지 않습니다.',text)
    
    # CG) 미미 『헤하 번호가 생성된 데미터 입니다,
    text = re.sub(r'미미.','이미',text)
    text = re.sub(r'데미터.','데이터',text)
    return text

def normalize_for_batch_input(text):
    text = re.sub(r'일팔입력', '일괄입력', text)
    text = re.sub(r'반영', '반영', text)
    text = re.sub(r'되었습니다.', '되었습니다.', text)
    return text

def normalize_for_generate_invoice(text):
    return text

def normalize_text(text, popup_type):
    """팝업 유형에 맞는 정규화 규칙 적용"""
    
    if popup_type == 'pallet_creation':
        text = normalize_for_pallet_creation(text)
    elif popup_type == 'batch_input':
        text = normalize_for_batch_input(text)
    elif popup_type == 'generate_invoice':
        text = normalize_for_generate_invoice(text)
    return text