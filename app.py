import streamlit as st
import pandas as pd
import os
import sys
import io
import contextlib
import traceback
import time
from aider.coders import Coder
from aider.models import Model
from aider.io import InputOutput
from dotenv import load_dotenv
from datetime import datetime

# 加载环境变量
load_dotenv(".env")

# 确保目录存在
os.makedirs("images", exist_ok=True)
os.makedirs("data", exist_ok=True)

# 初始化session_state变量
if "task_completed" not in st.session_state:
    st.session_state.task_completed = False
if "uploaded_file_path" not in st.session_state:
    st.session_state.uploaded_file_path = None
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "openrouter/google/gemini-2.0-flash-001"
# 添加聊天消息历史
if "messages" not in st.session_state:
    st.session_state.messages = []
# 添加聊天状态
if "chat_ready" not in st.session_state:
    st.session_state.chat_ready = False
if "coder" not in st.session_state:
    st.session_state.coder = None
if "df" not in st.session_state:
    st.session_state.df = None
# 当模型选择改变时更新session_state
# 设置页面
st.set_page_config(
    page_title="数据分析助手",
    layout="wide",
    page_icon="🔬",
    initial_sidebar_state="expanded"
)

# 主标题
st.title("🔬 数据分析助手 | AI-Powered")
st.caption("使用先进AI技术进行数据分析和可视化")
st.markdown("<div style='text-align: right; font-size: 0.8em; color: rgba(100,100,100,0.5);'>Created by Dr.Shi</div>", unsafe_allow_html=True)

# 侧边栏 - 模型选择和文件上传
with st.sidebar:
    st.markdown("### 🤖 选择AI模型")
    model_options = {
        "deepseek": "DeepSeek V3 0324",
        "openrouter/anthropic/claude-3.7-sonnet": "claude-3.7-sonnet",
        "openrouter/qwen/qwen-2.5-coder-32b-instruct": "Qwen 32B Coder",
        "openrouter/google/gemini-2.0-flash-001": "gemini-2.0-flash"
    }
    selected_model = st.selectbox(
        "选择模型",
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x],
        index=list(model_options.keys()).index(st.session_state.selected_model),
        key="model_selector"
    )
    
    # 添加API密钥输入
    st.markdown("### 🔑 API密钥设置")
    with st.expander("设置API密钥", expanded=False):
        # 根据选择的模型显示相应的API密钥输入框
        if selected_model.startswith("openrouter"):
            openrouter_key = st.text_input(
                "OpenRouter API密钥", 
                value=os.environ.get("OPENROUTER_API_KEY", ""),
                type="password",
                key="openrouter_key"
            )
            if openrouter_key:
                os.environ["OPENROUTER_API_KEY"] = openrouter_key
        elif selected_model == "deepseek":
            deepseek_key = st.text_input(
                "DeepSeek API密钥", 
                value=os.environ.get("DEEPSEEK_API_KEY", ""),
                type="password",
                key="deepseek_key"
            )
            if deepseek_key:
                os.environ["DEEPSEEK_API_KEY"] = deepseek_key
        
        st.caption("API密钥将临时保存在会话中，不会永久存储")
    
    if selected_model != st.session_state.selected_model or st.session_state.coder is None:
        st.session_state.selected_model = selected_model
        try:
            st.write(f"正在初始化模型: {st.session_state.selected_model}")
            model = Model(st.session_state.selected_model)
            io = InputOutput(yes=True)
            st.session_state.coder = Coder.create(
                main_model=model,
                io=io,
                fnames=["usercode.py"],
                read_only_fnames=["data/table_description.txt", "CONVENTIONS.md"],
                use_git=False,
                auto_test=True,
                test_cmd="python usercode.py"
            )
            # 如果已经上传了文件，恢复聊天就绪状态
            if st.session_state.df is not None:
                st.session_state.chat_ready = True
        except Exception as e:
            st.error(f"初始化模型时出错: {e}")    
    st.markdown("### 📤 上传数据文件")
    uploaded_file = st.file_uploader(
        "拖放或点击上传CSV/Excel文件", 
        type=["csv", "xlsx", "xls"],
        label_visibility="collapsed"
    )
    
    # 添加使用说明
    with st.expander("使用说明", expanded=False):
        st.markdown("""
        1. 上传CSV或Excel文件进行数据分析
        2. 在聊天框中输入你的数据分析问题
        3. AI会生成相应的分析代码并执行
        4. 分析结果会直接显示在聊天界面中
        5. 你可以继续提问，进行多轮对话
        """)

# 处理文件上传
if uploaded_file is not None and (st.session_state.uploaded_file_path is None or 
                                 os.path.basename(st.session_state.uploaded_file_path) != uploaded_file.name):
    # 清空usercode.py和images文件夹
    with open("usercode.py", "w") as f:
        f.write("")
    with open("result.md", "w") as f:
        f.write("")
    for file in os.listdir("images"):
        if file.endswith((".png", ".html")):
            os.remove(os.path.join("images", file))
    
    # 清空聊天历史
    st.session_state.messages = []
    
    # 读取上传的文件
    try:
        # 保存上传的文件到data文件夹
        file_path = os.path.join("data", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # 记录文件路径到会话状态
        st.session_state.uploaded_file_path = file_path
        
        # 读取文件
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # 保存到会话状态
        st.session_state.df = df
        
        # 获取数据信息
        buffer = io.StringIO()
        df.info(buf=buffer)
        info_str = buffer.getvalue()
        
        # 保存数据描述到文件
        os.makedirs("data", exist_ok=True)
        with open("data/table_description.txt", "w") as f:
            f.write("temp.csv表格结构:\n")
            f.write("数据预览：\n")
            f.write(df.head(10).to_string())
            f.write("\n\n数据信息：\n")
            f.write(info_str)
        
        # 保存数据到CSV (如果原始文件不是CSV)
        if not uploaded_file.name.endswith('.csv'):
            df.to_csv("data/temp.csv", index=False)
        else:
            # 如果是CSV，复制一份到temp.csv
            df.to_csv("data/temp.csv", index=False)
        # 设置聊天准备就绪状态
        st.session_state.chat_ready = True
        
        # 添加系统消息到聊天历史
        st.session_state.messages.append({"role": "assistant", "content": f"数据已成功上传！我已准备好帮你分析 {uploaded_file.name} 文件。请告诉我你想了解什么？"})
        
    except Exception as e:
        st.error(f"处理文件时出错: {e}")
        st.code(traceback.format_exc())

# 主界面 - 数据预览和聊天界面
if st.session_state.df is not None:
    # 显示数据预览
    with st.expander("数据预览", expanded=True):
        st.dataframe(st.session_state.df.head(10))
    
    # 显示聊天历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # 如果是助手回复且包含图表，显示图表
            if message["role"] == "assistant" and "task_id" in message:
                task_id = message["task_id"]
                html_files = [f for f in os.listdir("images") if f.startswith(f"chart_{task_id}_") and f.endswith(".html")]
                
                if html_files:
                    for i, html_file in enumerate(html_files):
                        html_path = os.path.join("images", html_file)
                        with open(html_path, "r", encoding="utf-8") as f:
                            html_content = f.read()
                        st.components.v1.html(html_content, height=500, scrolling=True)
    
    # 聊天输入框
    if st.session_state.chat_ready:
        user_query = st.chat_input("输入你的数据分析问题...")
        
        if user_query:
            # 添加用户消息到历史
            st.session_state.messages.append({"role": "user", "content": user_query})
            
            # 显示用户消息
            with st.chat_message("user"):
                st.markdown(user_query)
            
            # 显示助手正在思考
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("思考中...")
                
                # 清空images文件夹中的特定文件
                for file in os.listdir("images"):
                    if file.endswith(".html"):
                        os.remove(os.path.join("images", file))
                #清空result.md文件
                with open("result.md", "w") as f:
                    f.write("")
                #清空usercode.py文件
                with open("usercode.py", "w") as f:
                    f.write("")
                # 生成唯一的任务ID
                task_id = int(time.time())
                
                try:
                    # 使用已创建的coder对象
                    coder = st.session_state.coder
                    
                    # 运行aider并传入用户问题
                    coder.run(user_query)
                    # 读取result.md文件
                    if os.path.exists("result.md"):
                        with open("usercode.py", "r") as f:
                            code_content = f.read()
                        with open("result.md", "r") as f:
                            result_content = f.read()
                        
                        # 过滤主标题
                        filtered_content = []
                        for line in result_content.split('\n'):
                            if not line.startswith("# "):
                                filtered_content.append(line)
                        
                        # result_text = code_content + "\n" +'\n'.join(filtered_content)
                        result_text = '\n'.join(filtered_content)                        
                    else:
                        result_text = "分析已完成，但没有生成文本结果。"
                    
                    # 更新助手消息
                    message_placeholder.markdown(f"### 生成的代码:\n```python\n{code_content}\n```\n### 分析结果:\n{result_text}")
                    # 重命名生成的HTML文件，添加任务ID前缀
                    html_files = [f for f in os.listdir("images") if f.endswith(".html")]
                    for i, html_file in enumerate(html_files):
                        old_path = os.path.join("images", html_file)
                        new_name = f"chart_{task_id}_{i+1}.html"
                        new_path = os.path.join("images", new_name)
                        os.rename(old_path, new_path)
                    
                    # 显示当前消息的图表
                    renamed_html_files = [f for f in os.listdir("images") if f.startswith(f"chart_{task_id}_") and f.endswith(".html")]
                    if renamed_html_files:
                        for html_file in renamed_html_files:
                            html_path = os.path.join("images", html_file)
                            with open(html_path, "r", encoding="utf-8") as f:
                                html_content = f.read()
                            st.components.v1.html(html_content, height=500, scrolling=True)
                    
                    # 保存助手消息到历史
                    assistant_message = {"role": "assistant", "content": result_text, "task_id": task_id}
                    st.session_state.messages.append(assistant_message)
                    
                except Exception as e:
                    error_message = f"生成分析时出错: {str(e)}"
                    message_placeholder.markdown(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})
else:
    # 如果没有上传文件，显示欢迎信息
    st.markdown("### 👋 欢迎使用数据分析助手")
    st.markdown("请先在左侧上传数据文件，然后我们就可以开始聊天分析数据了！")
    st.image("https://img.freepik.com/free-vector/data-inform-illustration-concept_114360-864.jpg", width=400)
