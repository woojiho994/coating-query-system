@echo off
REM 设置代码页为UTF-8
chcp 65001
REM 激活Anaconda环境并启动Streamlit应用
set PATH=C:\Users\wooji\anaconda3;C:\Users\wooji\anaconda3\Scripts;C:\Users\wooji\anaconda3\Library\bin;%PATH%
C:\Users\wooji\anaconda3\python.exe -m streamlit run "app.py"
pause