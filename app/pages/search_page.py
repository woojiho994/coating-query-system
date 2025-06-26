import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from app.utils.data_utils import (
    load_chemicals_data, 
    search_chemical_by_cas, 
    get_toxicity_level_description,
    get_toxicity_level_color,
    process_structure_image
)
from app.auth.authentication import save_query_record

def search_page(username):
    st.title("涂料行业化学物质绿色分级查询系统")
    
    # 初始化session state
    if "search_result" not in st.session_state:
        st.session_state.search_result = None
    if "last_search_cas" not in st.session_state:
        st.session_state.last_search_cas = ""
    if "last_search_usage" not in st.session_state:
        st.session_state.last_search_usage = ""
    if "search_performed" not in st.session_state:
        st.session_state.search_performed = False
    
    # 载入数据
    df = load_chemicals_data()
    
    if df is None:
        st.error("无法加载数据，请联系管理员。")
        return
    
    # 显示列名以便后续处理
    column_names = df.columns.tolist()
    print(f"Excel文件的列名: {column_names}")
    
    # 定义列名映射（根据实际Excel文件调整）
    cas_col = 'CAS号'          # CAS号列
    name_col = '中文名称'       # 名称列
    toxicity_col = '绿色分级'   # 毒性分级列
    limit_col = '涂料现行标准限量要求'    # 功能用途列
    control_col = '我国新污染物相关管理要求' # 管控要求列
    
    print(f"使用的列名映射: CAS号:{cas_col}, 名称:{name_col}, 毒性:{toxicity_col},  限量:{limit_col}, 管控要求:{control_col}")
    
    # 搜索框
    st.subheader("请输入查询信息")
    cas_number = st.text_input("CAS号", key="cas_search", placeholder="请输入化学物质的CAS号")
    usage_purpose = st.text_input("使用用途", key="usage_search", placeholder="请输入该化学物质的使用用途")
    
    # 提交按钮
    if st.button("查询", key="search_button", type="primary"):
        if cas_number and usage_purpose:
            with st.spinner("正在查询..."):
                print(f"用户'{username}'正在查询CAS号: {cas_number}")
                # 查询化学物质
                result = search_chemical_by_cas(cas_number, df)
                
                # 保存查询结果到session state
                st.session_state.search_result = result
                st.session_state.last_search_cas = cas_number
                st.session_state.last_search_usage = usage_purpose
                st.session_state.search_performed = True
                
                if result:
                    print(f"查询结果: {result}")
                    # 获取数据
                    chemical_name = result.get(name_col, "未知")
                    toxicity_level = result.get(toxicity_col, "未知")
                    
                    # 构建结果字符串用于记录
                    result_text = f"{chemical_name} - 毒性分级: {toxicity_level}"
                    
                    # 保存查询记录
                    save_query_record(username, cas_number, result_text, usage_purpose)
                    
                else:
                    # 保存未找到的查询记录
                    save_query_record(username, cas_number, "未找到结果", usage_purpose)
                    
                # 强制重新运行以显示结果
                st.rerun()
        else:
            if not cas_number and not usage_purpose:
                st.warning("请输入CAS号和使用用途进行查询。")
            elif not cas_number:
                st.warning("请输入CAS号。")
            elif not usage_purpose:
                st.warning("请输入使用用途。")
    
    # 显示查询结果（从session state读取）
    if st.session_state.search_performed and st.session_state.search_result is not None:
        result = st.session_state.search_result
        cas_number = st.session_state.last_search_cas
        usage_purpose = st.session_state.last_search_usage
        
        # 添加分隔线
        st.markdown("---")
        
        if result:
            # 获取数据
            chemical_name = result.get(name_col, "未知")
            toxicity_level = result.get(toxicity_col, "未知")
            limit_req = result.get(limit_col, "暂无信息")
            control_req = result.get(control_col, "暂无信息")
            
            # 获取毒性级别描述和颜色
            level_desc = get_toxicity_level_description(toxicity_level)
            level_color = get_toxicity_level_color(toxicity_level)
            
            # 显示结果
            st.success("✅ 查询成功！")
            
            # 创建两列布局
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # 基本信息卡片
                st.subheader("📋 基本信息")
                st.markdown(f"**CAS号**: `{cas_number}`")
                st.markdown(f"**化学物质名称**: {chemical_name}")                
                st.markdown(f"**涂料现行标准限量要求**: {limit_req}")
                st.markdown(f"**我国新污染物相关管理要求**: {control_req}")
            
            with col2:
                # 毒性分级可视化
                st.subheader("⚠️ 毒性分级")
                
                # 创建仪表盘
                if toxicity_level and toxicity_level != "未知":
                    # 将中文数字转为数值
                    level_map = {"1级": 1, "2级": 2, "3级": 3, "4级": 4}
                    level_value = level_map.get(toxicity_level, 0)
                    
                    if level_value > 0:
                        gauge_value = level_value
                        
                        fig = go.Figure(go.Indicator(
                            mode = "gauge+number+delta",
                            value = gauge_value,
                            domain = {'x': [0, 1], 'y': [0, 1]},
                            title = {'text': f"毒性级别: {toxicity_level}", 'font': {'size': 24}},
                            gauge = {
                                'axis': {'range': [0, 4], 'tickvals': [0, 1, 2, 3, 4], 
                                        'ticktext': ['', '1级', '2级', '3级', '4级']},
                                'bar': {'color': level_color},
                                'steps': [
                                    {'range': [0, 1], 'color': '#00FF00'},  # 1级 - 绿色
                                    {'range': [1, 2], 'color': '#FFFF00'},  # 2级 - 黄色
                                    {'range': [2, 3], 'color': '#FFA500'},  # 3级 - 橙色
                                    {'range': [3, 4], 'color': '#FF0000'}   # 4级 - 红色
                                ],
                                'threshold': {
                                    'line': {'color': "black", 'width': 4},
                                    'thickness': 0.75,
                                    'value': gauge_value
                                }
                            }
                        ))
                        
                        fig.update_layout(height=250)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning(f"毒性级别: {toxicity_level}")
                else:
                    st.warning("未找到毒性级别信息")
                
                st.info(f"💡 **说明**: {level_desc}")
            
        else:
            # 显示未找到结果的信息
            st.warning(f"❌ 未找到CAS号为 `{cas_number}` 的化学物质。")
            
            # 显示联系信息的提示框
            st.info("""
            📧 **数据库暂无该物质结果**
            
            如需获取该物质评估结果，请发送邮件至 **liwei@scies.org** 邮箱
            
            邮件中请注明：
            - 化学物质名称
            - CAS号
            - 用途
            - 企业名称
            """)
    
    # 显示一些使用说明
    with st.expander("📖 使用帮助"):
        st.markdown("""
        ### 如何使用本系统
        1. 在搜索框中输入要查询的化学物质的CAS号
        2. 输入该化学物质的使用用途
        3. 确保两个字段都填写后，点击"查询"按钮
        4. 系统将显示该化学物质的详细信息，包括名称、毒性分级、功能用途等
        
        ### 查询要求
        - **CAS号**: 必填，化学物质的唯一标识符
        - **使用用途**: 必填，请描述您计划使用该化学物质的具体用途
        
        ### 毒性分级说明
        - **1级**: 基本无危害物质，可安全使用 🟢
        - **2级**: 低度危害物质，可在特定条件下使用 🟡
        - **3级**: 中度危害物质，建议寻找替代方案 🟠
        - **4级**: 高度危害物质，应优先考虑替代 🔴
        """)

def render_search_page(username):
    search_page(username) 