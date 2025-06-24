import yaml
import streamlit as st
import streamlit_authenticator as stauth
import os
from datetime import datetime
import pandas as pd

# 读取配置文件
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config

# 保存查询记录
def save_query_record(username, cas_number, result, usage_purpose=""):
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'query_logs.csv')
    
    # 获取当前时间
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 创建新记录
    new_record = pd.DataFrame({
        '用户名': [username],
        'CAS号': [cas_number],
        '使用用途': [usage_purpose],
        '查询时间': [timestamp],
        '查询结果': [result]
    })
    
    # 检查日志文件是否存在
    if os.path.exists(log_path):
        # 如果存在，追加记录
        logs = pd.read_csv(log_path)
        # 确保新增列存在（向后兼容）
        if '使用用途' not in logs.columns:
            logs['使用用途'] = ""
        logs = pd.concat([logs, new_record], ignore_index=True)
    else:
        logs = new_record
    
    # 保存日志
    logs.to_csv(log_path, index=False)

# 初始化验证器
def setup_authenticator():
    config = load_config()
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    return authenticator

# 创建新用户
def create_user(username, name, email, password):
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    
    # 读取现有配置
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    
    # 生成密码哈希
    hashed_password = stauth.Hasher([password]).generate()[0]
    
    # 检查用户名是否已存在
    if username in config['credentials']['usernames']:
        return False, "用户名已存在"
    
    # 添加新用户（同时保存明文密码和加密密码）
    config['credentials']['usernames'][username] = {
        'email': email,
        'name': name,
        'password': hashed_password,  # 用于验证的加密密码
        'plain_password': password    # 用于管理员查看的明文密码
    }
    
    # 保存配置
    with open(config_path, 'w', encoding='utf-8') as file:
        yaml.dump(config, file, default_flow_style=False)
    
    return True, "用户创建成功"

# 获取所有查询记录
def get_all_query_logs():
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'query_logs.csv')
    if os.path.exists(log_path):
        logs = pd.read_csv(log_path)
        # 确保新增列存在（向后兼容）
        if '使用用途' not in logs.columns:
            logs['使用用途'] = ""
        return logs
    return pd.DataFrame(columns=['用户名', 'CAS号', '使用用途', '查询时间', '查询结果'])

# 获取所有用户信息
def get_all_users():
    try:
        config = load_config()
        users_data = []
        
        for username, user_info in config['credentials']['usernames'].items():
            # 确定用户角色
            role = "管理员" if username == "admin" else "普通用户"
            
            # 获取明文密码，如果没有则显示提示
            plain_password = user_info.get('plain_password', '请重新设置密码')
            
            users_data.append({
                '用户名': username,
                '姓名': user_info.get('name', '未知'),
                '邮箱': user_info.get('email', '未知'),
                '密码': plain_password,  # 显示明文密码
                '角色': role
            })
        
        return pd.DataFrame(users_data)
    except Exception as e:
        print(f"获取用户列表时出错: {e}")
        return pd.DataFrame(columns=['用户名', '姓名', '邮箱', '密码', '角色'])

# 删除用户
def delete_user(username):
    if username == "admin":
        return False, "不能删除管理员账户"
    
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    
    try:
        # 读取现有配置
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        
        # 检查用户是否存在
        if username not in config['credentials']['usernames']:
            return False, "用户不存在"
        
        # 删除用户
        del config['credentials']['usernames'][username]
        
        # 保存配置
        with open(config_path, 'w', encoding='utf-8') as file:
            yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
        
        return True, f"用户 {username} 删除成功"
    except Exception as e:
        return False, f"删除用户时出错: {e}"

# 重置用户密码
def reset_user_password(username, new_password):
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    
    try:
        # 读取现有配置
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        
        # 检查用户是否存在
        if username not in config['credentials']['usernames']:
            return False, "用户不存在"
        
        # 生成新的密码哈希
        hashed_password = stauth.Hasher([new_password]).generate()[0]
        
        # 更新用户密码
        config['credentials']['usernames'][username]['password'] = hashed_password
        config['credentials']['usernames'][username]['plain_password'] = new_password
        
        # 保存配置
        with open(config_path, 'w', encoding='utf-8') as file:
            yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
        
        return True, f"用户 {username} 的密码重置成功"
    except Exception as e:
        return False, f"重置密码时出错: {e}" 