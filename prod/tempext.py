import re

def extract_last_pcode_adjacent_number(text):
    """
    提取字符串中最后一个 "pcode" 后面最近的一个数字字符串。

    Args:
        text: 输入字符串。

    Returns:
        如果找到，返回最近的数字字符串；否则返回 None。
    """
    if not isinstance(text, str):
        text = str(text)  # 尝试将输入转换为字符串

    matches = re.findall(r"pcode\s+([0-9]+)", text)
    if matches:
        return matches[-1]
    else:
        return None

# 示例用法
string1 = "一些文本 pcode 123 另一个 pcode  456 abc pcode   789 def"
result1 = extract_last_pcode_adjacent_number(string1)
print(f"字符串 '{string1}' 中提取到的数字字符串: {result1}")

string2 = "pcode  10 a pcode 20 b pcode  30"
result2 = extract_last_pcode_adjacent_number(string2)
print(f"字符串 '{string2}' 中提取到的数字字符串: {result2}")

string3 = "没有 pcode 的文本 999"
result3 = extract_last_pcode_adjacent_number(string3)
print(f"字符串 '{string3}' 中提取到的数字字符串: {result3}")

string4 = "pcode abc 123 pcode def"
result4 = extract_last_pcode_adjacent_number(string4)
print(f"字符串 '{string4}' 中提取到的数字字符串: {result4}")

string5 = "pcode  \n 567"
result5 = extract_last_pcode_adjacent_number(string5)
print(f"字符串 '{string5}' 中提取到的数字字符串: {result5}")

# 处理非字符串输入
integer_input = 12345
result_int = extract_last_pcode_adjacent_number(integer_input)
print(f"输入 '{integer_input}' 中提取到的数字字符串: {result_int}")