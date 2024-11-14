
import shutil

import glob
import cv2
import numpy as np
import os
import shutil
from PIL import ImageSequence
from PIL import Image as PILImage
import flet as ft
#from flet import *
#自作モジュール
from .import converter as con  #PDFをPNGに変換する
from .import gazousai_new as ga #２つのPNGの差異を求める

global tab_done

path = os.getcwd()
gazousyori_file=path+"/画像差異アプリ/画像処理用"
PDF_file_A=path+"/画像差異アプリ/画像A"
PDF_file_B=path+"/画像差異アプリ/画像B"
PDF_file_AB=path+"/画像差異アプリ/画像AB"
image_difference_dir = path+'/画像差異アプリ/画像差異検出'
SAVE_file=path+"/画像差異アプリ/画像保管用"


button_A1="ファルダ選択\n(画像A)"
button_A2="ファイル選択\n(画像A)"
button_B1="ファルダ選択\n(画像B)"
button_B2="ファイル選択\n(画像B)"

#タブの初期値
last_selected_index=0


#格納していた画像パスを一度削除して、画像Aの中にあるパスで再度画像パスを作る。
def Get_image_path(image_list, key):
            #選択ファオルダで選択した画像のリスト
            image_list.sort() # ファイルの順番を変える
            image_list= [s.replace('\\', '/') for s in image_list]# ファイルのパスの区切りを「/」に統一
            #画像Aか画像BのどっちにPNGを保存するか決める
            if key=="A":
                path=PDF_file_A
            if key=="B":
                path=PDF_file_B

            #Pngに統一して、それぞれのファイルに保存する
            for s in image_list:
                root, ext = os.path.splitext(s)  # ファイルの拡張子をextに保存する
                if ext ==".pdf":
                 # 選択したPDFファイルをPNGファイルに変換して、指定のファルダに保存する
                   con.pdfhenkan(s ,path)
                if ext ==".tif":
                    img = PILImage.open(s )
                    for i, gazou_page in enumerate(ImageSequence.Iterator(img)):  #tifからpngに変換して保存する。
                       name = os.path.splitext(os.path.basename(s))[0]   #拡張子なしのファイル名を取得
                       gazou_page.save(path+"/"+str(name).format(i)+"_{:02d}".format(i + 1) + ".png")        
                if ext ==".png":
                   name=s .split('/')[-1]
                   shutil.copy(s , path+"/"+str(name))# [画像A]フォルダに画像をコピー

                if ext ==".jpeg":
                    img = PILImage.open(s )
                    for i, gazou_page in enumerate(ImageSequence.Iterator(img)):  #tifからpngに変換して保存する。
                       name = os.path.splitext(os.path.basename(s))[0]   #拡張子なしのファイル名を取得
                       gazou_page.save(path+"/"+str(name).format(i)+"_{:02d}".format(i + 1) + ".png")
                if ext ==".JPG":
                    img = PILImage.open(s )
                    for i, gazou_page in enumerate(ImageSequence.Iterator(img)):  #tifからpngに変換して保存する。
                       name = os.path.splitext(os.path.basename(s))[0]   #拡張子なしのファイル名を取得
                       gazou_page.save(path+"/"+str(name).format(i)+"_{:02d}".format(i + 1) + ".png")
                if ext ==".jpg":
                    img = PILImage.open(s )
                    for i, gazou_page in enumerate(ImageSequence.Iterator(img)):  #tifからpngに変換して保存する。
                       name = os.path.splitext(os.path.basename(s))[0]   #拡張子なしのファイル名を取得
                       gazou_page.save(path+"/"+str(name).format(i)+"_{:02d}".format(i + 1) + ".png")
                
                if ext ==".tiff":
                    img = PILImage.open(s )
                    for i, gazou_page in enumerate(ImageSequence.Iterator(img)):  #tifからpngに変換して保存する。
                       name = os.path.splitext(os.path.basename(s))[0]   #拡張子なしのファイル名を取得
                       gazou_page.save(path+"/"+str(name).format(i)+"_{:02d}".format(i + 1) + ".png")
            
            fullpass=[]
            # [画像A]か[画像B]フォルダ内の画像を入手
            image_list = glob.glob('{}/*.png'.format(path)) \
                                                         + glob.glob('{}/*.jpg'.format(path)) \
 
            image_list.sort() # ファイルの順番を変える(名前順)
            image_list = [s.replace('\\', '/') for s in image_list]# ファイルのパスの区切りを「/」に統一

            print("image_list の結果")
            print(image_list)
            for i,src in  enumerate(image_list):
               src = src  # 画像のURLを変数に格納
               fullpass.append([[i], [src]])
             
            return fullpass



     



# 画像差異終了メッセージをポップアップとして表示
def show_popup(page):
    def close_dlg(e):
        alert_popup.open = False
        page.update()

    alert_popup = ft.AlertDialog(
        title=ft.Text("処理完了"),
        content=ft.Text("画像差異処理が終了しました。"),
        actions=[ft.TextButton("OK", on_click=lambda e: close_dlg(e))]
    )
    # ダイアログをオーバーレイに追加
    page.overlay.append(alert_popup)  # こちらでダイアログをオーバーレイに追加
    alert_popup.open = True  # ダイアログを開く
    page.update()  # ページを更新して変更を反映

# エラーメッセージをポップアップとして表示
def show_error_popup(page, message): 
    def close_dlg(e):
        dialog.open = False
        page.update()
    # エラーダイアログを作成
    dialog = ft.AlertDialog(
        title="Error",
        content=ft.Column([ft.Text(message)]),
        actions=[ft.TextButton("OK", on_click=lambda e: close_dlg(e))],
        on_dismiss=lambda e: print("Dialog dismissed!")  # ダイアログが閉じられた時にメッセージを表示
    )

    # ダイアログをページに追加
    page.overlay.append(dialog)  # overlayに追加することで、画面上に表示
    dialog.open = True  # ダイアログを開く。ここでTrueに設定する
    page.update()  # ページを更新

# 画像差異ボタンを押すと画像差異を求める
def Image_Difference_Detection(page,page4_done,TAB1_text_before,TAB1_text_after,progress_bar_text,progress_bar_1,Progress_Ring,fullpass_A,fullpass_B,fullpass_AB,MODE,SAVE):
        A=len(fullpass_A) 
        B=len(fullpass_B) 

        #進行度を表示
        progress_bar_1.visible = True
        Progress_Ring.visible = True
        progress_bar_1.value = 0.0
        progress_bar_text.visible = True
        progress_bar_text.value = f'画像検出率：{round(progress_bar_1.value,2)}%'

        TAB1_text_before.visible=False
        TAB1_text_after.visible = True

        print(progress_bar_text.value)
        #ページをアップデートして、変更を反映
        page.update()

        # 数が合わないときはダミーを作る
        if A > B:
          try:
           for num in range(B, A):  # fullpath_list_Aの方がBよりも画像リストが多ければ、（画像Aの画像数-画像Bの画像数）分の白画像を作る
             # 白色の画像を作成
            print("fullpass_A[num][1][0]:",fullpass_A[num][1][0])

            img =  PILImage.open(fullpass_A[num][1][0])
            width, height = img.size
            white_image = PILImage.new('RGB', (width, height), color='white')
            # 画像を保存
            i=num+len(fullpass_B)
            filename=str(PDF_file_B)+"/ダミー画像B_"+str(num)+".png"
            white_image.save(filename)
            fullpass_B.insert(i,[[i], [filename]] )
          except Exception as e:
                error_message = f"Error processing image {fullpass_B[num][1][0]}: {e}"
                print(error_message)
                
                # Fletポップアップ表示
                show_error_popup(page, error_message)

        if A < B:
          try:
           for num in range(A, B):  # fullpass_Bの方がAよりも画像リストが多ければ、（画像Bの画像数-画像Aの画像数）分の白画像を作る
            # 白色の画像を作成
            print("fullpass_B[num][1][0]:",fullpass_B[num][1][0])
            img =  PILImage.open(fullpass_B[num][1][0])
            width, height = img.size
            white_image = PILImage.new('RGB', (width, height), color='white')
            # 画像を保存
            i=num+len(fullpass_A)
            filename=str(PDF_file_A)+"/ダミー画像B_"+str(num)+".png"
            white_image.save(filename)
            fullpass_A.insert(i,[[i], [filename]] )
          except Exception as e:
                error_message = f"Error processing image {fullpass_B[num][1][0]}: {e}"
                print(error_message)
                
                # Fletポップアップ表示
                show_error_popup(page, error_message)

        page.update()
        fullpass_AB.clear()

        print("fullpass_A",fullpass_A)
        print("fullpass_B",fullpass_B)

        before_run_gauge=progress_bar_1.value

        for i in range(0, A):
            number=i  #今実行している画像の番号
            thickness_A=int(5)   #画像差異に使う線の太さ
            thickness_B=int(5)
            run_gauge=A

            if MODE==True:
              if SAVE==True:
               gazousai_filename=ga.gazousai(page,progress_bar_1,progress_bar_text,run_gauge,fullpass_A[i][1][0],fullpass_B[i][1][0],thickness_A,thickness_B,"ON","ON",number)
              else:
                gazousai_filename=ga.gazousai(page,progress_bar_1,progress_bar_text,run_gauge,fullpass_A[i][1][0],fullpass_B[i][1][0],thickness_A,thickness_B,"ON","",number)
            else:
                if SAVE==True:
                  gazousai_filename=ga.gazousai(page,progress_bar_1,progress_bar_text,run_gauge,fullpass_A[i][1][0],fullpass_B[i][1][0],thickness_A,thickness_B,"OFF","ON",number)
                else:
                  gazousai_filename=ga.gazousai(page,progress_bar_1,progress_bar_text,run_gauge,fullpass_A[i][1][0],fullpass_B[i][1][0],thickness_A,thickness_B,"OFF","",number)
        
            fullpass_AB.append(gazousai_filename)
            progress_bar_1.value=round((before_run_gauge+1/int(A)),2)
            progress_bar_text.value = f'画像検出率：{round(progress_bar_1.value*100,2)}%'
            before_run_gauge=progress_bar_1.value
            page.update()

        progress_bar_1.value=1.0
        progress_bar_text.value = f'画像検出率：100%'
        Progress_Ring.visible = False
        page.update()

        # 画像差異終了のポップアップ表示
        show_popup(page)
        print("画像差異終了")
        print("fullpass_AB:",fullpass_AB)
        return fullpass_AB








# 縦横比選択欄の表示切替
def ASPECT(event,key1,key2,key3):#（イベント、ボタンのキー、表示する画面のキー、表示する画像リスト、表示の切り替えをするキー、スクロールに反応するキー、保存する場所（1＝画像A、２＝画像B））
  # 縦横比選択
    if event == key1:
        if values[key1] == '指定比率': #指定比率を選んだら欄が非表示から表示に変わる
            aspect_visible = True
        else:
            aspect_visible = False
        window[key3].update(aspect_visible)




 
def triming(imgA,imgB,x,y,alpha,beta,i,fullpath_list,fullpath_list_move):#（画像Aパス（CV2）、画像Bパス（CV2）、動かす量（ｘ軸）、動かす量（ｙ軸）、画像Ａの重み、画像Ｂの重み、保存するファイルの数字、画像リスト）

    x=0-x
    y=0-y
    print("SHAPE1")
 
    print(imgA.shape)
    print(imgB.shape)

    # 画像が白黒で.shapeで縦横のサイズしか得られない場合はカラー(RGB)に直す
    if len(imgA.shape)==2:
        imgA = cv2.cvtColor(imgA,cv2.COLOR_GRAY2RGB)
    if len(imgB.shape)==2:
        imgB = cv2.cvtColor(imgB,cv2.COLOR_GRAY2RGB)
    if imgA.shape[2]==4:
        imgA = cv2.cvtColor(imgA,cv2.COLOR_RGBA2RGB)
    if imgB.shape[2]==4:
        imgB = cv2.cvtColor(imgB,cv2.COLOR_RGBA2RGB)
    
    print("SHAPE")
 
    print(imgA.shape)
    print(imgB.shape)

    i_AB=str(i)
    file_pass=PDF_file_AB+"/AB_"+i_AB+".png"
    file_pass_move=PDF_file_AB+"/AB_move_"+i_AB+".png"

    #imgBの白色部分以外を赤色に変更
    # 指定色
    target_color = (255, 255, 255)
    # 変更後の色
    change_color = (255, 255, 255)
    # 色の変更
    imgB_red  = np.where(imgB == target_color, change_color, (0, 0, 255))
    imgB_red  = imgB_red .astype(np.uint8)
    imgB  = imgB .astype(np.uint8)


    # カラー画像のときは、BGRからRGBへ変換する
    
    if imgB_red.shape[2] == 3:
         imgB_red = cv2.cvtColor(imgB_red , cv2.COLOR_BGR2RGB)
    elif imgB_red.shape[2] == 4:  # 透過
         imgB_red = cv2.cvtColor(imgB_red , cv2.COLOR_BGRA2RGBA)
    
    if imgB.shape[2] == 3:
         imgB = cv2.cvtColor(imgB, cv2.COLOR_BGR2RGB)
    elif imgB.shape[2] == 4:  # 透過
         imgB = cv2.cvtColor(imgB, cv2.COLOR_BGRA2RGBA)

       # NumPyからPillowへ変換
    pil_imageB  = PILImage.fromarray(imgB)
    pil_imageB_red  = PILImage.fromarray(imgB_red)

    

    lower,right,cA=(imgA.shape)



    # imgBを指定の範囲で切り取り、範囲外は０（黒色）になる
    im_crop  = pil_imageB.crop((x, y, right+x,  lower+y))
    im_crop_red  = pil_imageB_red.crop((x, y, right+x,  lower+y))
    
    #im_crop.save('トリミング結果.png', quality=95)

    new_image = np.array(im_crop_red, dtype=np.uint8)
    if new_image.ndim == 2:  # モノクロ
        pass
    elif new_image.shape[2] == 3:  # カラー
        new_image = new_image[:, :, ::-1]
    elif new_image.shape[2] == 4:  # 透過
        new_image = new_image[:, :, [2, 1, 0, 3]]
    
    imgpaste_B =  new_image
    imgpaste_B = imgpaste_B.astype(np.uint8)


   
    result=cv2.addWeighted(imgA, alpha, imgpaste_B, beta, 0.0)

    if file_pass in fullpath_list:
        pass
    else:
        fullpath_list.insert(i, file_pass)
    
    if file_pass_move in fullpath_list_move:
        pass
    else:
        fullpath_list_move.insert(i, file_pass_move)


    gazou_data=im_crop



    return imgpaste_B,result,file_pass,gazou_data,file_pass_move
    #imgpaste_B : result,file_pass,gazou_data,file_pass_move





