import re
import metrics
import tokenization


def normalize_sizes(text):
    regex = r"\d+x\d+"
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
        return normalize_sizes(text)
    return text


def normalize_fraction(text):
    regex = r"\d \/ \d"
    matches = re.finditer(regex, text, re.MULTILINE)
    flag = False
    for matchNum, match in enumerate(matches, start=1):
        a = match.start()
        b = match.end()
        sub_text = text[a:b]
        sub_text = re.sub(r' \/ ', '/', sub_text)
        text = ' '.join([text[0:a], sub_text, text[b:]])
        flag = True
        break
    if flag:
        return normalize_sizes(text)
    return text


def normalize_date(text):
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
        return normalize_date(text)
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
    'phần': '/'
}


def replace_gold_text(text):
    text = text.replace('sáo', 'sáu ')
    text = text.replace('xao', 'sau ')
    text = text.replace('xquang', 'x-quang ')
    text = text.replace('iii', 'ba ')

    return text


def replace_pred_text(text):
    text = text.replace('nhân', ' x ')
    return text


def normalize_tokens(text):
    lm_tokenizer = tokenization.LongMatchingTokenizer(bi_grams_path='./bi_grams.txt',
                                                      tri_grams_path='./tri_grams.txt')
    tokens = lm_tokenizer.tokenize(text)
    tokens = [translation_table.get(i, i) for i in tokens]
    text = ' '.join(tokens)
    text = replace_pred_text(text)

    text = normalize_fraction(text)

    return text


def normalize_golden_text(text: str) -> str:
    text = text.replace('~', ' khoảng ')

    text = metrics.normalize_text(text, lower_case=True,
                                  remove_punctuation=True)
    text = normalize_tokens(text)
    text = normalize_sizes(text)
    text = normalize_date(text)
    text = replace_gold_text(text)

    return re.sub(' +', ' ', text)


def normalize_pred_text(text: str) -> str:
    text = metrics.normalize_text(text, lower_case=True,
                                  remove_punctuation=True)
    text = normalize_tokens(text)
    text = metrics.normalize_text(text, lower_case=False,
                                  remove_punctuation=True)
    return re.sub(' +', ' ', text)


if __name__ == "__main__":
    print(normalize_golden_text(
        "Vú trái: Hình vài nốt mờ nhỏ có bờ đều, giới hạn rõ ở vùng 1/4 "
        "trên ngoài mô truyến, nốt lớn kích thước ~ "
        "3x5mm bên vú trái, 4 x 15 mm bên phải, 1.1x2mm ở giữa",
    ))
    print(normalize_golden_text("Vú trái: Hình vài nốt mờ nhỏ có bờ đều, giới hạn rõ ở vùng 1/4 "))
    print(normalize_golden_text("sửa câu mười một thành một nốt vôi hóa dạng lành tính vị trí 12h trong xquang."))
    print('#' * 10)
    print(normalize_pred_text("Đề nghị kết hợp lâm sàng kết hợp chụp xi ti."))
    print(normalize_pred_text("thêm lớp m nhỏ vùng đáy phổi trái kích thước 15 nhân hai mươi mi li mét vào sau Câu 1"))
    print(normalize_pred_text("giới hạn rõ ở vùng một phần tư"))
