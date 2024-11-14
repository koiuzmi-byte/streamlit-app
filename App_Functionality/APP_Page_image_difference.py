import flet as ft
#from flet import *
from PIL import Image as PILImage
import os
import shutil
import glob
import time
import pygetwindow as gw
#自作モジュール
from App_Functionality.Image_Difference import DIFF
import glob
import cv2
import numpy as np

path = os.getcwd()
current_working_directory = os.getcwd()
Page1="/PDF→PNG"
Page3="/AKAZE"
Page4="/hikaku"
gazousyori_file=path+"/画像差異アプリ/画像処理用"
PDF_file_A=path+"/画像差異アプリ/画像A"
PDF_file_B=path+"/画像差異アプリ/画像B"
PDF_file_AB=path+"/画像差異アプリ/画像AB"
image_difference_dir = path+'/画像差異アプリ/画像差異検出'
SAVE_file=path+"/画像差異アプリ/画像保管用"

#タブの初期値
last_selected_index=0

button_A1="ファルダ選択\n(画像A)"
button_A2="ファイル選択\n(画像A)"
button_B1="ファルダ選択\n(画像B)"
button_B2="ファイル選択\n(画像B)"

def create_folders_one(folder_path):
    """指定されたパスにフォルダを作成します。存在する場合は削除して新しく作成します。"""
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)  # フォルダが存在する場合、削除します。
    os.makedirs(folder_path)  # 新しいフォルダを作成します。

def Create_folder_ALL():
    # 各フォルダを作成する
    for folder in [gazousyori_file, PDF_file_A, PDF_file_B, PDF_file_AB, image_difference_dir, SAVE_file]:
        create_folders_one(folder)


def RESET_ALL(page):
    page.controls.clear()
    Create_folder_ALL()
    Page_image_difference(page)
    page.update()


#ページ移動用のクラス
class Page_Route:
    def __init__(self, route_name):
        self.Page_name= route_name
        
class Page_Move(Page_Route):
    def open_test(self, page):
        page.controls.clear()
        page.go(self.Page_name)

# 画像読込
# cv2.imread()は日本語パスに対応していないのでその対策
#ファイルパスをnpで読み込んでcv2用のパスに変換する
def imread(filename, flags=cv2.IMREAD_UNCHANGED, dtype=np.uint8):
    try:
        n = np.fromfile(filename, dtype)
        img = cv2.imdecode(n, flags)
        return img  #narray形式
    except Exception as e:
        print(e)
        return None

# 画像保存(cv2→Pillow)
def imwrite(img,output_path):
    try:
       # カラー画像のときは、BGRからRGBへ変換する
       if img.shape[2] == 3:
         img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
       elif img.shape[2] == 4:  # 透過
         img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)

       # NumPyからPillowへ変換
       pil_image = Image.fromarray(img)
       # Pillowで画像ファイルへ保存
       pil_image.save(output_path)

    except Exception as e:
        print(e)
        return None
    
# フォルダを作成または再作成する関数
def create_or_recreate_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)

# 必要なすべてのフォルダを作成する関数
def create_folders():
    folders = [gazousyori_file, PDF_file_A, PDF_file_B, PDF_file_AB, image_difference_dir, SAVE_file]
    for folder in folders:
        create_or_recreate_folder(folder)

#ダミー画像を作る
def Create_dummy(fullpass_A,fullpass_B):
     if len(fullpass_A) > len(fullpass_B):
        i=len(fullpass_A)-len(fullpass_B)
        number=len(fullpass_B)
        for dummy_i in range(1,i+1):
            # 白色のダミー画像を作成（例えば、200x200ピクセル）
            dummy_image = PILImage.new("RGB", (200, 200), color=(255, 255, 255))
            
            # 画像を一時ファイルとして保存し、パスを取得
            dummy_image_path = PDF_file_B+"/dummy_"+str(dummy_i)+".png"
            dummy_image.save(dummy_image_path)
            
            # ダミー画像のパスをfullpass_Bに追加
          
            fullpass_B.append([[number+dummy_i-1], [dummy_image_path]])
     elif len(fullpass_B) > len(fullpass_A):
        i=len(fullpass_B)-len(fullpass_A)
        number=len(fullpass_A)
        for dummy_i in range(1,i+1):
            # 白色のダミー画像を作成（例えば、200x200ピクセル）
            dummy_image = PILImage.new("RGB", (200, 200), color=(255, 255, 255))
            
            # 画像を一時ファイルとして保存し、パスを取得
            dummy_image_path = PDF_file_A+"/dummy_"+str(dummy_i)+".png"
            dummy_image.save(dummy_image_path)
            
            # ダミー画像のパスをfullpass_Bに追加
            fullpass_A.append([[number+dummy_i-1], [dummy_image_path]])



def update_container_height(e,page,container):
    container.height = page.window.height - 120
    print("container.height",container.height)
    page.update()

def update_container_width(e,page,container,i):
    if i=="A":
      container.width = (page.width/3)
      print("container.width",container.width)
    if i=="AB":
      container.width = (page.width/6)
      print("container.width",container.width)
    if i=="C":
      container.width = (page.width)
      print("container.width",container.width)
    page.update()



def Page_image_difference(page):
            Create_folder_ALL()
            
            #画像を更新する
            #タブリストをもう一度作り直して、表示する
            def pick_image_result(page,page4_done,src_image,i,fullpass_AB):
                            # メニュー項目を作成
                            def show_context_menu(e):
                                print("右クリック")
                                image_path = image_AB  # 例: "C:/path/to/your/image.png"

                                # 画像のあるフォルダを開く
                                if os.path.isfile(image_path):  # ファイルが存在するかチェック
                                    folder_path = os.path.dirname(image_path)  # フォルダパスを取得
                                    print(f"Opening folder: {folder_path}")
                                    os.startfile(folder_path)  # フォルダをエクスプローラーで開く
                                    # エクスプローラーのウィンドウが開くのを待つ
                                    time.sleep(1)  # 1秒待機（適宜調整）
        
                                    # 最前面に表示するための処理
                                    try:
                                        # エクスプローラーのウィンドウを取得して最前面に持ってくる
                                        windows = gw.getWindowsWithTitle('エクスプローラー')  # エクスプローラーのウィンドウを取得
                                        if windows:
                                            window = windows[0]  # 最初のウィンドウを選択
                                            window.activate()  # 最前面に持ってくる
                                    except Exception as e:
                                        print(f"ウィンドウ操作に失敗しました: {e}")
                                else:
                                    print("指定されたファイルが存在しません。")
                                page.update()



                            global last_selected_index
                            nonlocal tab_done
                            nonlocal image_AB
                            nonlocal image_pass
                            nonlocal progress_bar_1
                            nonlocal progress_bar_text
                            nonlocal Progress_Ring

                            image_AB=None

                            image_pass=src_image
 
                            # グローバル変数の初期化
                            if 'last_selected_index' not in globals():
                                last_selected_index = 0

                            def on_tab_change(e):
                                 global last_selected_index
                                 last_selected_index = e.control.selected_index
                                 print(f"Selected tab index: {last_selected_index}")
                            print(f"Type of page: {type(page)}")
                            page_width=page.window.width
                            page_height=page.window.height
                            #一度クリアにする
                            page4_done.controls.clear() 

                            
                            image_AB=image_pass
                            if fullpass_AB !=[]:
                                image_AB=fullpass_AB[i]
                                page.update() 
                            print("タブを更新しました",image_AB)
                            image_component = ft.Image(src=image_AB)

                            print("image_component",image_component)

                            progress_bar_1 = ft.ProgressBar(width=400, color="green", bgcolor="#eeeeee", bar_height=10, visible=False)
                            progress_bar_1.value = 0.0
                            progress_bar_text=ft.Text("画像検出率",weight=ft.FontWeight.W_500,color="red",size=30, visible=False)
                            Progress_Ring=ft.ProgressRing(visible=False,color=ft.colors.GREEN)
                            TAB1_text_after=ft.Text("100%になると完了です。結果を表示できます。\n左側の画像AからBの順番でクリックし、\n上の「検出結果」をクリックすると、違いが色で示されます。\n　灰色：同一部分（重なり）\n　緑色：画像Aにのみある部分\n　赤色：画像Bにのみある部分\n\n検出結果の画像上で右クリックすれば画像があるフォルダが開きます",
                                                                                    style=ft.TextStyle(font_family="Noto Sans JP", weight="normal",size=18 ))

                            tab_list = ft.Tabs(
                                    selected_index=last_selected_index,      #最初に表示されるタブのインデックス（位置）を指定しています。ここでは 0 が設定されているため、「A・B表示」というタブが初期選択されます。
                                    animation_duration=300,   #タブの切り替えにかかるアニメーションの時間（ミリ秒単位）を設定しています
                                    on_change=on_tab_change, 
                                    tabs=[
                                        ft.Tab(
                                            tab_content=ft.Text("A・B表示",
                                                                 style=ft.TextStyle(font_family="Noto Sans JP",weight="bold",size=20  # 必要に応じてサイズを変更
                                                                )),
                                            content=ft.Container(
                                                      content=ft.Column([Progress_Ring,
                                                                        progress_bar_text,
                                                                        progress_bar_1,
                                                                        TAB1_text_after,],
                                                                              alignment=ft.MainAxisAlignment.CENTER),
                                                                        alignment=ft.alignment.center,
                                                                        #alignment=ft.MainAxisAlignment.CENTER ,
                                                                        bgcolor=ft.colors.GREY_400,
                                                                        ),),
                                        ft.Tab(
                                            tab_content=ft.Row(
                                                    [
                                                      ft.Icon(ft.icons.SEARCH, tooltip="画像差異の結果を表示"),
                                                      ft.Text("検出結果",
                                                               style=ft.TextStyle(font_family="Noto Sans JP",weight="bold",size=20))
                                                    ],
                                                     spacing=4  # アイコンとテキストの間のスペースを調整
                                                  ),
                                            content= ft.GestureDetector(on_secondary_tap=lambda e:show_context_menu(e),
                                                                         content=(ft.InteractiveViewer(
                                                min_scale=0.1,
                                                max_scale=15,
                                                boundary_margin=ft.margin.all(20),
                                                on_interaction_start=lambda e: print(e),
                                                on_interaction_end=lambda e: print(e),
                                                on_interaction_update=lambda e: print(e),
                                                content=image_component
                                            )if image_AB is not None else None),)

                                            
                                         
                                              ),
                                        ft.Tab(
                                            tab_content=ft.Row([ft.Icon(ft.icons.IMAGE_OUTLINED),
                                                                ft.Text("元の画像",
                                                                 style=ft.TextStyle(font_family="Noto Sans JP",weight="bold",size=20  # 必要に応じてサイズを変更
                                                                )),]
                                            ),
                                            content=ft.InteractiveViewer(
                                                min_scale=0.1,
                                                max_scale=15,
                                                boundary_margin=ft.margin.all(20),
                                                on_interaction_start=lambda e: print(e),
                                                on_interaction_end=lambda e: print(e),
                                                on_interaction_update=lambda e: print(e),
                                                content=ft.Image(
                                                    src=image_pass
                                                )
                                            )
                                        ),
                                    ],
                                    expand=1,
                                    divider_height=10,
                                    divider_color=ft.colors.WHITE,
                                    indicator_border_side=ft.BorderSide(width=10, color=ft.colors.BLACK) ,
                                    label_color=ft.colors.RED,
                        
                                                )
                            #tabを表示する用のコンテナ
                            tab_done=ft.Column(controls=[
                                                 ft.Container(
                                                         content=tab_list,
                                                         bgcolor=ft.colors.GREY_400,
                                                         height=page.window_height - 120,
                                                         expand=True,
                                                         ink=True,
                                                         padding=5,
                                                         on_click=lambda e: print("タブをクリックしました,",image_AB),
                                                              )
                                                        ])  
                 

                            page4_done.controls.append(tab_done)
                            # レイアウトを構築
                            page4_done.update()
                            tab_list.update()
                            page.update()

            def Show_fullpass(image_done,fullpass,fullpass_AB,color,):    #page4_doneはタブ画面のコントロール、image_doneは画像の表示コントロール、fullpassは画像の順番、fullpass＿ABは画像差異の順番
                        
                        nonlocal image_pass
                        nonlocal image_AB

                           #ドラッグ＆ドロップで画像の順番を入れ替えるための関数
                        def swap_images(e, target_index):
                            # ドラッグされている画像の情報を取得
                            src_image = e.control.page.get_control(e.src_id)
                            source_index=src_image.data
                            print("target_index:",target_index)
                            print("source_index:",source_index)

                            fullpass[source_index][1][0], fullpass[target_index][1][0] = fullpass[target_index][1][0], fullpass[source_index][1][0]
                            print("fullpassは",fullpass)
                            Show_fullpass(image_done,fullpass,fullpass_AB,color)
                        #表示するコンテナと画像リストを削除
                        image_done.controls.clear()

            
                        for i,src_image in  enumerate(fullpass):
                           image_pass = src_image[1][0]  # 画像のURLを変数に格納
                           i=src_image[0][0]
                           print(src_image)
                           print(i)
                           draggable_container = ft.Draggable(
                                                                group="images",
                                                                content=ft.Container(
                                                                                      content=ft.Column(
                                                                                                         controls=[
                                                                                                         ft.Container(
                                                                                                                       content=ft.Image(
                                                                                                                                         src=image_pass,
                                                                                                                                         expand=True ,
                                                                                                                                         fit=ft.ImageFit.CONTAIN
                                                                                                                                     ),
                                                                                                                       expand=True ,
                                                                                                                       alignment=ft.alignment.center  # 画像を中央に配置
                                                                                                                   ),
                                                                                                       ft.Container(content=ft.Text(
                                                                                                                f" No.{i}\n {image_pass.split('/')[-1]}",
                                                                                                                color=ft.colors.BLACK,
                                                                                                                size=15,
                                                                                                                style=ft.TextStyle(weight=ft.FontWeight.BOLD,),  # 太字に設定      
                                                                                                                overflow=ft.TextOverflow.ELLIPSIS,
                                                                                                                tooltip=ft.Tooltip(message=image_pass.split('/')[-1],text_style=ft.TextStyle(size=20, color=ft.colors.WHITE)), 
                                                                                                                bgcolor=ft.colors.RED_100 if color == "red" else ft.colors.GREEN_100 if color == "green" else ft.colors.LIGHT_BLUE_100,
                                                                                                                text_align=ft.TextAlign.LEFT,
                                                                                                              ),)
                                                                                                        
                                                                                                     ],
                                                                                                     expand=True ,
                                                                                             alignment=ft.MainAxisAlignment.CENTER  # Columnの要素を垂直方向に中央揃え
                                                                                              ),
                                                                        width=250,
                                                                        height=250,
                                                                        margin=10,
                                                                        tooltip=ft.Tooltip(message=image_pass.split('/')[-1],text_style=ft.TextStyle(size=20, color=ft.colors.WHITE)), 
                                                                        bgcolor=ft.colors.RED_100 if color == "red" else ft.colors.GREEN_100 if color == "green" else ft.colors.LIGHT_BLUE_100,
                                                                        border=ft.border.all(2, ft.colors.RED_100) if color == "red" else ft.border.all(2, ft.colors.GREEN_100) if color == "green" else ft.colors.LIGHT_BLUE_100,
                                                                        ink=True,
                                                                        on_click=lambda e, i=i, src_image=image_pass : pick_image_result(page, page4_done, src_image,i,fullpass_AB),
                                                                       ),
                                                     data=i
                                                  )


                           # DragTargetを作成
                           drag_target = ft.DragTarget(
                                            group="images",
                                            content=ft.Container(
                                                                  width=300,
                                                                  height=300,
                                                                  bgcolor=ft.colors.RED if color == "red" else ft.colors.GREEN if color == "green" else ft.colors.LIGHT_BLUE_100,
                                                                  alignment=ft.alignment.center,
                                                                  content=ft.Column(
                                                                              controls=[draggable_container],
                                                                              auto_scroll=True,  # コンテンツが領域を超えた場合に自動的にスクロール
                                                                              expand=True,  # Columnが親コンテナに合わせて広がる
                                                                          ),
                                                                  border_radius=10,
                                                                  

                                                              ),
                                                              data=i,
                                            on_accept=lambda e, target_index=i: swap_images(e, target_index)
                                          )

                           image_done.controls.append(drag_target)

                        image_done.update()
                        page.update()


            #ファルダログで選択した画像をimageslist_A_and_Bに表示する
            def image_pick_files_result(e: ft.FilePickerResultEvent,i):  #iで画像する像Bなのかを判断
              nonlocal fullpass_A  #関数の外側のも変更可能にする
              nonlocal fullpass_B
              nonlocal fullpass_AB
            

              if i==0:
                 for file_path in glob.glob(os.path.join(PDF_file_A, "*dummy*")):
                     try:
                            os.remove(file_path)
                            print(f"削除しました: {file_path}")
                     except Exception as e:
                            print(f"削除に失敗しました: {file_path}, エラー: {e}")
                            image_paths = []
              elif i==1:
                 for file_path in glob.glob(os.path.join(PDF_file_B, "*dummy*")):
                     try:
                            os.remove(file_path)
                            print(f"削除しました: {file_path}")
                     except Exception as e:
                            print(f"削除に失敗しました: {file_path}, エラー: {e}")
                            image_paths = []

              image_paths = []

              if not e.files:
                # list_paths が空の場合は処理をスキップ
                print("ファイルが選択されませんでした。.")
                return

              #選んだファイルを格納する
              image_paths= [f.path for f in e.files]
              print("image_paths")
              print(image_paths)
              

              if i==0:
                fullpass_A=DIFF.Get_image_path(image_paths,"A")
                
                print("fullpass_A")
                print(len(fullpass_A))
                Create_dummy(fullpass_A,fullpass_B)
                print(("fullpass_B"))
                print((fullpass_B))
                Show_fullpass(image_A,fullpass_A,fullpass_AB,"green")
                Show_fullpass(image_B,fullpass_B,fullpass_AB,"red")
                

              elif  i==1:

                fullpass_B=DIFF.Get_image_path(image_paths,"B")
                print(len(fullpass_A))
                print(len(fullpass_B))
                print((fullpass_B))
                Create_dummy(fullpass_A,fullpass_B)
                Show_fullpass(image_A,fullpass_A,fullpass_AB,"green")
                Show_fullpass(image_B,fullpass_B,fullpass_AB,"red")

            #画像差異を求める関数
            def gazousai_AB():
                nonlocal fullpass_AB
                #表示を
                page4_done.controls.clear() 
                page4_done.controls.append(tab_done)
                fullpass_AB=DIFF.Image_Difference_Detection(page,page4_done,TAB1_text_before,TAB1_text_after,progress_bar_text,progress_bar_1,Progress_Ring,fullpass_A,fullpass_B,fullpass_AB,MODE=True,SAVE=True)
                
                page.update()
            
            def update_button_font_size(page):
                # ウィンドウの幅に基づいて文字サイズを調整
                print("max(5, min(24, page.width // 50)):",max(5, min(24, page.width // 50)))
                return max(5, min(50, page.width // 50))


            #フォルダをリセットする
            create_folders()
            
            
            #使う変数
            fullpass_A=[]   #表示する画像Aのパスのまとめ
            fullpass_B=[]   #表示する画像Aのパスのまとめ
            fullpass_AB=[]   #表示する画像ABのパスのまとめ
            image_AB=None
            image_pass=None
            
            #使うウインドウサイズ
            #page_width=page.window.width
            #page_height=page.window.height


            # ProgressBarの定義
            progress_bar_1 = ft.ProgressBar(width=400, color="green", bgcolor="#eeeeee", bar_height=10, visible=False)
            progress_bar_1.value = 0.0
            progress_bar_text=ft.Text("画像検出率",weight=ft.FontWeight.W_500,color="red",size=30, visible=False)
            Progress_Ring=ft.ProgressRing(visible=False,color=ft.colors.GREEN)
            
            TAB1_text_before=ft.Text("2枚の画像A・Bの違いを比較できます\n左上の緑色の画像Aボタンから画像を開いてください\n右隣の赤色の画像Bボタンから画像を開いてください\n右隣の黒色の検出ボタンで検出が開始されます",
                                                                                    style=ft.TextStyle(font_family="Noto Sans JP", weight="normal",size=18 ))
            TAB1_text_after=ft.Text("100%になると完了です。結果を表示できます。\n左側の画像AからBの順番でクリックし、\n上の「検出結果」をクリックすると、違いが色で示されます。\n　灰色：同一部分（重なり）\n　緑色：画像Aにのみある部分\n　赤色：画像Bにのみある部分\n\n検出結果の画像上で右クリックすれば画像があるフォルダが開きます",
                                                                                    style=ft.TextStyle(font_family="Noto Sans JP", weight="normal",size=18 ), visible=False)
            #tabを表示する用(Progress_Ring,progress_bar_text, progress_bar_1)
            tab_list = ft.Tabs(
                        selected_index=0,      #最初に表示されるタブのインデックス（位置）を指定しています。ここでは 0 が設定されているため、「A・B表示」というタブが初期選択されます。
                        animation_duration=300,   #タブの切り替えにかかるアニメーションの時間（ミリ秒単位）を設定しています
                        tabs=[
                            ft.Tab(
                                tab_content=ft.Text("A・B表示",
                                                     style=ft.TextStyle(font_family="Noto Sans JP",weight="bold",size=20  # 必要に応じてサイズを変更
                                                    )),
                                content=ft.Container(
                                                      content=ft.Column([Progress_Ring,
                                                                        progress_bar_text,
                                                                        progress_bar_1,
                                                                        TAB1_text_before,
                                                                        TAB1_text_after,],
                                                                              alignment=ft.MainAxisAlignment.CENTER),
                                                                        alignment=ft.alignment.center,
                                                                        #alignment=ft.MainAxisAlignment.CENTER ,
                                                                        bgcolor=ft.colors.GREY_400,
                                                                        ),),
                            ft.Tab(
                                            tab_content=ft.Row(
                                                    [
                                                      ft.Icon(ft.icons.SEARCH, tooltip="画像差異の結果を表示"),
                                                      ft.Text("検出結果",
                                                               style=ft.TextStyle(font_family="Noto Sans JP",weight="bold",size=20))
                                                    ],
                                                     spacing=4  # アイコンとテキストの間のスペースを調整
                                                  ),
                                            content=ft.InteractiveViewer(
                                                min_scale=0.1,
                                                max_scale=15,
                                                boundary_margin=ft.margin.all(20),
                                                on_interaction_start=lambda e: print(e),
                                                on_interaction_end=lambda e: print(e),
                                                on_interaction_update=lambda e: print(e),
                                                content=ft.Image(
                                                    src=image_AB
                                                )
                                            )if image_AB is not None else None
                                         
                                              ),
                                        ft.Tab(
                                            tab_content=ft.Row([ft.Icon(ft.icons.IMAGE_OUTLINED),
                                                                ft.Text("元の画像",
                                                                 style=ft.TextStyle(font_family="Noto Sans JP",weight="bold",size=20  # 必要に応じてサイズを変更
                                                                )),]
                                            ),
                                            content=ft.InteractiveViewer(
                                                min_scale=0.1,
                                                max_scale=15,
                                                boundary_margin=ft.margin.all(20),
                                                on_interaction_start=lambda e: print(e),
                                                on_interaction_end=lambda e: print(e),
                                                on_interaction_update=lambda e: print(e),
                                                content=ft.Image(
                                                    src=image_pass
                                                )
                                            )if image_AB is not None else None
                                        ),
                        ],
                        expand=1,
                        divider_height=10,
                        divider_color=ft.colors.WHITE,
                        indicator_border_side=ft.BorderSide(width=10, color=ft.colors.BLACK) ,
                        label_color=ft.colors.RED,
                        
                                    )
            
            #tabを表示する用のコンテナ
            tab_done=ft.Column(controls=[
                                     ft.Container(
                                             content=tab_list,
                                             bgcolor=ft.colors.GREY_400,
                                             height=page.window_height - 120,
                                             expand=True,
                                             ink=True,
                                             padding=5,
                                             on_click=lambda e: print("タブをクリックしました"),
                                                  )
                                            ])  
                                     
            #右枠に画像を表示する大枠
            page4_done = ft.Column(  # 画像拡大表示用
                              controls=[tab_done
                                 ],
                                 expand=True,
                             ) 


            imageslist_A_and_B = ft.Column()   #左の表を格納する用
            base_field=ft.Column() 


            selected_files = ft.Text()
            selected_files = ft.Text()


                               

            image_A = ft.Column(
                       spacing=10,
                       height=200,
                       width=200,
                       scroll=ft.ScrollMode.ALWAYS,
                        )
            image_B = ft.Column(
                       spacing=10,
                       height=200,
                       width=200,
                       scroll=ft.ScrollMode.ALWAYS,
                        )



            #画像リストAの表示用

            image_list_A=ft.Container(
                                content=image_A,
                                bgcolor=ft.colors.GREEN,
                                #height=max(page_height-150,100),
                                expand=True,
                                width=page.width/6,
                                ink=True,
                                 on_click=lambda e: print("image_list_A clicked!"),
                                   )
            
            #画像リストBの表示用
            image_list_B=ft.Container(
                    content=image_B,
                    bgcolor=ft.colors.RED,
                    expand=True,
                    width=page.width/6,
                    ink=True,
                    on_click=lambda e: print("image_list_B with Ink clicked!"),
                )
             ##画像A,Bのボタンを押した際のダイアログボックス                  
            pick_files_dialog_A = ft.FilePicker(on_result=lambda e:image_pick_files_result(e,0))
            page.overlay.append(pick_files_dialog_A)
            pick_files_dialog_B = ft.FilePicker(on_result=lambda e:image_pick_files_result(e,1))
            page.overlay.append(pick_files_dialog_B)
           
            font_size = update_button_font_size(page)
           #ボタンのコンテナ
            button_AB=ft.Container(content=ft.Row(controls=[ft.ElevatedButton("画像A", on_click=lambda e: pick_files_dialog_A.pick_files(allow_multiple=True,allowed_extensions=["pdf", "png", "jpg","tif"]),
                                                                                          style=ft.ButtonStyle(bgcolor=ft.colors.GREEN,      # ボタンの背景色を緑に設定
                                                                                                               color=ft.colors.WHITE ,text_style=ft.TextStyle(font_family="Noto Sans JP",weight="bold", size=15),), # テキストの色を白に設定
                                                                                        expand=True,                     # ボタンがRowの幅に合わせて広がる
                                                                                        height=60     
                                                                             ),
                                                            ft.Container(width=10),
                                                            ft.ElevatedButton("画像B", on_click=lambda e: pick_files_dialog_B.pick_files(allow_multiple=True,allowed_extensions=["pdf", "png", "jpg","tif"]),
                                                                                                                                         style=ft.ButtonStyle(bgcolor=ft.colors.RED,color=ft.colors.WHITE  ,
                                                                                                                                                              text_style=ft.TextStyle(font_family="Noto Sans JP",weight="bold", size=15)       # テキストの色を白に設定
                                                                                        ),
                                                                                        expand=True,                     # ボタンがRowの幅に合わせて広がる
                                                                                        height=60 ),
                                                            ft.Container(width=10),
                                                            ft.ElevatedButton("検出", icon=ft.Icon(ft.icons.SEARCH, size=24),on_click=lambda e: gazousai_AB(),
                                                                                          style=ft.ButtonStyle(
                                                                                     
                                                                                                               bgcolor=ft.colors.BLACK,      # ボタンの背景色を緑に設定
                                                                                                               color=ft.colors.WHITE ,  
                                                                                                               text_style=ft.TextStyle(font_family="Noto Sans JP",
                                                       weight="bold", size=15)      # テキストの色を白に設定
                                                                                        ),expand=True,                     # ボタンがRowの幅に合わせて広がる
                                                                                        height=60 )
                                                        ],expand=True,  # Row自体が親Containerの幅に広がる
        alignment=ft.MainAxisAlignment.SPACE_EVENLY  # ボタン間のスペースを均等に配置
             ),
                                  bgcolor=ft.colors.GREY_400,
                                  height=60,
                                  width= page.width/3,
                                  ink=True,
                                  alignment=ft.alignment.center,
                                  padding=5,
                                  on_click=lambda e: print("Clickable transparent with Ink clicked!"),
                                  )
            #画像A、画像Bのリストを画像付きで表示するコンテナ
            imageslist_A_and_B.controls.append(ft.Container(
                                               content=ft.Column(controls=[
                                                                      button_AB,
                                                                      ft.Row(controls=[ft.Column(controls=[image_list_A],expand=True,),
                                                                                       ft.Column(controls=[image_list_B],expand=True,)],expand=True,)
                                                                      ]),
                                               bgcolor=ft.colors.GREY_400,
                                               expand=True,
                                               ink=True,
                                               on_click=lambda e: print("imageslist_A_and_Bをクリックしました"),
                                              )    
                                )



            
            base_field.controls.append(ft.Container(
                                                    content=ft.Row(controls=[
                                                                             imageslist_A_and_B,
                                                                             page4_done,
                                                                            ]),
                                                    bgcolor=ft.colors.WHITE,
                                                    expand=True,
                                                    ink=True,
                                                    height=page.window_height-120,
                                                    on_click=lambda e: print("base_fieldをクリックしました"),
                                                    ) ,   
                                                 )
            


            #アプリバーの設定
            APP_BAR_gazousai= ft.AppBar(
                               leading=ft.Icon(name=ft.icons.BROKEN_IMAGE_SHARP ,color=ft.colors.WHITE, size=50),
                               leading_width=40,
                               title=ft.Text("画像差異検出アプリ",size=30,weight=ft.FontWeight.W_500,color=ft.colors.WHITE,bgcolor=ft.colors.BLACK),
                               bgcolor=ft.colors.BLACK,
                               #back_button=False,  # 自動生成される戻るボタンを無効化
                               actions=[
                                       ft.ElevatedButton("リセット",icon=ft.icons.LAYERS_CLEAR_SHARP, on_click=lambda e:RESET_ALL(page),icon_color=ft.colors.WHITE,
                                                          style=ft.ButtonStyle(color={ ft.ControlState.HOVERED: ft.colors.WHITE,
                                                                                       ft.ControlState.FOCUSED: ft.colors.BLUE,     #ボタンがフォーカスされた状態（クリックやタブ操作で選択されたとき）では、テキスト色を青 (BLUE) にします。
                                                                                       ft.ControlState.DEFAULT: ft.colors.WHITE,   #通常状態（何も操作がされていないとき）は、テキスト色が黒 (BLACK) になります。
                                                                                     },
                                                                               bgcolor={ft.ControlState.FOCUSED: ft.colors.PINK_200, "": ft.colors.BLUE_GREY},   #ボタンが「フォーカス」状態のとき、背景色が薄いピンク色
                                                                               padding={ft.ControlState.HOVERED: 10},
                                                                               overlay_color=ft.colors.TRANSPARENT,
                                                                               elevation={"pressed": 0, "": 1},
                                                                               animation_duration=500,     #状態が変わる際のアニメーションに500ミリ秒（0.5秒）かけることを意味
                                                                               side={
                                                                                   ft.ControlState.DEFAULT: ft.BorderSide(2, ft.colors.WHITE),   # 触れていない時の線の太さ
                                                                                   ft.ControlState.HOVERED: ft.BorderSide(4, ft.colors.WHITE),   # ホバー時の線の太さ
                                                                               },
                                                                               shape={
                                                                                   ft.ControlState.HOVERED: ft.RoundedRectangleBorder(radius=20),
                                                                                   ft.ControlState.DEFAULT: ft.RoundedRectangleBorder(radius=20),
                                                                               },
                                                                               text_style=ft.TextStyle(font_family="Noto Sans JP",weight="bold",  # 太字に設定size=20     
                                                                                                       ),
                                                                    ),
                                                height=40
                                                           ),
                                        # ボタン間にスペースを追加
                                         ft.Container(width=20),  # 20ピクセルの幅のスペース
                                       ft.ElevatedButton("TOP",icon="home", on_click=lambda e:Page_Move("/").open_test(page),icon_color=ft.colors.WHITE,
                                                          style=ft.ButtonStyle(color={ ft.ControlState.HOVERED: ft.colors.WHITE,
                                                                                       ft.ControlState.FOCUSED: ft.colors.BLUE,     #ボタンがフォーカスされた状態（クリックやタブ操作で選択されたとき）では、テキスト色を青 (BLUE) にします。
                                                                                       ft.ControlState.DEFAULT: ft.colors.WHITE,   #通常状態（何も操作がされていないとき）は、テキスト色が黒 (BLACK) になります。
                                                                                     },
                                                                               bgcolor={ft.ControlState.FOCUSED: ft.colors.PINK_200, "": ft.colors.BLUE_GREY},   #ボタンが「フォーカス」状態のとき、背景色が薄いピンク色
                                                                               padding={ft.ControlState.HOVERED: 10},
                                                                               overlay_color=ft.colors.TRANSPARENT,
                                                                               elevation={"pressed": 0, "": 1},
                                                                               animation_duration=500,     #状態が変わる際のアニメーションに500ミリ秒（0.5秒）かけることを意味
                                                                               side={
                                                                                   ft.ControlState.DEFAULT: ft.BorderSide(2, ft.colors.WHITE),   # 触れていない時の線の太さ
                                                                                   ft.ControlState.HOVERED: ft.BorderSide(4, ft.colors.WHITE),   # ホバー時の線の太さ
                                                                               },
                                                                               shape={
                                                                                   ft.ControlState.HOVERED: ft.RoundedRectangleBorder(radius=20),
                                                                                   ft.ControlState.DEFAULT: ft.RoundedRectangleBorder(radius=20),
                                                                               },
                                                                               text_style=ft.TextStyle(font_family="Noto Sans JP",weight="bold",  # 太字に設定size=20     
                                                                                                       ),
                                                                    ),
                                                height=40
                                                           ),
                                       ]
                                 )

            # base_field2 に expand を設定
            # ページ設定
            page.on_resize = lambda e:[update_container_height(e,page,base_field),update_container_height(e,page,tab_done),
                                        update_container_width(e,page,imageslist_A_and_B,"A"),update_container_width(e,page,button_AB,"A"),
                                        update_container_width(e,page,image_list_A,"AB"),update_container_width(e,page,image_list_B,"AB"),
                                        update_container_width(e,page,base_field,"C"),
                                        # フォントサイズの更新
                                            setattr(button_AB, 'font_size', update_button_font_size(page)),
                                            button_AB.update(),
                                            # フォントサイズを表示
                                                print(f"Updated font size of button_AB: {button_AB.font_size}")
                                            ]
#
            page.views.append(
                ft.View(    
                    route=Page4,
                    scroll="adaptive",
                    controls=[
                        APP_BAR_gazousai,
                        base_field,
                            ],
                    )
                            )
