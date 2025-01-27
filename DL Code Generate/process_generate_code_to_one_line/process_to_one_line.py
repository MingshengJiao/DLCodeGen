import re
import black
from parser_code import transfer_to_one_line
import os

def remove_comments(line: str) -> str:
    """
    Removes comments from a single line of Python code.

    Args:
        line (str): The line of Python code to process.

    Returns:
        str: The line of code with comments removed. May be an empty string.
    """
    # Regular expression to match comments
    # Matches hash symbol and any text following it
    comment_pattern = r'#.*'

    # Remove comments using regex substitution
    cleaned_line = re.sub(comment_pattern, '', line)

    return cleaned_line


# 由于prompt中的template文件包含多行注释，导致生成结果中注释内容过多，影响实验结果
# 使用此函数将生成内容中的多行注释去掉
# 主要检测""" """包裹的内容，经过手工检查，gpt-35_origin中不包含用此形式定义的多行字符串
def remove_multi_line_comment(lines):
    tmp = []
    flag = True
    for line in lines:
        if line.strip().startswith('"""'):
            flag = not flag
            continue
        if flag:
            tmp.append(remove_comments(line))
    return tmp


def remove_triple_backticks(lines):
    # return lines
    tmp = []
    for line in lines:
        line = line.replace('```python', '')
        line = line.replace('```', '')
        tmp.append(line)
    return tmp


def count_line_characters(lines, d_num):
    max_c = d_num
    for line in lines:
        if len(line) > max_c:
            max_c = len(line)
    return max_c


# 该函数使用black8对代码进行规范化
def format_code_with_black(code: str) -> str:
    formatted_code = black.format_str(code, mode=black.FileMode(line_length=210, string_normalization=True))
    return formatted_code


def process_code(tmp, max_c, i):
    tmp = remove_multi_line_comment(tmp)
    max_c = count_line_characters(tmp, max_c)
    tmp = remove_triple_backticks(tmp)

    codes = '\n'.join(tmp)
    try:
        codes = format_code_with_black(codes)
    except Exception as e:
        # Handle the exception, print a message, but do not terminate the program
        print(f"A black parse error occurred for {i}: {e} ")

    codes = transfer_to_one_line(codes)
    return codes, max_c


def process_2_one_line(source_file, target_file):
    lines = []

    with open(source_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    tmp = []
    final_lines = []
    count = 0
    max_c = 0
    for line in lines:
        if '------------------------------------- ' in line:
            codes, max_c = process_code(tmp, max_c, count)
            print(f"{count} processed finish!\n")
            count += 1

            final_lines.append(" ".join(codes) + "\n")
            tmp = []
        else:
            tmp.append(line)

    # 对结尾额外处理
    # codes, max_c = process_code(tmp, max_c, count)
    # final_lines.append(" ".join(codes) + "\n")


    print(f"max c: {max_c}")
    print(len(final_lines))

    with open(target_file, 'w', encoding='utf-8') as f:
        f.writelines(final_lines)
    print(f"{source_file} --> {target_file} success!")

if __name__ == "__main__":
    source_path = ""
    target_path = ""

    source_files = []
    target_files  = []

    # 遍历 source_path 中的 .txt 文件
    for filename in os.listdir(source_path):
        if filename.endswith('.txt'):
            # 原始文件的完整路径
            source_file_path = os.path.join(source_path, filename)
            source_files.append(source_file_path)
            
            # 添加 _one_line 后缀并生成目标文件路径
            target_filename = os.path.splitext(filename)[0] + '_one_line.txt'
            target_file_path = os.path.join(target_path, target_filename)
            target_files.append(target_file_path)

    for source, target in zip(source_files, target_files):
        process_2_one_line(source, target)
