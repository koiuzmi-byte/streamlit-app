import streamlit as st
import subprocess
import os

# ウィンドウのタイトル設定
st.title("app_main.py 実行")

# ボタンを作成
if st.button("app_main.pyを実行"):
    try:
        # app_main.py のパスを指定（現在のディレクトリにある前提）
        script_path = os.path.join(os.getcwd(), "app_main.py")

        # app_main.py をバックグラウンドで実行
        subprocess.Popen(["python", script_path])
        st.success("app_main.py が実行されました！")
    except Exception as e:
        st.error(f"app_main.py の実行に失敗しました: {e}")

