import re
from src import metrics
from src import tokenization
import os

current_dir = os.path.dirname(os.path.realpath(__file__))


def normalize_both_sizes(text):
    regex = r"x\d+\s+"
    matches = re.finditer(regex, text, re.MULTILINE)
    flag = False
    for matchNum, match in enumerate(matches, start=1):
        a = match.start()
        b = match.end()
        sub_text = text[a:b]
        sub_text = re.sub(r'x', ' x ', sub_text)
        text = ' '.join([text[0:a], sub_text, text[b:]])
        flag = True
        break
    if flag:
        return normalize_both_sizes(text)
    return text


def normalize_unit(text):
    regex = r"\d+(mm|cm)"
    matches = re.finditer(regex, text, re.MULTILINE)
    flag = False
    for matchNum, match in enumerate(matches, start=1):
        a = match.start()
        b = match.end()
        sub_text = text[a:b]
        sub_text = re.sub(r'cm', ' cm ', sub_text)
        sub_text = re.sub(r'mm', ' mm ', sub_text)
        text = text[0:a] + sub_text + text[b:]
        flag = True
        break
    if flag:
        return normalize_unit(text)
    text = normalize_both_sizes(text)
    return text


def normalize_fraction(text):
    regex = r"\d+\/\d+"
    matches = re.finditer(regex, text, re.MULTILINE)
    flag = False
    for matchNum, match in enumerate(matches, start=1):
        a = match.start()
        b = match.end()
        sub_text = text[a:b]
        sub_text = re.sub(r'\/', ' phần ', sub_text)
        text = ' '.join([text[0:a], sub_text, text[b:]])
        flag = True
        break
    if flag:
        return normalize_fraction(text)
    return text


def normalize_en_hour(text):
    regex = r"\d+h"
    matches = re.finditer(regex, text, re.MULTILINE)
    flag = False
    for matchNum, match in enumerate(matches, start=1):
        a = match.start()
        b = match.end()
        sub_text = text[a:b]
        sub_text = re.sub(r'h', ' giờ ', sub_text)
        text = ' '.join([text[0:a], sub_text, text[b:]])
        flag = True
        break
    if flag:
        return normalize_en_hour(text)
    return text


def normalize_vi_hour(text):
    regex = r"(\d+g)|(\d+\sg)"
    matches = re.finditer(regex, text, re.MULTILINE)
    flag = False
    for matchNum, match in enumerate(matches, start=1):
        a = match.start()
        b = match.end()
        sub_text = text[a:b]
        sub_text = re.sub(r'g', ' giờ ', sub_text)
        text = ' '.join([text[0:a], sub_text, text[b:]])
        flag = True
        break
    if flag:
        return normalize_en_hour(text)
    return text


translation_table = {
    'm': 'mờ',
    'một': '1',
    'hai': '2',
    'ba': '3',
    'bốn': '4',
    'tư': '4',
    'năm': '5',
    'sáu': '6',
    'bảy': '7',
    'tám': '8',
    'chín': '9',
    'mười': '10',
    'mười_một': '11',
    'mười_hai': '12',
    'mười_ba': '13',
    'mười_bốn': '14',
    'mười_lăm': '15',
    'mười_sáu': '16',
    'mười_bảy': '17',
    'mười_tám': '18',
    'mười_chín': '19',
    'hai_mươi': '20',
    'mi_li_mét': 'mm',
    'cen_ti_mét': 'cm',
    'xi_ti': 'ct',
    'x_quang': 'x-quang',
    "tư_thế": 'tư thế'
}


def replace_gold_text(text):
    text = text.replace('sáo', 'sáu ')
    text = text.replace('xao', 'sau ')
    text = text.replace("tém", 'tám ')
    text = text.replace('xquang', 'x-quang ')
    text = text.replace('iii', '3 ')
    text = text.replace('ii', '2 ')
    return text


def replace_multiplication_text(text):
    text = text.replace('nhân', ' x ')
    return text


def normalize_date(text):
    regex = r"([0-2][0-9]|(3)[0-1])(\/)(((0)[0-9])|((1)[0-2]))(\/)\d{4}"
    matches = re.finditer(regex, text, re.MULTILINE)
    flag = False
    for matchNum, match in enumerate(matches, start=1):
        a = match.start()
        b = match.end()
        sub_text = text[a:b]
        details = sub_text.split('/')
        details = f"ngày {str(int(details[0]))} tháng {str(int(details[1]))} năm {str(int(details[2]))}"
        text = ' '.join([text[0:a], details, text[b:]])
        flag = True
        break
    if flag:
        return normalize_both_sizes(text)
    return text


def normalize_tokens(text):
    lm_tokenizer = tokenization.LongMatchingTokenizer(bi_grams_path=os.path.join(current_dir, 'bi_grams.txt'),
                                                      tri_grams_path=os.path.join(current_dir, 'tri_grams.txt'))
    tokens = lm_tokenizer.tokenize(text)
    tokens = [translation_table.get(i, i) for i in tokens]
    text = ' '.join(tokens)
    text = replace_multiplication_text(text)
    text = normalize_date(text)
    text = normalize_fraction(text)
    text = normalize_unit(text)
    text = normalize_en_hour(text)
    text = normalize_vi_hour(text)

    return text


def normalize_golden_text(text: str) -> str:
    text = text.lower()

    text = normalize_tokens(text)

    text = ' '.join([i for i in text.split() if i not in ("·", "₋")])
    text = text.replace('~', ' khoảng ')
    text = re.sub(r'^.\s+', '', text)
    text = re.sub(r'\s+0+(.+)', r' \1', text)
    text = re.sub(r'^\.+', '', text)
    text = replace_gold_text(text)
    text = metrics.normalize_text(text, lower_case=True,
                                  remove_punctuation=True)
    text = re.sub(' +', ' ', text)
    return text.strip()


def normalize_pred_text(text: str) -> str:
    text = text.lower()

    text = normalize_tokens(text)

    text = metrics.normalize_text(text, lower_case=True,
                                  remove_punctuation=True)
    text = re.sub(' +', ' ', text)
    return text.strip()


if __name__ == "__main__":
    # print(normalize_golden_text(
    #     "Vú trái: Hình vài nốt mờ nhỏ có bờ đều, giới hạn rõ ở vùng 1/4 "
    #     "trên ngoài mô truyến, nốt lớn kích thước ~ "
    #     "3x5mm bên vú trái, 4 x 15 cm bên phải, 1.1x2mm ở giữa",
    # ))
    # print(normalize_golden_text("sửa câu mười một thành một nốt vôi hóa dạng lành tính vị trí 12h trong xquang."))
    # print(normalize_golden_text("Mô vú có đậm độ cản quang ở mức trung bình ( Level III)"))
    # print(normalize_golden_text("Cơ hoành hai bên dâng cao do tư thế nằm."))
    # print(normalize_golden_text("₋Hình ảnh chấm vôi hóa 1/2 trên vú trái ₋Không thấy vôi hóa thành mạch trẻ trai 06 tuổi."))
    # print(normalize_golden_text("vú trái bất đối xứng ở vùng trong kích thước 4.3 cm cách núm vú 4.81 cm"))
    # print(normalize_golden_text("thêm hình nốt mờ nhỏ ngoại vi nửa dưới trường phổi phải ( không thay đổi so với phim chụp ngày 08/09/2017). vào xao câu bốn"))
    # print(normalize_golden_text(".............Mật độ mô vú: phân bố không đồng nhất có thể che lấp một số tổn thương nhỏ."))
    # print(normalize_golden_text(" Hình ảnh gãy 1/3 giữa xương đòn phải  đã được cố định bằng nẹp vít    Presence of 1/3 middle of right clavicle fractured, fixed by screw brace"))
    # print(normalize_golden_text("Đọc kết quả chụp X quang cổ chân hai bên:   Hình ảnh gai xương nhẹ đầu dưới xương chày và xương gót hai bên dạng thoái hóa."))
    print(normalize_golden_text("sửa câu số 1 thành hình ảnh gai xương nhỏ mặt trước thân các đốt sống l3 l4 l5 và s1"))
    # print('#' * 10)
    print(normalize_pred_text("Đề nghị kết hợp lâm sàng kết hợp chụp xi ti."))
    print(normalize_pred_text("thêm lớp m nhỏ vùng đáy phổi trái kích thước 15 nhân hai mươi mi li mét vào sau Câu 1"))
    print(normalize_pred_text("giới hạn rõ ở vùng một phần tư"))
    print(normalize_pred_text("nốt vi vôi hóa đơn độc gồm một phân tích ngoài"))
    print(normalize_pred_text("vị trí 11 g và 11h, 12g cách luồn vú"))
