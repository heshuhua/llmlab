from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain.chains.router import MultiPromptChain
from langchain_ollama import OllamaLLM
from langchain.chains import ConversationChain
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains.router.llm_router import LLMRouterChain,RouterOutputParser
from langchain.chains.router.multi_prompt_prompt import MULTI_PROMPT_ROUTER_TEMPLATE

withdraw_template = """你是银行资深柜员，非常善于处理客户取款问题。
你会从输入信息中判断出是谁来做业务，给出客户姓名 username=客户姓名
你会判断客户到银行做的是什么交易，识别出取款交易给设置当前的 pcode=200101。
你会从问题中识别出客户要取多少钱，比如取3000， 那amount=3000。
你会从客户是否是代为他人办理，如果是代办，需要设置agent=true，如果是本人办理或没有识别出来，则设置agent=false

这是一个客户业务：
{input}

请只输出 username,pcode，amount，agent的信息
"""


despoit_template =  """你是银行资深柜员，非常善于处理客户存款问题。
你会从输入信息中判断出是谁来做业务，给出客户姓名 username=李四
你会判断客户到银行做的是什么交易，识别出存款交易给设置当前的 pcode=200102。
你会从问题中识别出客户要存多少钱，比如存3000， 那amount=3000。

这是一个客户业务：
{input}

请只输出 username,pcode和amount的信息
"""

prompt_infos = [
    {
        "name": "存款",
        "description": "适用于回答存款问题",
        "prompt_template": despoit_template,
    },
    {
        "name": "取款",
        "description": "适用于回答取款问题",
        "prompt_template": withdraw_template,
    },
]

llm = OllamaLLM(model="llama3.1:latest",temperature=0.9)
#llm = OllamaLLM(model="deepseek-r1:32b",temperature=0.9)


destination_chains = {}
# 遍历prompt_infos列表，为每个信息创建一个LLMChain。
for p_info in prompt_infos:
    name = p_info["name"]  # 提取名称
    prompt_template = p_info["prompt_template"]  # 提取模板
    # 创建PromptTemplate对象
    prompt = PromptTemplate(template=prompt_template, input_variables=["input"])
    # 使用上述模板和llm对象创建LLMChain对象
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # 将新创建的chain对象添加到destination_chains字典中
    destination_chains[name] = chain

# 创建一个默认的ConversationChain
default_chain = ConversationChain(llm=llm, output_key="text")

# 从prompt_infos中提取目标信息并将其转化为字符串列表
destinations = [f"{p['name']}: {p['description']}" for p in prompt_infos]
# 使用join方法将列表转化为字符串，每个元素之间用换行符分隔
destinations_str = "\n".join(destinations)
# 根据MULTI_PROMPT_ROUTER_TEMPLATE格式化字符串和destinations_str创建路由模板
router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(destinations=destinations_str)
# 创建路由的PromptTemplate
router_prompt = PromptTemplate(
    template=router_template,
    input_variables=["input"],
    output_parser=RouterOutputParser(),
)
# 使用上述路由模板和llm对象创建LLMRouterChain对象
router_chain = LLMRouterChain.from_llm(llm, router_prompt)
# 创建MultiPromptChain对象，其中包含了路由链，目标链和默认链。
chain = MultiPromptChain(
    router_chain=router_chain,
    destination_chains=destination_chains,
    default_chain=default_chain,
    verbose=True,
)