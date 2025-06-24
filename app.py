import streamlit as st
import pandas as pd
import os

# 设置页面配置 - 必须是第一个st命令
st.set_page_config(
    page_title="涂料行业化学物质绿色分级查询系统",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 创建数据目录（如果不存在）
def ensure_data_dir():
    data_dir = os.path.join("app", "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

# 确保数据目录存在
ensure_data_dir()

# 导入自定义模块
from app.auth.authentication import setup_authenticator
from app.pages.search_page import render_search_page
from app.pages.admin_page import render_admin_page

# 自定义CSS
def load_css():
    st.markdown("""
    <style>
        .main .block-container {
            padding-top: 2rem;
        }
        
        h1, h2, h3 {
            color: #1E88E5;
        }
        
        .stApp {
            background-color: #F5F7F9;
        }
        
        .css-18e3th9 {
            padding-top: 1rem;
        }
        
        .css-1d391kg {
            padding-top: 1rem;
        }
        
        .stButton>button {
            background-color: #1E88E5;
            color: white;
            border-radius: 5px;
            border: none;
            padding: 0.5rem 1rem;
        }
        
        .stButton>button:hover {
            background-color: #1565C0;
        }
        
        .toxicity-level-1 {
            color: #FF0000;
            font-weight: bold;
        }
        
        .toxicity-level-2 {
            color: #FFA500;
            font-weight: bold;
        }
        
        .toxicity-level-3 {
            color: #FFFF00;
            font-weight: bold;
        }
        
        .toxicity-level-4 {
            color: #00FF00;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

# 初始化会话状态
def init_session_state():
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = None
    if "username" not in st.session_state:
        st.session_state["username"] = None
    if "name" not in st.session_state:
        st.session_state["name"] = None

# 主应用
def main():
    # 加载CSS
    load_css()
    
    # 初始化会话状态
    init_session_state()
    
    # 设置认证器
    authenticator = setup_authenticator()
    
    # 侧边栏
    with st.sidebar:
        # 华南所logo
        st.image("华南所logo-011.jpg")

        
        st.title("涂料行业化学物质绿色分级查询系统")
        st.markdown("---")
        
        # 认证表单 - 只在未登录时显示
        if st.session_state["authentication_status"] is not True:
            login_tab, register_tab = st.tabs(["登录", "注册说明"])
            
            with login_tab:
                # 使用0.2.3版本兼容的参数格式
                name, authentication_status, username = authenticator.login('Login', 'sidebar')
                
                # 只在有认证结果时更新session state
                if authentication_status is not None:
                    st.session_state["authentication_status"] = authentication_status
                    st.session_state["username"] = username
                    st.session_state["name"] = name
                
                if st.session_state["authentication_status"] is False:
                    st.error("用户名或密码错误")
                elif st.session_state["authentication_status"] is None:
                    st.warning("请输入用户名和密码")
            
            with register_tab:
                st.info("请联系管理员创建新账户")
        
        # 显示登录信息和退出按钮
        if st.session_state["authentication_status"] is True:
            st.success(f"已登录为: {st.session_state['name']}")
            
            # 导航菜单
            st.subheader("导航")
            options = ["化学物质查询"]
            if st.session_state["username"] == "admin":
                options.append("管理面板")
            page = st.radio("选择页面", options)
            st.session_state["page"] = page
            
            # 退出按钮
            authenticator.logout('退出登录', 'sidebar')
            
            # 显示版本信息
            st.markdown("---")
            st.caption("版本 1.0.0")
    
    # 主内容区域
    if st.session_state["authentication_status"] is True:
        if page == "化学物质查询":
            render_search_page(st.session_state["username"])
        elif page == "管理面板" and st.session_state["username"] == "admin":
            render_admin_page()
    else:
        # 未登录显示
        st.title("欢迎使用涂料行业化学物质绿色分级查询系统")
        st.markdown("""
        ### 系统功能
        本系统提供涂料行业化学物质绿色分级查询服务，支持以下功能：
        
        - 通过CAS号查询化学物质绿色分级
        - 显示化学物质详细信息，包括名称、绿色分级、功能用途等
        - 可视化展示绿色分级结果
        - 查询历史记录（管理员）
        
        ### 使用方法
        请在左侧边栏登录系统后使用。如果没有账号，请联系管理员。
        """)
        
        st.info("请登录后使用系统功能")

if __name__ == "__main__":
    main() 