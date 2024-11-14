import streamlit as st
import subprocess
import os
import time

# FletのWebアプリを起動
def start_flet_app():
    # Fletアプリの実行
    subprocess.Popen(["python", "app_main.py"])

    # Fletアプリが起動するまで少し待機
    time.sleep(5)

    # FletアプリのWebURL（ここではデフォルトのlocalhostで動作する仮定）
    flet_url = "http://localhost:8552"

    return flet_url

# Streamlitで表示
st.title("FletのUI表示")

if st.button("Fletアプリを実行"):
    try:
        # Fletアプリをバックグラウンドで起動
        flet_url = start_flet_app()

        st.success(f"Fletアプリが実行されました！以下のURLで表示されています：")
        st.markdown(f"[Fletアプリへ移動]({flet_url})")

    except Exception as e:
        st.error(f"Fletアプリの実行に失敗しました: {e}")

