from rapidocr import RapidOCR

def parse_rapidocr_output(result):
    """
    兼容所有 RapidOCR 输出格式:
    - list of [box, text, score]
    - list of dicts
    - RapidOCROutput(boxes, txts, scores)
    - (result, image)
    """
    if result is None:
        return (), ()

    # -------------------------------
    # 1. 新版本：RapidOCROutput 对象
    # -------------------------------
    # 例如：
    #   result.boxes
    #   result.txts
    #   result.scores
    try:
        if hasattr(result, "txts") and hasattr(result, "scores"):
            return tuple(result.txts), tuple(result.scores)
    except:
        pass

    # -------------------------------
    # 2. 老版本：返回 (result, image)
    # -------------------------------
    if isinstance(result, tuple) and len(result) == 2:
        result = result[0]

    if not result:
        return (), ()

    # -------------------------------
    # 3. 普通列表格式
    # -------------------------------
    txts = []
    scores = []

    for item in result:
        # 格式 A：[box, text, score]
        if isinstance(item, list) and len(item) == 3:
            txts.append(item[1])
            scores.append(float(item[2]))

        # 格式 B：{"box": ..., "text": ..., "score": ...}
        elif isinstance(item, dict):
            txts.append(item.get("text", ""))
            scores.append(float(item.get("score", 0.0)))

    return tuple(txts), tuple(scores)

