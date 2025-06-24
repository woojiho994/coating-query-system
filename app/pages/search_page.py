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
    
    # 载入数据
    df = load_chemicals_data()
    
    if df is None:
        st.error("无法加载数据，请联系管理员。")
        return
    
    # 定义列名映射（根据实际Excel文件调整）
    cas_col = 'CAS号'          
    name_col = '中文名称'       
    toxicity_col = '绿色分级'   
    limit_col = '涂料现行标准限量要求'    
    control_col = '我国新污染物相关管理要求' 
    
    # 初始化session state
    if 'show_result' not in st.session_state:
        st.session_state.show_result = False
    if 'current_result' not in st.session_state:
        st.session_state.current_result = None
    if 'current_cas' not in st.session_state:
        st.session_state.current_cas = ""
    if 'current_usage' not in st.session_state:
        st.session_state.current_usage = ""
    
    # 搜索框
    st.subheader("请输入查询信息")
    cas_number = st.text_input("CAS号", key="cas_search", placeholder="请输入化学物质的CAS号")
    usage_purpose = st.text_input("使用用途", key="usage_search", placeholder="请输入该化学物质的使用用途")
    
    # 创建两列用于按钮
    col1, col2 = st.columns([1, 1])
    
    with col1:
        search_clicked = st.button("查询", key="search_button", type="primary")
    
    with col2:
        if st.session_state.show_result:
            clear_clicked = st.button("清除结果", key="clear_button")
            if clear_clicked:
                st.session_state.show_result = False
                st.session_state.current_result = None
                st.session_state.current_cas = ""
                st.session_state.current_usage = ""
                st.rerun()
    
    # 处理查询
    if search_clicked:
        if cas_number and usage_purpose:
            # 清除之前的结果
            st.session_state.show_result = False
            st.session_state.current_result = None
            
            with st.spinner("正在查询..."):
                try:
                    # 查询化学物质
                    result = search_chemical_by_cas(cas_number, df)
                    
                    # 保存到session state
                    st.session_state.current_result = result
                    st.session_state.current_cas = cas_number
                    st.session_state.current_usage = usage_purpose
                    st.session_state.show_result = True
                    
                    # 保存查询记录
                    if result:
                        chemical_name = result.get(name_col, "未知")
                        toxicity_level = result.get(toxicity_col, "未知")
                        result_text = f"{chemical_name} - 毒性分级: {toxicity_level}"
                        save_query_record(username, cas_number, result_text, usage_purpose)
                    else:
                        save_query_record(username, cas_number, "未找到结果", usage_purpose)
                    
                    # 强制重新运行以显示结果
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"查询时发生错误: {str(e)}")
                    st.session_state.show_result = False
        else:
            if not cas_number and not usage_purpose:
                st.warning("请输入CAS号和使用用途进行查询。")
            elif not cas_number:
                st.warning("请输入CAS号。")
            elif not usage_purpose:
                st.warning("请输入使用用途。")
    
    # 显示查询结果
    if st.session_state.show_result and st.session_state.current_result is not None:
        result = st.session_state.current_result
        cas_number = st.session_state.current_cas
        usage_purpose = st.session_state.current_usage
        
        st.markdown("---")  # 分隔线
        
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
            st.success("查询成功！")
            
            # 创建两列布局
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # 基本信息卡片
                st.subheader("基本信息")
                st.markdown(f"**CAS号**: {cas_number}")
                st.markdown(f"**化学物质名称**: {chemical_name}")                
                st.markdown(f"**涂料现行标准限量要求**: {limit_req}")
                st.markdown(f"**我国新污染物相关管理要求**: {control_req}")
            
            with col2:
                # 毒性分级可视化
                st.subheader("毒性分级")
                
                # 创建仪表盘
                if toxicity_level and toxicity_level != "未知":
                    try:
                        # 将中文数字转为数值
                        level_map = {"1级": 1, "2级": 2, "3级": 3, "4级": 4}
                        level_value = level_map.get(toxicity_level, 0)
                        
                        if level_value > 0:
                            gauge_value = level_value
                            
                            fig = go.Figure(go.Indicator(
                                mode = "gauge+number",
                                value = gauge_value,
                                domain = {'x': [0, 1], 'y': [0, 1]},
                                title = {'text': f"毒性级别: {toxicity_level}", 'font': {'size': 20}},
                                gauge = {
                                    'axis': {'range': [0, 4], 'tickvals': [0, 1, 2, 3, 4], 
                                            'ticktext': ['', '1级', '2级', '3级', '4级']},
                                    'bar': {'color': level_color},
                                    'steps': [
                                        {'range': [0, 1], 'color': '#E8F5E8'},
                                        {'range': [1, 2], 'color': '#FFF8DC'},  
                                        {'range': [2, 3], 'color': '#FFE4B5'},  
                                        {'range': [3, 4], 'color': '#FFE4E1'}   
                                    ],
                                    'threshold': {
                                        'line': {'color': "black", 'width': 3},
                                        'thickness': 0.75,
                                        'value': gauge_value
                                    }
                                }
                            ))
                            
                            fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning(f"毒性级别: {toxicity_level}")
                    except Exception as e:
                        st.warning(f"毒性级别: {toxicity_level}")
                else:
                    st.warning("未找到毒性级别信息")
                
                st.info(f"**说明**: {level_desc}")
        else:
            # 未找到结果
            st.warning(f"未找到CAS号为 {cas_number} 的化学物质。")
            
            # 显示联系信息的提示框
            st.info("""
            **数据库暂无该物质结果**
            
            如需获取该物质评估结果，请发送邮件至 **liwei@scies.org** 邮箱
            
            邮件中请注明：
            - 化学物质名称
            - CAS号
            - 用途
            - 企业名称
            """)
    
    # 显示使用说明
    with st.expander("使用帮助"):
        st.markdown("""
        ### 如何使用本系统
        1. 在搜索框中输入要查询的化学物质的CAS号
        2. 输入该化学物质的使用用途
        3. 确保两个字段都填写后，点击"查询"按钮
        4. 系统将显示该化学物质的详细信息，包括名称、毒性分级、功能用途等
        5. 点击"清除结果"可以清除当前查询结果
        
        ### 查询要求
        - **CAS号**: 必填，化学物质的唯一标识符
        - **使用用途**: 必填，请描述您计划使用该化学物质的具体用途
        
        ### 毒性分级说明
        - **1级**: 基本无危害物质，可安全使用
        - **2级**: 低度危害物质，可在特定条件下使用
        - **3级**: 中度危害物质，建议寻找替代方案
        - **4级**: 高度危害物质，应优先考虑替代
        """)

def render_search_page(username):
    search_page(username) 