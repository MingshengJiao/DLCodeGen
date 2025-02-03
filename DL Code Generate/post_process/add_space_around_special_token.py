# 该脚本输入为一个文本文件，每一行代表一个代码片段
# 该程序的处理为，在特殊符号前后增加空格，从而将不同的单元分隔开，便于更加精准的CodeBLEU分数计算
# 对于使用
import re
import os

# 用于替换字符串和浮点数为占位符
def replace_strings_and_floats(code: str):
    string_pattern = r"('''.*?'''|\"\"\".*?\"\"\"|'.*?'|\".*?\")"   # 匹配单行和多行字符串的正则模式
    float_pattern = r"\b\d+\.\d+\b"   # 匹配浮点数内容
    paired_operators_pattern = r"(//|\*\*|==|!=|<=|>=)"  # 成对运算符

    # 匹配所有的字符串和浮点数
    strings = re.findall(string_pattern, code)
    floats = re.findall(float_pattern, code)
    paired_operators = re.findall(paired_operators_pattern, code)
    
    # 替换字符串和浮点数为占位符
    code = re.sub(string_pattern, "__STRING__", code)
    code = re.sub(float_pattern, "__FLOAT__", code)
    code = re.sub(paired_operators_pattern, "__PAIRED_OPERATOR__", code)

    return code, strings, floats, paired_operators


# 用于恢复字符串和浮点数的原始内容
def restore_strings_and_floats(code: str, strings: list, floats: list, paired_operators: list):
    # 恢复浮点数
    for float_num in floats:
        code = code.replace("__FLOAT__", float_num, 1)
    
    # 恢复字符串
    for string in strings:
        code = code.replace("__STRING__", '_'.join(string.split(' ')), 1)

    # 恢复浮点数
    for paired_operator in paired_operators:
        code = code.replace("__PAIRED_OPERATOR__", paired_operator, 1)
    
    return code


def add_spaces_around_special_chars(code: str) -> str:
    # 替换字符串和浮点数
    code_with_placeholders, strings, floats, paired_operators = replace_strings_and_floats(code)

    # 定义需要添加空格的特殊字符，不包含减号
    special_chars = r"([.,()\[\]{}:;=+\*/%!<>&|^~\'\"])"
    spaced_code = re.sub(special_chars, r" \1 ", code_with_placeholders)
    spaced_code = re.sub(r"(?<!\d)\-(?!\d)", " - ", spaced_code)    # 处理独立的减号，将负号与运算符区分开
    spaced_code = re.sub(r"[ ]{2,}", " ", spaced_code)      # 去除多余的空格

    # 恢复字符串和浮点数
    final_code = restore_strings_and_floats(spaced_code, strings, floats, paired_operators)

    return final_code


# 定义主函数，遍历 a 文件夹中的 txt 文件，处理并保存到 b 文件夹
def process_txt_files(input_folder: str, output_folder: str):
    # 检查 b 文件夹是否存在，如果不存在则创建
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 遍历 a 文件夹中的文件
    for filename in os.listdir(input_folder):
        # 只处理 .txt 文件
        if filename.endswith('.txt'):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            # 读取文件内容
            with open(input_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # 对内容进行特殊符号分隔处理
            processed_content = add_spaces_around_special_chars(content)

            # 将处理后的内容写入 b 文件夹下的文件
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(processed_content)

            print(f"Processed and saved: {output_path}")

# 指定文件夹路径
input_folder = '/'  # 输入文件夹路径
output_folder = ''  # 输出文件夹路径

# 执行文件处理
process_txt_files(input_folder, output_folder)
