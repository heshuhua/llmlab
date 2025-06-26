import json
import random

# 定义中文茶的类型和对应的描述关键词
tea_data_zh = {
    "绿茶": [
        "这款茶带有清新、海苔的香气，口感清爽回甘，茶汤呈清澈的黄绿色。",
        "未经发酵的茶叶，经过杀青工艺，保留了天然的绿色和豆香，滋味鲜爽。",
        "以其翠绿的叶片和提神醒脑的功效而闻名，常带有清新的植物气息。",
        "冲泡后汤色清澈，叶底嫩绿，口感鲜醇，带有淡淡的板栗香或海苔味。",
        "这款茶口感清雅，带有春天的气息和独特的鲜爽感，适合日常饮用。",
        "富含茶多酚和维生素C，冲泡后叶片舒展，散发出清幽的兰花香。",
        "它的特点是清汤绿叶，滋味甘醇，带有天然的清香和一丝丝的甜味。",
        "采用蒸青或炒青工艺制成，茶汤清澈，口感醇厚回甘，香气持久。",
        "早春采摘的嫩芽制成，茶毫显露，汤色鹅黄明亮，滋味鲜爽甘甜。",
        "具有清热解毒、消食去腻的功效，常被形容为带有雨后青草的芬芳。"
    ],
    "红茶": [
        "经过完全发酵的茶叶，带有浓郁的麦芽香和花果香，茶汤呈红色明亮。",
        "口感醇厚饱满，滋味浓强鲜爽，适合与牛奶、糖搭配冲泡，作为早餐茶。",
        "这款茶汤色红艳，香气高扬，带有焦糖或蜜糖的甜香，回味悠长。",
        "其独特的发酵工艺赋予了它温润的口感和深沉的香气，适合在冬天饮用。",
        "条索紧结，色泽乌润，冲泡后茶汤橙红明亮，滋味甘醇，带有淡淡的玫瑰香。",
        "具有暖胃、提神的功效，香气浓郁持久，是世界上产量最大的茶类之一。",
        "这款茶冲泡后茶汤金圈显露，滋味浓郁而柔和，带有独特的发酵香。",
        "口感顺滑，带有天然的甜味和花香，是下午茶的理想选择。",
        "通常采用萎凋、揉捻、发酵、干燥等工艺制成，具有独特的醇厚感。",
        "这款茶具有提神醒脑、消除疲劳的功效，适合在工作或学习时饮用。"
    ],
    "乌龙茶": [
        "半发酵茶，介于绿茶和红茶之间，既有绿茶的清新，又有红茶的醇厚。",
        "香气馥郁，滋味醇厚回甘，常带有花香、果香或烘焙香，茶汤橙黄。",
        "以其独特的制作工艺而闻名，茶叶经过摇青、晾青等多道工序，形成独特的风味。",
        "这款茶泡饮时香气扑鼻，滋味浓郁甘润，回甘持久，被誉为“茶中珍品”。",
        "具有花香、果香或蜜香等多种香型，口感醇厚，回味无穷。",
        "茶汤呈琥珀色或金黄色，滋味醇厚，带有独特的火功香或焙火香。",
        "其独特的“绿叶镶红边”特征，使其既有绿茶的清香，又有红茶的醇厚。",
        "这款茶多次冲泡后依然香气四溢，滋味不减，是品鉴价值很高的茶类。",
        "其发酵程度介于10%到70%之间，赋予了其丰富多变的香气和口感。",
        "具有消食解腻、降脂减肥的功效，常被视为健康饮品。"
    ],
    "花草茶": [
        "不含咖啡因，这款茶以菊花和枸杞为主要成分，具有清热明目的功效。",
        "以薰衣草和洋甘菊制成，具有镇静安神的作用，适合睡前饮用。",
        "这款茶以玫瑰花和洛神花为主，口感酸甜，带有浓郁的花果香。",
        "由薄荷叶和柠檬草混合而成，具有清新提神、帮助消化的作用。",
        "混合了多种干果和花瓣，口感丰富，带有天然的甜味和果香。",
        "以生姜和红枣为主，具有暖身驱寒、补气养血的功效。",
        "这款茶由金银花和胖大海制成，具有清热润肺、利咽开音的作用。",
        "以胎菊和茉莉花为主，具有清香淡雅、疏肝解郁的功效。",
        "由柠檬片和罗汉果混合而成，口感酸甜，具有清热润肺的作用。",
        "这款茶以蒲公英和牛蒡根制成，具有清热解毒、利尿消肿的功效。"
    ],
    "拼配茶": [
        "这款茶是红茶与佛手柑油的混合，带有独特的柑橘香气和醇厚口感。",
        "绿茶与烘焙过的糙米混合，带来独特的坚果香和清新的茶味。",
        "混合了红茶、肉桂、丁香和豆蔻，是制作印度奶茶的理想选择。",
        "以绿茶为基底，加入茉莉花，散发出浓郁的茉莉花香和清新的茶味。",
        "这款茶将多种水果干与红茶混合，口感酸甜，茶香浓郁。",
        "白茶与蜜桃和生姜的混合，带来清新果香和微辣的口感。",
        "将乌龙茶与烘焙的坚果和香草混合，口感丰富，带有独特的坚果香。",
        "这款茶是薄荷叶与绿茶的混合，具有提神醒脑和清新口腔的作用。",
        "红茶与干浆果和奶油香料的混合，口感甜美，带有浓郁的果酱风味。",
        "混合了多种花瓣和绿茶，带来馥郁的花香和清新的茶味。"
    ]
}

# 生成数据集
train_data_raw = []
test_data_raw = []

for tea_type, descriptions in tea_data_zh.items():
    random.shuffle(descriptions) # 打乱描述
    # 80% 用于训练，20% 用于测试
    num_train = int(len(descriptions) * 0.8)
    train_descriptions = descriptions[:num_train]
    test_descriptions = descriptions[num_train:]

    for desc in train_descriptions:
        train_data_raw.append({"text": desc, "label": tea_type})
    for desc in test_descriptions:
        test_data_raw.append({"text": desc, "label": tea_type})

random.shuffle(train_data_raw)
random.shuffle(test_data_raw)

# 将原始数据转换为 Instruction Tuning 格式
# 格式：{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
formatted_train_data = []
for item in train_data_raw:
    formatted_train_data.append({
        "messages": [
            {"role": "system", "content": "你是一位专业的茶饮分类助手。请根据描述准确分类茶饮类型。你的回答只包含茶饮类型，不包含其他内容。"},
            {"role": "user", "content": f"请分类以下茶饮描述：{item['text']}"},
            {"role": "assistant", "content": item['label']}
        ]
    })

# 测试数据也需要保存，以便后续评估
# 测试数据依然使用 'instruction' 和 'output'，方便直接使用
formatted_test_data = []
for item in test_data_raw:
    formatted_test_data.append({
        "instruction": f"请分类以下茶饮描述：{item['text']}",
        "output": item['label']
    })

# 保存为 JSON Lines 文件
with open("tea_classification_train_zh.jsonl", "w", encoding="utf-8") as f:
    for entry in formatted_train_data:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

with open("tea_classification_test_zh.jsonl", "w", encoding="utf-8") as f:
    for entry in formatted_test_data:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print(f"生成了 {len(formatted_train_data)} 条中文训练数据到 tea_classification_train_zh.jsonl")
print(f"生成了 {len(formatted_test_data)} 条中文测试数据到 tea_classification_test_zh.jsonl")