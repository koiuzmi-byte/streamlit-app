import streamlit as st
import subprocess
import time
from pyngrok import ngrok

# Fletアプリをバックグラウンドで実行し、ngrokで公開する
def start_flet_app():
    # Fletアプリの実行
    subprocess.Popen(["python", "app_main.py"])
    
    # Fletアプリが起動するまで少し待機
    time.sleep(5)
    
    # ngrokでFletのポートを公開
    public_url = ngrok.connect(8552)  # Fletはデフォルトで8552ポート
    return public_url

# Streamlitで表示
st.title("Fletアプリケーション表示")

if st.button("Fletアプリを実行３"):
    try:
        # Fletアプリをバックグラウンドで実行し、公開URLを取得
        flet_url = start_flet_app()

        # FletアプリのURLを表示
        st.success(f"Fletアプリが実行されました！以下のURLで表示されています：")
        st.markdown(f"[Fletアプリへ移動]({flet_url})")

        # iframeとしてFletアプリを埋め込む
        st.markdown(f'<iframe src="{flet_url}" width="100%" height="600"></iframe>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Fletアプリの実行に失敗しました: {e}")
