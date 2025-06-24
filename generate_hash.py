import streamlit_authenticator as stauth

# 生成密码哈希
hashed_passwords = stauth.Hasher(['admin123', 'user123']).generate()

print("管理员密码哈希:", hashed_passwords[0])
print("普通用户密码哈希:", hashed_passwords[1]) 