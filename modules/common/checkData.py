import re
from rapidocr import RapidOCR


class OCRSingleton:
    """RapidOCR单例，确保OCR实例只创建一次"""
    _instance = None
    _ocr = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._ocr = RapidOCR()
        return cls._instance

    @property
    def ocr(self):
        return self._ocr


# 全局OCR实例
_ocr_instance = OCRSingleton()


#游戏内单位转换
def convert_units(data):
    # 单位映射
    multipliers = {
        'K': 1_000,
        'M': 1_000_000,
        'B': 1_000_000_000
    }

    # 如果最后一位是单位
    if data[-1] in multipliers:
        number = float(data[:-1])  # 去掉最后的单位
        return number * multipliers[data[-1]]

    # 无单位
    return float(data)

#图片识别金币后转换单位
def img_coin_ocr(imgPath):
    print("enter img ocr：", imgPath)
    data = _ocr_instance.ocr(imgPath)
    txts, scores = _parse_rapidocr_output(data)
    print("txts :", txts)

    if len(txts) == 1:
        check_coin = txts[0]
    else:
        check_coin = parse_number_unit(txts)

    print("check_coin :",check_coin)

    convert_data = convert_units(check_coin)

    return convert_data


def _parse_rapidocr_output(data):
    """解析RapidOCR输出"""
    if data is None:
        return [], []
    txts = data[1] if len(data) > 1 else []
    scores = data[2] if len(data) > 2 else []
    return txts, scores

#处理ocr识别金币成2个文本
def parse_number_unit(txts):
    # 提取第一段数字：允许整数、小数
    first_num = None
    for t in txts:
        m = re.match(r"^\d+(\.\d+)?$", t)
        if m:
            first_num = t
            break

    # 提取带单位的部分
    unit_num = None
    unit = ""
    for t in txts:
        m = re.match(r"(\d+(?:\.\d+)?)([KMG])$", t)
        if m:
            unit_num = m.group(1)
            unit = m.group(2)
            break

    # 情况 1：像 ('22.6', '6M') → 使用 first_num + unit
    if first_num and unit:
        return f"{first_num}{unit}"

    # 情况 2：普通 ('20', '0.9M') → 合并
    if first_num and unit_num and unit:
        return f"{first_num}.{unit_num}{unit}"

    # 单一带单位，例如 ('0.9M',)
    if unit_num and unit:
        return f"{unit_num}{unit}"

    # 只有一个数字
    if first_num:
        return first_num

    # 全都不匹配
    return " ".join(txts)