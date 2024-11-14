#画像差異アプリのメニューを管理する


import flet as ft
#from flet import *
import os
import shutil
#自作モジュール

from App_Functionality import APP_Page_image_difference as PID

# 画像が保存されているフォルダのパス
base_folder_path = os.path.join(os.getcwd(), '類似画像検索アプリ', '計算済み画像')



Page1="/hikaku"
Page4="/hikaku"

path = os.getcwd()
gazousyori_file=path+"/画像差異アプリ/画像処理用"
PDF_file_A=path+"/画像差異アプリ/画像A"
PDF_file_B=path+"/画像差異アプリ/画像B"
PDF_file_AB=path+"/画像差異アプリ/画像AB"
image_difference_dir = path+'/画像差異アプリ/画像差異検出'
SAVE_file=path+"/画像差異アプリ/画像保管用"





#ページ移動用のクラス
class Page_Route:
    def __init__(self, route_name):
        self.Page_name= route_name
        
class Page_Move(Page_Route):
    def open_test(self, page):
        page.go(self.Page_name)


class Feature_Selection:
    def __init__(self):
        self.Feature_name= "Feature_name"

def main(page: ft.Page):
    page.title = "画像差異アプリ"  # タイトル
    page.scroll = "ADAPTIVE"   #"ADAPTIVE": デバイスやウィンドウサイズに応じてスクロールが動的に適用され、レスポンシブなスクロール動作になります。

    # ---------------------------------

    
    def close_dialog(e):
                page.close(e.control.parent)

    # ページを更新する
    def route_change(e):
        print("Route change:", e.route)
        
        # トップページに来たらpage.viewを初期化
        if page.route == "/":
         page.views.clear()

        # トップページ（常にviewに追加する）
        if page.views==[]:

          # ウィンドウリサイズイベントハンドラを登録
         #page.on_window_event = on_window_resize
         page_width=page.window.width
         page_height=page.window.height

         page.views.append(
            ft.View(
                "/",
                [
                    ft.AppBar(title=ft.Text("トップページ"),bgcolor=ft.colors.GREEN,),
                    ft.Container(image_src='背景画像/main01.jpg',
                                 image_opacity=0.5,
                                 image_fit="FILL",
                            content=ft.Column([
                                               ft.ElevatedButton(content=ft.Text(value="画像差異検出", size=40), on_click=lambda e: Page_Move(Page1).open_test(page),),
                                               ],
                                                scroll=ft.ScrollMode.ALWAYS, spacing=10, expand=True),
                            border=ft.border.all(1, ft.colors.BLACK),
                            padding=10,
                            width=page_width,
                            height=page_height,
                        )
                ],
                scroll="auto",
            )
         )


        # 画像差異を表示するページ
        if page.route == Page1:
            PID.Page_image_difference(page)
        # ページ更新
        page.update()
        
        #同じページが連続した場合は消す
        if len(page.views)>=2:
         if str(page.views[-2])== str(page.views[-1]):
            page.views.pop()



    # 現在のページを削除して、前のページに戻る
    def view_pop_2(e):
        print("View pop:", e.view)
        print((page.views))
        page.views.pop()
        print("View pop2:")
        print((page.views))
        top_view = page.views[-1]
        page.go(top_view.route)


    # ---------------------------------
    # イベントの登録
    # ---------------------------------
    # ページ遷移イベントが発生したら、ページを更新
    page.on_route_change = route_change
    #page.on_route_change は、イベントハンドラ（イベントの処理を行う関数）を設定するための属性です。具体的には、ページのルート（URLパス）が変更された際に実行される関数を指定するために使用されます。
    
    # AppBarの戻るボタンクリック時、前のページへ戻る
    page.on_view_pop = view_pop_2

    # ---------------------------------
    # 起動時の処理
    # ---------------------------------
    # ページ遷移を実行
    page.go(page.route)

# アプリの起動
ft.app(target=main)