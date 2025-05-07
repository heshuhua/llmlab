import re
import json

data_string = "{'input': '张三从银行取出50万', 'text': '根据你的需求，我可以帮助你分析这个业务，并输出所需的信息。\n\n**输入信息**\n\n* `username`: 张三 (因为你提到我会从输入信息中判断出是谁来做业务)\n* 交易类型：取款 (因为你提到我会判断客户到银行做的是什么交易)\n\n**识别出的参数**\n\n* `pcode`: 200101 (因为取款交易的 pcode 是固定的，即 200101)\n* `amount`: 5000000 (因为客户要取出 50 万，相当于人民币 5,000,000)\n* `agent`: false (因为没有明确指出这是代为他人办理的业务，所以默认是本人办理)\n\n**输出信息**\n\n```\nusername: 张三\npcode: 200101\namount: 5000000\nagent: false\n```'}"

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

extracted_info = extract_values(data_string)

# 获取 pcode 的值
pcode_value = extracted_info.get('pcode')

print(f"提取到的 pcode 值: {pcode_value}")

# 如果需要 JSON 格式的输出，可以这样做：
json_output = json.dumps({'pcode': pcode_value}, ensure_ascii=False, indent=4)
print(f"JSON 格式的 pcode 值:\n{json_output}")