import re

# 延迟导入：避免在模块加载时就要求 OCR 依赖齐全
try:
    from rapidocr import RapidOCR
    _RAPIDOCR_AVAILABLE = True
except ImportError:
    _RAPIDOCR_AVAILABLE = False


class OCRSingleton:
    """RapidOCR单例，懒加载：只在首次访问 ocr 属性时才初始化"""
    _instance = None
    _ocr = None
    _init_failed = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def ocr(self):
        """懒加载 OCR 实例，首次访问时才创建，失败时给出明确提示"""
        if self._ocr is None and not self._init_failed:
            if not _RAPIDOCR_AVAILABLE:
                raise ImportError(
                    "RapidOCR 未安装。请运行：pip install rapidocr-onnxruntime"
                )
            try:
                self._ocr = RapidOCR()
            except ImportError as e:
                self._init_failed = True
                raise ImportError(
                    f"RapidOCR 初始化失败，请安装 onnxruntime：pip install onnxruntime\n"
                    f"原始错误: {e}"
                ) from e
        return self._ocr


# 全局OCR实例（不立即初始化，仅在调用 .ocr 时才创建）
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