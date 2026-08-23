import streamlit as st
import os
from openai import OpenAI

# 设置页面配置，包括页面标题、图标、布局等
st.set_page_config(
    page_title="余哥出品",  # 设置页面标题
    page_icon="resources/my_emoji.png",  # 设置页面图标
    layout="wide",  # 设置页面布局为宽屏模式
    initial_sidebar_state="expanded",  # 设置侧边栏初始状态为展开
    menu_items={  # 设置页面底部菜单项
        'Get Help': 'https://www.extremelycoolapp.com/help',  # 帮助链接
        'Report a bug': "https://www.extremelycoolapp.com/bug",  # 报告bug链接
        'About': "# This is a header. This is an *extremely* cool app!"  # 关于信息
    }
)
# 设置页面标题为"Ai.智能伴侣"
st.title("Ai.智能伴侣")
# 设置页面logo，使用resources/my_emoji.png图片，并设置为大尺寸
st.logo("resources/my_emoji.png",size="large")
# 创建deepseek客户端
client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")

# 在侧边栏中创建一个区域
# with st.sidebar:
#     # 在侧边栏中显示图片，设置宽度为120像素
#     st.image("resources/my_emoji.png", width=120) # width设置像素宽度

# 输入框
# 系统提示词
system_prompt = """你就是迪迦奥特曼。
你是守护地球的巨人，相信人类的光。
说话简短热血，温柔又坚定。
安慰失落的人，告诉大家每个人都可以成为光。
不要提到人工智能，完全代入迪迦身份对话。"""
# 初始化消息
if 'messages' not in st.session_state:
   st.session_state.messages = []
for messages in st.session_state.messages:#{"role":"user", "content":"迪迦你好"}列表格式
    # 另一种写法
    # st.chat_message(messages["role"],).write(messages["content"])
# 根据消息的角色类型来显示不同的聊天消息
   if messages["role"] == "user":  # 如果消息的角色是"user"
    # 使用用户自定义的头像和样式显示用户消息
       st.chat_message("user",avatar = "resources/my_emoji.png").write(messages["content"])
   elif messages["role"] == "assistant":  # 如果消息的角色是"assistant"
    # 使用迪迦头像的样式显示助手消息
       st.chat_message("assistant",avatar = "resources/迪迦.png").write(messages["content"])



prompt = st.chat_input("你好，我是迪迦，有什么可以帮助你的吗？")
if prompt:
# 使用st.chat_message创建一个用户消息气泡
# 参数说明：
# - "user": 指定消息类型为用户消息
# - avatar: 设置用户消息的头像图片路径
#   - 这里使用了本地资源 "resources/my_emoji.png" 作为头像
   st.chat_message("user",avatar = "resources/my_emoji.png").write(prompt)
   #    存入提示词
   st.session_state.messages.append({"role": "user", "content": prompt})
   print(f"----------->调试专用,提示词: {prompt}")


   response = client.chat.completions.create(
       model="deepseek-v4-pro",
       # 调用deepseek-v4-pro模型
       messages=[
           {"role": "system", "content": system_prompt},
           *st.session_state.messages,#解包列表，将列表中的元素逐个传入
       ],
       stream=True,
       # reasoning_effort="high",
       # extra_body={"thinking": {"type": "enabled"}}
   )
   # 打印大模型返回的结果（非流式输出）

   # print("<------大模型返回的结果: ",response.choices[0].message.content)
   # st.chat_message("assistant",avatar = "resources/迪迦.png").write(response.choices[0].message.content)

   #打印大模型返回的结果（流式输出）
   response.messages = st.empty()
   full_respons = ""
   for chunk in response:
       if chunk.choices[0].delta.content is not None:
           content = chunk.choices[0].delta.content
           full_respons += content
           response.messages.chat_message("assistant",avatar = "resources/迪迦.png").write(full_respons)
   # 保存大模型返回的结果，方便后续查看

   st.session_state.messages.append({"role": "assistant", "content": full_respons})
