from flask import Flask,request,jsonify
import json
from langchain_ollama import OllamaLLM
from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain import PromptTemplate


app= Flask(__name__)

@app.route("/")
def home():
    return "hello"

@app.route("/predict",methods=['POST'])
def predict():
    if request.method=='POST':
       data = request.get_data()
       data = json.loads(data)
       message = data['message']
       print(message)
       llm = OllamaLLM(
           model="llama3.1:latest",
           )
       prompt_template2 = PromptTemplate.from_template(
           "你是一个资深的银行柜员，请按照以下步骤提取描述信息：" \
            "先识别客户要做什么交易，比如取款的交易码 那 pode=200101；" \
            "再识别客户的交易金额，比如取2000元，那amount=2000，" \
            "最后返回结果，pcode=200101,amount=2000, 客户输入如下{content}" \
            "返回的输出格式为包含一下内容的json字符串，如果没有找到的类型，保持为空" \
            "\n pcode=200101，amount=2000元"
            )
       inputContent=message
       prompt2= prompt_template2.format(content=inputContent)
       print(prompt2)
       return(llm(prompt2))

        #  两种返回方式都可以
        # return {'response': f'Received message: {message}'}
       return jsonify({'response': 'Message received:'+message})

app.run()