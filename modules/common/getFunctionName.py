import inspect
import os


def getName():
    # 获取调用者的栈帧（调用getName的函数）
    caller_frame = inspect.stack()[1]

    # 获取调用者的函数名
    caller_function_name = caller_frame.function

    # 获取调用者所在的文件名（去掉路径和扩展名）
    caller_file_path = caller_frame.filename
    file_name_only = os.path.splitext(os.path.basename(caller_file_path))[0]

    # 拼接最终结果
    function_name = f"{file_name_only}_{caller_function_name}"

    print(function_name)
    return function_name
