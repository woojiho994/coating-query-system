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

# 导入自定义模块
from app.pages.search_page import render_search_page

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

# 创建数据目录（如果不存在）
def ensure_data_dir():
    data_dir = os.path.join("app", "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

# 主应用
def main():
    # 确保数据目录存在
    ensure_data_dir()
    
    # 加载CSS
    load_css()
    
    # 侧边栏
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/4306/4306652.png", width=100)
        st.title("")
        st.markdown("---")
        st.caption("版本 1.0.0")
    
    # 主内容
    st.title("化学物质毒性查询系统")
    st.markdown("""
    ### 系统功能
    本系统提供化学物质毒性分级查询服务，支持通过CAS号查询化学物质的毒性分级信息。
    """)
    
    # 直接显示查询页面，使用"guest"作为用户名
    render_search_page("guest")

if __name__ == "__main__":
    main() 