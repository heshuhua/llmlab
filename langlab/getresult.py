import re
import json

text = "根据客户业务描述，我可以推断出以下信息：\n\n* pcode = 200101（取款交易）\n* amount = 2600（客户要取出的金额）\n* agent = true（因为王五是代替爱人办理业务）\n\n因此，输出结果为：\n```\npcode: 200101\namount: 2600\nagent: true\n```"

def getResult(text):
    pcode_match = re.search(r"pcode\s*=\s*(\w+)", text)
    amount_match = re.search(r"amount\s*=\s*(\d+)", text)
    agent_match = re.search(r"agent\s*=\s*(true|false)", text)

    result = {}

    if pcode_match:
        result['pcode'] = pcode_match.group(1)
    if amount_match:
        result['amount'] = int(amount_match.group(1))
    if agent_match:
        result['agent'] = agent_match.group(1) == 'true'

    json_output = json.dumps(result, ensure_ascii=False, indent=4)
    print(json_output)

getResult(text)