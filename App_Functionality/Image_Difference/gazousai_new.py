import  os
import numpy as np
from PIL import Image
import sys
import cv2
import time




# 処理に使う画像を保管する場所
path=os.getcwd()

histogram_dir = path+'/画像差異アプリ/画像処理用/ヒストグラム処理'
binarization_dir = path+'/画像差異アプリ/画像処理用/2値化処理'
expansion_dir = path+'/画像差異アプリ/画像処理用/膨張処理'
move_dir= path+'/画像差異アプリ/画像処理用/自動位置調整'

image_difference_dir = path+'/画像差異アプリ/画像差異検出/画像Aの差異(青色)'
result_dir = path+'/画像差異アプリ/画像差異検出/検出結果(通常)'
mask_dir=path+'/画像差異アプリ/画像差異検出/マスク画像'
gray_difference_dir= path+'/画像差異アプリ/画像差異検出/検出結果(灰色バージョン)'


#Pillowで画像ファイルを開き、OpenCV(NumPyのndarray)に変換する関数
def pil2cv(image):
    ''' PIL型 -> OpenCV型 '''
    new_image=Image.open(image)
    new_image = new_image.convert('L')
    new_image = np.array(new_image)
    
    if new_image.ndim == 2:  # モノクロ
        new_image = new_image
    elif new_image.shape[2] == 3:  # カラー
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
    elif new_image.shape[2] == 4:  # 透過
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
    return new_image

#OpenCV(NumPyのndarray)からPillowに変換する関数
def cv2pil(image):
    ''' OpenCV型 -> PIL型 '''
    new_image = image.copy()
    if new_image.ndim == 2:  # モノクロ
        pass
    elif new_image.shape[2] == 3:  # カラー
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
    elif new_image.shape[2] == 4:  # 透過
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGRA2RGBA)
    new_image = Image.fromarray(new_image)
    return new_image

  ##保存する先のファイルを設定する  
def getOutputName(title,i,number,color):
    if i=="1":
      if not os.path.exists(histogram_dir):
         # ディレクトリが存在しない場合、ディレクトリを作成する
         os.makedirs(histogram_dir)
      title=histogram_dir+"/"+ title + "_histogram.png"

    if i=="2":
      if not os.path.exists(binarization_dir):
         # ディレクトリが存在しない場合、ディレクトリを作成する
         os.makedirs(binarization_dir)
      title=binarization_dir+"/"+ title + "_binarization.png"
    
    if i=="3":
      if not os.path.exists(expansion_dir):
         # ディレクトリが存在しない場合、ディレクトリを作成する
         os.makedirs(expansion_dir)
      title=expansion_dir+"/"+ title + "_expansion.png"

    if i=="5":
      if not os.path.exists(mask_dir):
         # ディレクトリが存在しない場合、ディレクトリを作成する
         os.makedirs(mask_dir)
      if color=="red":
        title=mask_dir+"/mask_red"+"_{:02d}".format(number + 1) + ".png"
      if color=="blue":
        title=mask_dir+"/mask_blue"+"_{:02d}".format(number + 1) + ".png"

    if i=="6":
      if not os.path.exists(image_difference_dir):
         # ディレクトリが存在しない場合、ディレクトリを作成する
         os.makedirs(image_difference_dir)
      if not os.path.exists(result_dir):
         # ディレクトリが存在しない場合、ディレクトリを作成する
         os.makedirs(result_dir)

      if color=="red":
        title=image_difference_dir+"/gazousai_red"+"_{:02d}".format(number + 1) + ".png"
      if color=="blue":
        title=result_dir+"/gazousai_blue"+"_{:02d}".format(number + 1) + ".png"

    if i=="7":
      if not os.path.exists(gray_difference_dir):
         # ディレクトリが存在しない場合、ディレクトリを作成する
         os.makedirs(gray_difference_dir)
      title=gray_difference_dir+"/gazousai_gray"+"_{:02d}".format(number + 1)+"_"+str(int(time.time())) + ".png"

    if i=="8":
      if not os.path.exists(move_dir):
         # ディレクトリが存在しない場合、ディレクトリを作成する
         os.makedirs(move_dir)
      title=move_dir+"/"+ title + "_gazoumove.png"


    return title

#画像の色を変えて重ねる
def color_convert(im1_u8,image,diff,i,name,number,mode):  #im1_u8:画像、image：重ねる対象の画像、diff:マスク作成に使う差異データ,iで色を決める（0:赤、1:緑、2:青）
 r_bool = diff[:,:,0]
 g_bool = diff[:,:,1]
 b_bool = diff[:,:,2]
 if i==2:
    mask_title=getOutputName(name,"5",number,"red")
    gazousai_title=getOutputName(name,"6",number,"red")


 if i==0:
    mask_title=getOutputName(name,"5",number,"blue")
    gazousai_title=getOutputName(name,"6",number,"blue")
 if i==1:
    mask_title=getOutputName(name,"5",number,"blue")
    gazousai_title=getOutputName(name,"6",number,"blue")

    


 mask_bool = r_bool | g_bool | b_bool
 mask_u8 = mask_bool.astype(np.uint8) * 255  # 差異部分が白色の白黒画像を作る

 # PIL画像に変換
 mask_img = Image.fromarray(mask_u8)
 mask_img.save(mask_title)

 # 全ての画素の色をiを(0,255,0)とした配列作成
 green_u8 = np.zeros(im1_u8.shape, np.uint8)
 green_u8[:,:,i] = 255
 #if i==1:
 #  green_u8[:,:,2] = 255
 
 
 # １つ目の画像に色を混ぜる
 blend_u8 = im1_u8 * 0.3 + green_u8 * 0.7

 # 画像に変換
 blend_img = Image.fromarray(blend_u8.astype(np.uint8))
 # １つ目の画像に貼り付け
 diff_img = image.copy()
 diff_img.paste(im=blend_img, mask=mask_img)
 # 画像表示
 diff_img.save(gazousai_title)

 return  diff_img,gazousai_title,mask_title





#ヒストグラムの度数が増加している範囲を調査し、その境界値を slim に設定する関数
def getStdThrsh(img, Blocksize):  #img:白黒画像のデータ(ndarray形式)、Blocksize:整数（64）
    stds = []
    for y in range( 0, img.shape[0], Blocksize ):
        for x in range( 0, img.shape[1], Blocksize ):
            pimg = img[y:y+Blocksize, x:x+Blocksize] #xとyは画像内の座標を表し、Blocksize は切り取る領域のサイズを指定します。
            std = np.std( pimg )  #NumPyのstd関数で領域内の要素の標準偏差を計算する
            stds.append(std)  #stdsリストに計算結果を格納する

    hist = np.histogram( stds, bins=64 )  #NumPyのnp.histogram関数でヒストグラムを作る。1:stds 配列のデータをビン（階級）に分割します。ビンの数は 64 で指定。各ビンに含まれるデータポイントの数をカウントします。
    peaki = np.argmax(hist[0])   #与えられた配列 hist の最大要素のインデックスを取得する処理。これでヒストグラムの中で最も頻繁に出現する値（度数が最大の値）のインデックスを取得できます。

    #plt.hist( stds, bins=64 )
    #plt.show()

    slim = 6.0
    for n in range(peaki,len(hist[0])-1):  #peaki から hist[0] の最後の要素の1つ前までの範囲でループを実行します。
        if hist[0][n] < hist[0][n+1]:  #現在の要素と次の要素を比較して、現在の要素の度数が次の要素の度数よりも小さい場合に条件を満たします。
            slim = hist[1][n+1]   #条件を満たす最初の要素の境界値を slim に代入します。
            break 

    if slim > 6.0:
        slim = 6.0
    
    return slim

#ヒストグラム平坦化処理などで黒い点などのノイズを消す関数
#参考文献：テキスト画像の文字の背景を白飛びさせて読みやすくする(https://qiita.com/picpie/items/050ed903eda93fffed10)
def sharpenImg(imgfile,filename,mode):

    Testimagefile = imgfile   #ファイルのパス　例：C:\Users\KOIZUMI\Desktop\画像差異４/画像AB/AB_move_0.png
    name = filename  #ファイルの名前だけを抽出（.pngなどの拡張子もない）例：AB_move_0

    Blocksize = 64

    print("ファイル名: "+str(Testimagefile))

    # Pillowで画像ファイルを開き、OpenCV(NumPyのndarray)に変換
    pil_img = pil2cv(Testimagefile)
    # カラー画像から白黒画像へ変換する（あとの画像処理ではカラーよりも白黒の方が都合がいい）
    print("pil_img.axis: "+str(pil_img.shape))
    if pil_img.ndim == 3:  # カラー
      img_gray = cv2.cvtColor(pil_img, cv2.COLOR_BGR2GRAY)
    if pil_img.ndim == 2:  # 白黒
      img_gray = pil_img

    print("img_gray .axis: "+str(img_gray.shape))
    print(type(img_gray))
    slim = getStdThrsh(img_gray, Blocksize)  # ヒストグラムの度数が増加している範囲を調査し、その境界値を求める
    yimgs=[]
    for y in range( 0, img_gray.shape[0], Blocksize ):
        s = ""
        ximgs=[]
        for x in range( 0, img_gray.shape[1], Blocksize ):
            pimg = img_gray[y:y+Blocksize, x:x+Blocksize]
            std = np.std( pimg )  #NumPyのstd関数で領域内の要素の標準偏差を計算する

            if std < slim: #標準偏差が境界値よりも小さい場合はpimgと同じサイズの配列ximgを生成し、そのすべての要素を255(白色)で初期化する処理です。
                s = s + "B"
                ximg=np.zeros(pimg.shape) + 255
            else:  #この処理は、画像の濃淡を調整するために使用されます。lut 配列には、入力画像の画素値に対応する変換後の値が設定されており、これにより画像のコントラストや明るさを調整できます。
                s = s + "_" 
                lut = np.zeros(256)  #長さが 256 のゼロで初期化された配列 lut を生成しています。
                white = int(np.median(pimg))  #部分画像 pimg の画素値の中央値を計算し、整数に変換して white に代入しています。
                black = int(white / 2)  #
                cnt = int(white - black)  #
                for n in range(cnt):
                    lut[black+n]=( int(256 * n / cnt) )  #lut 配列の black + n 番目の要素に値を設定しています
                for n in range(white,256):
                    lut[n]=(255)  #
                ximg=cv2.LUT(pimg,lut)  #部分画像 pimg に対して、lut 配列を用いてトーンカーブの調整を行い、新しい画像 ximg を生成しています。
            ximgs.append(ximg)
        print( "{:4d} {:s}".format( y, s ) )
        yimgs.append( cv2.hconcat( ximgs ) )  #部分画像のリスト ximgs を横方向に連結して、新しい画像リスト yimgs に追加する処理です。

    outimage = cv2.vconcat(yimgs)  #画像処理後の画像をoutimage （ndarray形式）に保存

    #保存モードの時のみ処理画像を保存
    if mode=="on":
        pil_image=cv2pil(image)

        title=getOutputName(name,"1",0,"")
        gray = pil_image.convert("I")
        if pil_image.mode == 'F':
           pil_image = pil_image.convert('RGB')
        print("変換後のデータ")
        print(title)
        result=pil_image.save(title)
        print(result)

    print("ヒストグラム処理完了")
    return outimage #画像処理後の画像をoutimage （ndarray形式)


def Improved_image(img, name, mode):
    # 画像をRGBに変換
    img = Image.fromarray(img).convert('RGB')
    size = img.size  # 画像のサイズを保存
    img_array = np.array(img)  # NumPy配列に変換
    
    border = 170  # 閾値

    # 閾値よりも明るい場所は全て白色にする
    img_white = np.where(img_array > border, 255, img_array)
    
    # 閾値よりも低い場所は全て黒色にする
    img_black = np.where(img_white < border, 0, img_white)

    # 結果をPIL画像に変換
    img_black_pil = Image.fromarray(img_black.astype('uint8'))

    # 保存モードのときのみ処理画像を保存する
    if mode == "ON":
        title = getOutputName(name, "2", 0, "")
        img_black_pil.save(title)

    print("2値処理終了")
    return img_black_pil  # 画像処理後の画像を返す


#画像の線を太くする関数
def henkan(pil_image,i,name,mode):

 img=np.array(pil_image)#Pillow -> NumPyへ変換

 if img is not None: #画像ファイルで正常に読み込めた場合に処理する
            kernel =np.ones((i,i),np.uint8) #膨張するパラメータ設定
            erosion=cv2.erode(img,kernel,iterations=1) #膨張実行

            if mode=="ON":
                title=getOutputName(name,"3",0,"")
                pil_image = Image.fromarray(erosion)
                pil_image.save(title)

 return erosion

 #黒色部分を灰色にする関数
import numpy as np
from PIL import Image

def gray_Improved(img, number, mode):
    size = img.size  # 画像のサイズを保存
    img_array = np.array(img)  # NumPy配列に変換

    border = 10  # 閾値

    # 条件に基づいてピクセルの色を変更
    mask = (img_array[:, :, 0] < border) & (img_array[:, :, 1] < border) & (img_array[:, :, 2] < border)
    img_array[mask] = [125, 125, 125]  # 条件を満たすピクセルを指定の色に変更

    # NumPy配列からPIL画像に変換
    img_new = Image.fromarray(img_array.astype('uint8'))

    # 保存モードのときのみ処理画像を保存する
    title = getOutputName("", "7", number, "")
    if mode == "ON":
        img_new.save(title)

    print("膨張処理完了")
    return img_new, title


 #画像の位置を自動で調整
def gazou_move(file1,file2,name,mode):

 #変形させる画像
 float_img = np.array(file1)
 #変形元画像
 ref_img = np.array(file2)

 # 画像の大きさを取得
 height, width = ref_img.shape[:2]
 print("変形元のwidth: " + str(width))
 print("変形元のwheight: " + str(height))
 print("name: " + str(name))

 akaze = cv2.AKAZE_create()  #OpenCV（において、AKAZE（Accelerated KAZE）特徴量検出器を生成するメソッド。
 # 両画像に対してキーポイントと記述子を計算
 # kp=keypoints(特徴点抽出), des=descriptors(特徴点描画)
 # detectAndCompute() => (kp:特徴点の一覧, des:各特徴点の特徴量記述子)  のタプルになります。
 float_kp, float_des = akaze.detectAndCompute(float_img, None)
 ref_kp, ref_des = akaze.detectAndCompute(ref_img, None)
 print("float_des: " + str(float_des))
 print("ref_des: " + str(ref_des))

 #kpは検出された特徴点（キーポイント）のリストで、desはそれらの特徴点の記述子を表すNumpy配列
 if float_des is not None and ref_des is not None:
  pass
 else:
  warped_image =float_img 
   # NumPyからPillowへ変換
  pil_image = Image.fromarray(warped_image)
  if mode =="ON":
    title=getOutputName(name,"8",0,"")
    # Pillowで画像ファイルへ保存
    pil_image.save(title)
  print("自動位置調整完了")
  return pil_image

 #  デフォルトパラメータを使用したBFMatcherオブジェクトを作成
 bf = cv2.BFMatcher()
 # 記述子をマッチング
 


 matches = bf.knnMatch(float_des, ref_des, k=2)

 good_matches = [] 
 ratio = 0.75  # データをマッチング精度を決める。大きいほどマッチングする特徴点が増える
 #DMatch. distance - 記述子間の距離。低いほど良いです。
 for m, n in matches:
    if m.distance < ratio * n.distance:
        good_matches.append([m])

 # 適切なキーポイントを選択
 #・queryIdx：クエリ記述子（検索データ）の記述子のインデックス
 ref_matched_kpts = np.float32(
    [float_kp[m[0].queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
 sensed_matched_kpts = np.float32(
    [ref_kp[m[0].trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)


 # ホモグラフィを計算
 H, status = cv2.findHomography(
    ref_matched_kpts, sensed_matched_kpts, cv2.RANSAC, 5.0)

 # 画像を変換
 warped_image = cv2.warpPerspective(
    float_img, H, (width,height))

 # NumPyからPillowへ変換
 pil_image = Image.fromarray(warped_image)
 if mode =="ON":
   title=getOutputName(name,"8",0,"")
   # Pillowで画像ファイルへ保存
   pil_image.save(title)
 print("自動位置調整完了")
 return pil_image






def gazousai(page,progress_bar_1,progress_bar_text,run_gauge,file1,file2,i1,i2,move_mode,save_mode,number):   #（file1：指定画像Aのパス、file2：指定画像Bのパス,i1;,i2;,mode,number:何番目の画像か)
 dir = path
 filename1=os.path.splitext(os.path.basename(file1))[0]  #画像パスからファイル名を取り出す（画像保存する際の名前につかう）
 filename2=os.path.splitext(os.path.basename(file2))[0]
 print("filename1:"+str(filename1))

 i1=int(i1)  #画像Aの膨張処理のサイズを決める（数字が大きくなるほど画像差異に使う画像の線が太くなる）
 i2=int(i2)  #画像Bの膨張処理のサイズを決める
  
 image_histogram_A=sharpenImg((file1),filename1,save_mode)  #ヒストグラム平坦化を実行(image_histogramはndarray形式の処理後の画像)
 image_binarization_A=Improved_image(image_histogram_A,filename1,save_mode)  #image_binarization：pillow形式の画像処理後のデータ
 #image_binarization_A= Image.fromarray(image_histogram_A)
 progress_bar_1.value=round((progress_bar_1.value+1/(int(run_gauge)*6)),2)
 progress_bar_text.value = f'画像検出率：{round(progress_bar_1.value*100,2)}%'
 page.update()

 #画像Bでも同様のことを行う
 image_histogram_B=sharpenImg(str(file2),filename2,save_mode)  #ヒストグラム平坦化を実行(image_histogramはndarray形式の処理後の画像)
 image_binarization_B=Improved_image(image_histogram_B,filename2,save_mode)  #image_binarization：pillow形式の画像処理後のデータ
 #image_binarization_B= Image.fromarray(image_histogram_B)

 if move_mode=="ON":
   image_binarization_B=gazou_move(image_binarization_B,image_binarization_A,filename2,save_mode)  #自動画像位置調整を実行（移動させる対象画像B、位置を合わせる対象）

 progress_bar_1.value=round((progress_bar_1.value+1/(int(run_gauge)*6)),2)
 progress_bar_text.value = f'画像検出率：{round(progress_bar_1.value*100,2)}%'
 page.update()

 #画像の線を太くする。iの数字が大きくなるほど太くなる。
 image_expansion_A=henkan(image_binarization_A,i1,filename1,save_mode)  #image_expansion_A：NumPy形式の画像処理後のデータ
 image_expansion_B=henkan(image_binarization_B,i2,filename2,save_mode)  #image_expansion_B：NumPy形式の画像処理後のデータ

 progress_bar_1.value=round((progress_bar_1.value+1/(int(run_gauge)*6)),2)
 progress_bar_text.value = f'画像検出率：{round(progress_bar_1.value*100,2)}%'
 page.update()

 # 画像の読み込み
 image1 = image_binarization_A  #上の画像処理でノイズを取り除いた画像A
 image2 = image_binarization_B  #上の画像処理でノイズを取り除いた画像B
 image3 = Image.fromarray(image_expansion_A)  #膨張処理で線を太くした画像A
 image4 = Image.fromarray(image_expansion_B)  #膨張処理で線を太くした画像b

 # RGB画像に変換
 image1 = image1.convert("RGB")
 image2 = image2.convert("RGB")
 image3 = image3.convert("RGB")
 image4 = image4.convert("RGB")

 # NumPy配列へ変換
 im1_u8 = np.array(image1)
 im2_u8 = np.array(image2)
 im3_u8 = np.array(image3)
 im4_u8 = np.array(image4)

 # サイズや色数が違うならエラー
 if im1_u8.shape != im2_u8.shape:
    print("サイズが違います")
        # それぞれの画像の高さと幅を取得
    height1, width1, _ = im1_u8.shape
    height2, width2, _ = im2_u8.shape

    # リサイズ後のサイズを決定（大きい方のサイズに合わせる）
    new_height = max(height1, height2)
    new_width = max(width1, width2)

    # 画像1をリサイズ
    image1 = image1.resize((new_width, new_height),  Image.Resampling.LANCZOS)
    im1_u8 = np.array(image1)

    # 画像2をリサイズ
    image2 = image2.resize((new_width, new_height),  Image.Resampling.LANCZOS)
    im2_u8 = np.array(image2)

    # 必要に応じて、他の画像も同様にリサイズする
    image3 = image3.resize((new_width, new_height), Image.Resampling.LANCZOS)
    im3_u8 = np.array(image3)

    image4 = image4.resize((new_width, new_height), Image.Resampling.LANCZOS)
    im4_u8 = np.array(image4)

 # 負の値も扱えるようにnp.int16に変換
 im1_i16 = im1_u8.astype(np.int16)
 im2_i16 = im2_u8.astype(np.int16)
 im3_i16 = im3_u8.astype(np.int16)
 im4_i16 = im4_u8.astype(np.int16)

 # 差分配列作成（マスク画像に使う）
 diff_i16A = im1_i16 - im4_i16
 diff_i16B = im3_i16 - im2_i16

 progress_bar_1.value=round((progress_bar_1.value+1/(int(run_gauge)*6)),2)
 progress_bar_text.value = f'画像検出率：{round(progress_bar_1.value*100,2)}%'
 page.update()

 '''ここから作成する画像によって異なる処理'''

 # 差分の絶対値が0以外の輝度値を255に変換
 diff_bool = diff_i16A < 0
 diff_bool2 = diff_i16B > 0 

 image_A,filename_A,maskname_A=color_convert(im1_u8,image1,diff_bool,1,filename1,number,save_mode)  #im1_u8：画像Aのデータ(ndarray)、image1:重ねる対象画像(pillow),diff_bool:差異画像、線の色を設定、ファイル名（いらない？）、画像の順番、保存モードの設定
  #image_Aはpillow形式
 image_B,ffilename_B,maskname_B=color_convert(im2_u8,image_A,diff_bool2,0,filename2,number,save_mode)

 progress_bar_1.value=round((progress_bar_1.value+1/(int(run_gauge)*6)),2)
 progress_bar_text.value = f'画像検出率：{round(progress_bar_1.value*100,2)}%'
 page.update()

 kekka,gray_image= gray_Improved(image_B,number,save_mode)
 progress_bar_1.value=round((progress_bar_1.value+1/(int(run_gauge)*6)),2)
 progress_bar_text.value = f'画像検出率：{round(progress_bar_1.value*100,2)}%'
 page.update()
 
 print(str(number)+"番目の画像差異検出完了")
 #image_A = np.asarray(image_A)
 #image_A  = cv2.cvtColor(image_A , cv2.COLOR_RGB2BGR)
 #image_B = np.asarray(image_B)
 #image_B  = cv2.cvtColor(image_B , cv2.COLOR_RGB2BGR)

 return gray_image
