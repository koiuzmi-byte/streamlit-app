import streamlit as st
import subprocess
import os
import time

# FletアプリのWebアプリを起動
ddef start_flet_app():
    try:
        # Dockerの代わりにローカルでFletアプリを実行
        process = subprocess.Popen(["python", "app_main.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if stderr:
            st.error(f"Fletアプリの起動中にエラーが発生しました:\n{stderr.decode()}")
            return None
        
        st.success("Fletアプリが正常に実行されました！")
        return "http://localhost:8550"
    except Exception as e:
        st.error(f"Fletアプリの実行中に予期しないエラーが発生しました: {e}")
        return None


# Streamlitで表示
st.title("FletのUI表示")

if st.button("Fletアプリを実行"):
    flet_url = start_flet_app()

    if flet_url:
        st.success(f"Fletアプリが実行されました！以下のURLで表示されています：")
        st.markdown(f"[Fletアプリへ移動]({flet_url})")
    else:
        st.error("Fletアプリの実行に失敗しました。")
