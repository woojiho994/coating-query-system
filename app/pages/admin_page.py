import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from app.auth.authentication import get_all_query_logs, create_user, get_all_users, delete_user

def admin_page():
    st.title("管理员面板")
    
    # 创建标签页
    tab1, tab2 = st.tabs(["查询记录", "用户管理"])
    
    with tab1:
        st.header("查询记录")
        
        # 获取所有查询记录
        logs_df = get_all_query_logs()
        
        if logs_df.empty:
            st.info("暂无查询记录")
        else:
            # 添加日期过滤器
            st.subheader("按日期筛选")
            
            # 转换日期列为datetime类型
            logs_df['查询时间'] = pd.to_datetime(logs_df['查询时间'])
            
            # 获取最早和最新日期
            min_date = logs_df['查询时间'].min().date()
            max_date = logs_df['查询时间'].max().date()
            
            # 创建日期选择器
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("开始日期", min_date)
            with col2:
                end_date = st.date_input("结束日期", max_date)
            
            # 筛选数据
            filtered_df = logs_df[
                (logs_df['查询时间'].dt.date >= start_date) & 
                (logs_df['查询时间'].dt.date <= end_date)
            ]
            
            # 显示筛选后的数据
            st.subheader("查询记录列表")
            st.dataframe(filtered_df, use_container_width=True)
            
            # 创建一些统计信息
            st.subheader("统计信息")
            
            # 按日期统计查询次数
            daily_counts = filtered_df.groupby(filtered_df['查询时间'].dt.date).size().reset_index(name='查询次数')
            daily_counts.columns = ['日期', '查询次数']
            
            fig1 = px.bar(daily_counts, x='日期', y='查询次数', title='每日查询次数')
            st.plotly_chart(fig1, use_container_width=True)
            
            # 按用户统计查询次数
            user_counts = filtered_df.groupby('用户名').size().reset_index(name='查询次数')
            user_counts.columns = ['用户', '查询次数']
            
            fig2 = px.pie(user_counts, values='查询次数', names='用户', title='用户查询分布')
            st.plotly_chart(fig2, use_container_width=True)
            
            # 导出功能
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="导出为CSV",
                data=csv,
                file_name=f'查询记录_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
            )
    
    with tab2:
        st.header("用户管理")
        
        # 创建子标签页
        subtab1, subtab2, subtab3 = st.tabs(["查看用户", "创建新用户", "重置密码"])
        
        with subtab1:
            st.subheader("现有用户列表")
            
            # 获取所有用户
            users_df = get_all_users()
            
            if users_df.empty:
                st.info("暂无用户数据")
            else:
                # 添加显示密码的选项
                show_passwords = st.checkbox("显示密码", value=False, help="勾选以显示用户密码（仅管理员可见）")
                
                # 根据选项决定是否显示密码列
                if show_passwords:
                    display_df = users_df.copy()
                else:
                    display_df = users_df.drop('密码', axis=1)
                
                # 显示用户列表
                st.dataframe(display_df, use_container_width=True)
                
                # 如果显示密码，添加安全提示
                if show_passwords:
                    st.warning("⚠️ 密码信息已显示，请注意保护用户隐私")
                
                # 用户删除功能
                st.subheader("删除用户")
                
                # 获取除管理员外的用户列表
                non_admin_users = users_df[users_df['用户名'] != 'admin']['用户名'].tolist()
                
                if non_admin_users:
                    # 创建删除用户的表单
                    with st.form("delete_user_form"):
                        selected_user = st.selectbox("选择要删除的用户", non_admin_users)
                        st.warning("⚠️ 删除用户将永久移除该用户账户，此操作不可恢复！")
                        
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            delete_button = st.form_submit_button("删除用户", type="primary")
                        
                        if delete_button and selected_user:
                            # 执行删除
                            success, message = delete_user(selected_user)
                            if success:
                                st.success(message)
                                st.success("✅ 用户删除成功！请刷新页面查看最新用户列表。")
                            else:
                                st.error(message)
                else:
                    st.info("当前只有管理员账户，无法删除")
                
                # 统计信息
                st.subheader("用户统计")
                total_users = len(users_df)
                admin_count = len(users_df[users_df['角色'] == '管理员'])
                regular_count = len(users_df[users_df['角色'] == '普通用户'])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("总用户数", total_users)
                with col2:
                    st.metric("管理员", admin_count)
                with col3:
                    st.metric("普通用户", regular_count)
        
        with subtab2:
            st.subheader("创建新用户")
            
            with st.form("new_user_form"):
                username = st.text_input("用户名", key="new_username", help="用户名必须唯一")
                name = st.text_input("姓名", key="new_name")
                email = st.text_input("邮箱", key="new_email")
                password = st.text_input("密码", type="password", key="new_password", help="请输入安全密码")
                submit_button = st.form_submit_button("创建用户")
                
                if submit_button:
                    if username and name and email and password:
                        # 创建新用户
                        success, message = create_user(username, name, email, password)
                        
                        if success:
                            st.success(message)
                            st.balloons()  # 添加庆祝动画
                        else:
                            st.error(message)
                    else:
                        st.warning("请填写所有字段")

        with subtab3:
            st.subheader("重置用户密码")
            
            # 获取所有用户
            users_df = get_all_users()
            
            if not users_df.empty:
                # 获取所有用户列表
                all_users = users_df['用户名'].tolist()
                
                with st.form("reset_password_form"):
                    selected_user = st.selectbox("选择要重置密码的用户", all_users)
                    new_password = st.text_input("新密码", type="password", help="请输入新的密码")
                    confirm_password = st.text_input("确认密码", type="password", help="请再次输入新密码")
                    reset_button = st.form_submit_button("重置密码")
                    
                    if reset_button:
                        if new_password and confirm_password:
                            if new_password == confirm_password:
                                # 重置密码
                                from app.auth.authentication import reset_user_password
                                success, message = reset_user_password(selected_user, new_password)
                                
                                if success:
                                    st.success(message)
                                    st.info(f"用户 {selected_user} 的新密码是: **{new_password}**")
                                else:
                                    st.error(message)
                            else:
                                st.error("两次输入的密码不一致")
                        else:
                            st.warning("请输入新密码并确认")
            else:
                st.info("暂无用户可重置密码")

def render_admin_page():
    admin_page() 