import streamlit as st
import subprocess
import os
import time

# FletのWebアプリを起動
def start_flet_app():
    # Fletアプリの実行
    try:
        process = subprocess.Popen(["python", "app_main.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # 出力とエラーをキャプチャ
        stdout, stderr = process.communicate()

        # エラーがあった場合、標準エラー出力を表示
        if stderr:
            st.error(f"Fletアプリの起動中にエラーが発生しました:\n{stderr.decode()}")
            return None
        
        # 正常に起動した場合
        st.success("Fletアプリが正常に実行されました！")
        return "http://localhost:8550"  # ポート番号を確認して適切に設定
    except Exception as e:
        st.error(f"Fletアプリの実行中に予期しないエラーが発生しました: {e}")
        return None

# Streamlitで表示
st.title("FletのUI表示")

if st.button("Fletアプリを実行２"):
    flet_url = start_flet_app()

    if flet_url:
        st.success(f"Fletアプリが実行されました！以下のURLで表示されています：")
        st.markdown(f"[Fletアプリへ移動]({flet_url})")
    else:
        st.error("Fletアプリの実行に失敗しました。")
