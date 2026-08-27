import streamlit as st
import os
from openai import OpenAI
from datetime import datetime
import json
import uuid

st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

# --------------------------关键改动：获取访问用户唯一ID--------------------------
def get_user_id():
    """每个浏览器访问者生成唯一ID，存到st.session_state，区分不同用户"""
    if "user_id" not in st.session_state:
        # uuid生成随机唯一标识，代表这个来访用户
        st.session_state.user_id = str(uuid.uuid4())
    return st.session_state.user_id

def get_user_session_dir():
    """每个用户独立文件夹 sessions/用户ID/"""
    user_id = get_user_id()
    user_dir = os.path.join("sessions", user_id)
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

# 生成会话标识函数
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# 保存会话信息函数【修改：存到当前用户自己的文件夹】
def save_session():
    if st.session_state.current_session:
        session_data = {
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages
        }
        user_dir = get_user_session_dir()
        file_path = os.path.join(user_dir, f"{st.session_state.current_session}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

# 加载当前用户所有会话列表
def load_sessions():
    session_list = []
    user_dir = get_user_session_dir()
    if os.path.exists(user_dir):
        file_list = os.listdir(user_dir)
        for filename in file_list:
            if filename.endswith(".json"):
                session_list.append(filename[:-5])
    session_list.sort(reverse=True)
    return session_list

# 加载指定会话（只读取当前用户目录）
def load_session(session_name):
    try:
        user_dir = get_user_session_dir()
        file_path = os.path.join(user_dir, f"{session_name}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.messages = session_data["messages"]
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.nature = session_data["nature"]
                st.session_state.current_session = session_name
    except Exception:
        st.error("加载会话失败!")

# 删除会话
def delete_session(session_name):
    try:
        user_dir = get_user_session_dir()
        file_path = os.path.join(user_dir, f"{session_name}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            if session_name == st.session_state.current_session:
                st.session_state.messages = []
                st.session_state.current_session = generate_session_name()
    except Exception:
        st.error("删除会话失败!")


st.title("AI智能伴侣")

# 注意：部署到streamlit cloud不要读取本地图片resources/logo.png！云端没有这个文件，注释或者替换成网络图片
# st.logo("resources/logo.png")

system_prompt = """
        你叫 %s，现在是用户的真实伴侣，请完全代入伴侣角色。
        规则：
            1. 每次只回1条消息
            2. 禁止任何场景或状态描述性文字
            3. 匹配用户的语言
            4. 回复简短，像微信聊天一样
            5. 有需要的话可以用❤️🌸等emoji表情
            6. 用符合伴侣性格的方式对话
            7. 回复的内容, 要充分体现伴侣的性格特征
        伴侣性格：
            - %s
        你必须严格遵守上述规则来回复用户。
    """

# 初始化
if "user_id" not in st.session_state:
    get_user_id()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "小甜甜"
if "nature" not in st.session_state:
    st.session_state.nature = "活泼开朗的东北姑娘"
if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()


st.text(f"会话名称: {st.session_state.current_session}")
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])


client = OpenAI(
    api_key=st.secrets["DEEPSEEK_API_KEY"],  # 重要！部署云端不能用环境变量os.environ，要用st.secrets保存密钥
    base_url="https://api.deepseek.com"
)


with st.sidebar:
    st.subheader("AI控制面板")

    if st.button("新建会话", width="stretch", icon="✏️"):
        save_session()
        if st.session_state.messages:
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()
            save_session()
            st.rerun()

    st.text("会话历史")
    session_list = load_sessions()
    for session in session_list:
        col1,col2 = st.columns([4,1])
        with col1:
            if st.button(session, width="stretch", icon="📄", key=f"load_{session}", type="primary" if session == st.session_state.current_session else "secondary"):
                load_session(session)
                st.rerun()
        with col2:
            if st.button("", width="stretch", icon="❌️", key=f"delete_{session}"):
                delete_session(session)
                st.rerun()

    st.divider()
    st.subheader("伴侣信息")
    nick_name = st.text_input("昵称", placeholder="请输入昵称", value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name

    nature = st.text_area("性格", placeholder="请输入性格", value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature


prompt = st.chat_input("请输入您要问的问题")
if prompt:
    st.chat_message("user").write(prompt)
    print("----------> 调用AI大模型, 提示词: ", prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt % (st.session_state.nick_name, st.session_state.nature)},
            *st.session_state.messages
        ],
        stream=True
    )

    response_message = st.empty()
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            response_message.chat_message("assistant").write(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    save_session()
