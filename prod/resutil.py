import re
import json

data_string = "{'input': '张三从银行取出50万', 'text': '根据你的需求，我可以帮助你分析这个业务，并输出所需的信息。\n\n**输入信息**\n\n* `username`: 张三 (因为你提到我会从输入信息中判断出是谁来做业务)\n* 交易类型：取款 (因为你提到我会判断客户到银行做的是什么交易)\n\n**识别出的参数**\n\n* `pcode`: 200101 (因为取款交易的 pcode 是固定的，即 200101)\n* `amount`: 5000000 (因为客户要取出 50 万，相当于人民币 5,000,000)\n* `agent`: false (因为没有明确指出这是代为他人办理的业务，所以默认是本人办理)\n\n**输出信息**\n\n```\nusername: 张三\npcode: 200101\namount: 5000000\nagent: false\n```'}"
#data_string2 = "{'input': '张三取出20,000元', 'text': '{"username": "张三", "pcode": "200101", "amount": 20000, "agent": false}'}"
#print(f"111111{type(data_string2)}")
#data_string2="''可以直接从客户说的话中获取信息：\n\n*   用户名：username = 张三\n*   交易类型：pcode = 200101（取款）\n*   取款金额：amount = 20000\n*   是否代为他人办理：agent = false （因为没有发现代办的迹象）\n\n因此，业务信息如下：\n\n```json\n{\n    "username": "张三",\n    "pcode": "200101",\n    "amount": 20000,\n    "agent": false\n}\n```\n\n客户想要取出 20,000元。'"


def extract_values(data):
    """
    从给定的字符串中提取 username, pcode, agent 的值。

    Args:
        data: 包含所需信息的字符串。

    Returns:
        一个包含 username, pcode, agent 值的字典。
    """
    results = {}

    # 使用正则表达式匹配 username
    username_match = re.search(r"`username`:\s*([^\s(]+)", data)
    if username_match:
        results['username'] = username_match.group(1)

    # 使用正则表达式匹配 pcode
    pcode_match = re.search(r"`pcode`:\s*([^\s(]+)", data)
    if pcode_match:
        results['pcode'] = pcode_match.group(1)

    # 使用正则表达式匹配 agent
    agent_match = re.search(r"`agent`:\s*([^\s(]+)", data)
    if agent_match:
        results['agent'] = agent_match.group(1)

    return results

def replace_special_symbols_with_space(text):
    """
    将字符串中的指定特殊符号（，。“”）转换为空格。

    Args:
        text: 输入字符串。

    Returns:
        转换后的字符串。
    """
    if not isinstance(text, str):
        text = str(text)  # 确保输入是字符串

    # 使用正则表达式替换指定的特殊符号
    pattern = r"{}[，。，\n“”]"
    replaced_text = re.sub(pattern, " ", text)
    return replaced_text

def extract_pcode(text):
    """
    提取字符串中最后一个 'pcode' 后面最近的一个数字字符串，
    'pcode' 后面不直接跟着 '=' 号。

    Args:
        text: 输入字符串。

    Returns:
        如果找到符合条件的数字字符串，则返回该字符串；否则返回 None。
    """
    print(f"In resutil----{text}")
    if not isinstance(text, str):
        text = str(text)  # 尝试将输入转换为字符串
    text = replace_special_symbols_with_space(text)
    print(f"in resutil erase special char-----{text}")
    text = text.replace('{',' ')
    text = text.replace('}',' ')
    text = text.replace('\'',' ')
    text = text.replace('\"',' ')
    print(f"in resutil space char-----{text}")
    matches = re.findall(r"pcode\s+([^\d=]*?)(\d+)", text, re.IGNORECASE)
    if matches:
        return matches[-1][1]
    else:
        return None

def extract_amount(amounttext):
    """
    提取字符串中最后一个 'amount' 后面最近的一个数字字符串，
    'pcode' 后面不直接跟着 '=' 号。

    Args:
        text: 输入字符串。

    Returns:
        如果找到符合条件的数字字符串，则返回该字符串；否则返回 None。
    """
    print(f"In resutil----{amounttext}")
    if not isinstance(amounttext, str):
        amounttext = str(amounttext)  # 尝试将输入转换为字符串
    amounttext = replace_special_symbols_with_space(amounttext)
    print(f"in resutil erase special char-----{amounttext}")
    amounttext = amounttext.replace('{',' ')
    amounttext = amounttext.replace('}',' ')
    amounttext = amounttext.replace('\'',' ')
    amounttext = amounttext.replace('\"',' ')
    print(f"in resutil space char-----{amounttext}")
    matches = re.findall(r"amount\s+([^\d=]*?)(\d+)", amounttext, re.IGNORECASE)
    if matches:
        return matches[-1][1]
    else:
        return None

def convert_string_to_integer(text):
    """
    将字符串转换为整数。

    Args:
        text: 包含整数的字符串。

    Returns:
        转换后的整数，如果转换失败则返回 None。
    """
    if not isinstance(text, str):
        return None  # 输入不是字符串

    try:
        integer_value = int(text)
        return integer_value
    except ValueError:
        print(f"错误：字符串 '{text}' 无法转换为整数。")
        return None


#extracted_info = extract_values(data_string)

#print(extract_pcode(data_string2))