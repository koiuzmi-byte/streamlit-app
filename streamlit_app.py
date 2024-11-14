import streamlit as st
import subprocess
import os
import time

# FletアプリのWebアプリを起動
def start_flet_app():
    try:
        # Dockerコンテナ内でのFletアプリの起動
        process = subprocess.Popen(["docker", "run", "-d", "-p", "8550:8550", "flet-app-image"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # プロセスの標準出力とエラーをキャッチ
        stdout, stderr = process.communicate()

        # エラーが発生した場合
        if stderr:
            st.error(f"Fletアプリの起動中にエラーが発生しました:\n{stderr.decode()}")
            return None
        
        # アプリが起動するまで少し待機
        time.sleep(5)

        # Fletアプリが起動したらlocalhost:8550でアクセスできることを確認
        flet_url = "http://localhost:8550"

        st.success("Fletアプリが正常に実行されました！")
        return flet_url

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
