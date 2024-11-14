# 画像の特徴量を抽出してデータベースに保存する
import flet as ft
from flet import AppBar, ElevatedButton, Page, Text, View, Video, WebView, ProgressBar,Checkbox,Row,Column,icons
import time
import cv2
import sqlite3
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog
import heapq
import zlib
from pdf2image import convert_from_path
from PIL import Image

#インストールしたPopplerのパスを環境変数「PATH」へ追記する。
#OS自体に設定してあれば以下の2行は不要
path = os.getcwd() #exe実行ディレクトリpathを取得するのが重要
TESSERACT_PATH = path + '/poppler-23.10.0/Library/bin' #今回はexeと同じディレクトリに配置させる前提とする
os.environ["PATH"] += os.pathsep + TESSERACT_PATH

path = os.getcwd()

# 画像から特徴量を抽出する
def features_AKAZE(image_path):
    image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    akaze = cv2.AKAZE_create()
    keypoints, descriptors = akaze.detectAndCompute(gray, None)
    
    # 画像ファイルのベース名を取得（拡張子を除く）
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    # 「_」で区切られたファイル名の部分を取得
    subfolder_name = base_name.split('_')[0]
    
    # 「計算済み画像」フォルダ内にサブフォルダのパスを生成
    output_subfolder = os.path.join("類似画像検索アプリ/計算済み画像", subfolder_name)
    if not os.path.exists(output_subfolder):
        os.makedirs(output_subfolder)
    
    # 保存する画像のファイルパスを生成
    output_path = os.path.join(output_subfolder, f"{base_name}.png")
    
    # 画像をエンコードしてファイルに書き込む（日本語パス対応）
    _, encoded_image = cv2.imencode('.png', image)
    with open(output_path, 'wb') as file:
        file.write(encoded_image)
    
    return descriptors

# 特徴量のサイズを揃える
def align_feature_size(feature1, feature2):
    # 特徴量のサイズを揃えるための処理を記述する
    # 例えば、次元削減や特徴量の正規化などが考えられます
    aligned_feature1 = feature1[:min(len(feature1), len(feature2))]
    aligned_feature2 = feature2[:min(len(feature1), len(feature2))]
    return aligned_feature1, aligned_feature2



# 画像の特徴量を抽出してデータベースに保存する（上書き保存&圧縮）
def save_features_to_database_compressed(db_path, image_name, features, overwrite_all=False):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # テーブルが存在するかどうかを確認し、存在しない場合は新しいスキーマで作成
        cursor.execute('''CREATE TABLE IF NOT EXISTS features (
                          id INTEGER PRIMARY KEY,
                          image_name TEXT UNIQUE,
                          feature_vector BLOB,
                          descriptor_size INTEGER,
                          dtype TEXT)''')
        
        # 既存のエントリを確認
        cursor.execute('SELECT image_name FROM features WHERE image_name = ?', (image_name,))
        existing_entry = cursor.fetchone()

        # 既存のエントリがあり、一括上書きがFalseの場合はユーザーに確認
        if existing_entry and not overwrite_all:
            overwrite = input(f"既に同じ名前のデータがあります 「{image_name}」 上書き保存しますか? (y/n): ")
            if overwrite.lower() != 'y':
                print("データは保存しません。前のデータのままです。")
                return

        # 既存のデータを削除
        if existing_entry:
            cursor.execute('DELETE FROM features WHERE image_name = ?', (image_name,))

        # データを圧縮して保存
        compressed_features = zlib.compress(features.tobytes())
        descriptor_size = features.shape[1]
        dtype_str = str(features.dtype)
        cursor.execute('INSERT INTO features (image_name, feature_vector, descriptor_size, dtype) VALUES (?, ?, ?, ?)',
                       (image_name, compressed_features, descriptor_size, dtype_str))

# データベース内のすべての特徴量を取得する
def retrieve_all_features_from_database_compressed(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT image_name, feature_vector , descriptor_size FROM features')
    results = cursor.fetchall()
    conn.close()
    all_features = []
    for result in results:
        image_name = result[0]
        compressed_feature_vector = result[1]
        descriptor_size=result[2]
        feature_vector = np.frombuffer(zlib.decompress(compressed_feature_vector), dtype=np.uint8)
        feature_vector = feature_vector .reshape(-1, descriptor_size)
        all_features.append((image_name, feature_vector))
    return all_features
#この修正では、retrieve_all_features_from_database_compressed 関数がデータベースから圧縮された特徴量を取得し、zlib.decompress を使用して特徴量を展開しています。展開された特徴量は、NumPy 配列として取得され、結果のリストに追加されます。
#このように修正することで、データベースから圧縮された特徴量を取得することができます。


#この関数は、指定された名前の特徴量のみを取得します。もし指定された名前の特徴量が見つからない場合は、None を返します。これにより、データベースから指定された名前の特徴量を取得することができます。
def retrieve_features_by_name_from_database_compressed(db_path, target_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT feature_vector, image_name , descriptor_size FROM features WHERE image_name = ?', (target_name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        compressed_feature_vector, image_name,descriptor_size = result
        feature_vector = np.frombuffer(zlib.decompress(compressed_feature_vector), dtype=np.uint8)
        feature_vector = feature_vector .reshape(-1, descriptor_size)
        return feature_vector
    else:
        return None


def create_database_and_table(db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS comparison_results (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          base_image_name TEXT,
                          compared_image_name TEXT,
                          similarity_score INTEGER)''')
        conn.commit()

#このコードでは、os.path.exists 関数を使用して result_db_path に指定されたパスのファイルが存在するかどうかをチェックしています。ファイルが存在する場合は、既存の比較結果を取得して existing_results_dict に格納します。ファイルが存在しない場合は、このステップをスキップし、すべての画像に対して新たに比較を行います。
#また、新しい比較結果をデータベースに保存する部分でも同様にファイルの存在をチェックしています。これにより、result.db ファイルが存在しない場合は、新しい比較結果の保存もスキップされます。
def compare_with_all_features(new_features, all_features, new_image_name, result_db_path, Previous_data, page, done):
    comparison_results = []
    bf = cv2.BFMatcher()
    existing_results_dict = {}

    pb = ft.ProgressBar(width=400, color="green", bgcolor="#eeeeee", bar_height=10)
    pb.value = 0.0
    pacent=0
    pb_text=ft.Text(value=f"{pacent=}%",color="green",weight=ft.FontWeight.W_100,size=20)
    done.controls.append(pb)
    done.controls.append(pb_text)
    page.update()

    # result.dbが存在するかチェックし、存在しない場合は新しくデータベースとテーブルを作成、存在する場合は既存の比較結果を取得
    if not os.path.exists(result_db_path):
        create_database_and_table(result_db_path)

    # result.dbが存在し、既存の結果を使用する場合は比較結果を取得
    if Previous_data and os.path.exists(result_db_path):
        with sqlite3.connect(result_db_path) as conn:
            cursor = conn.cursor()
            # base_image_name と compared_image_name の両方の組み合わせをチェック
            cursor.execute('''SELECT base_image_name, compared_image_name, similarity_score
                              FROM comparison_results
                              WHERE base_image_name = ? OR compared_image_name = ?''', 
                           (new_image_name, new_image_name))
            existing_results = cursor.fetchall()
            existing_results_dict = {}

            for base_name, compared_name, score in existing_results:
                if base_name == new_image_name:
                    existing_results_dict[compared_name] = score
                else:
                    existing_results_dict[base_name] = score

    total_images = len(all_features)
    i = round(1.0 / total_images, 2)
    
    for index, (image_name, feature_vector) in enumerate(all_features):
        if image_name == new_image_name:  # 同じ名前の場合はスキップ
            continue

        # 既存の結果があり、それを使用する場合
        if Previous_data and image_name in existing_results_dict:
            print(f"{image_name}は前のデータを使用します")
            similarity_score = existing_results_dict[image_name]

            # データベースに保存する前に、同じ組み合わせが存在するか確認
            if os.path.exists(result_db_path):
                with sqlite3.connect(result_db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''SELECT COUNT(*)
                                  FROM comparison_results
                                  WHERE base_image_name = ? AND compared_image_name = ?''',
                               (new_image_name, image_name))
                    count = cursor.fetchone()[0]
    
                    if count == 0:  # 組み合わせが存在しない場合のみ保存
                        cursor.execute('INSERT INTO comparison_results (base_image_name, compared_image_name, similarity_score) VALUES (?, ?, ?)',
                                       (new_image_name, image_name, similarity_score))
                        conn.commit()
        
        else:
            # 新しい比較を行う
            print("新しいデータ")
            print(image_name)
            reference_features = feature_vector
            aligned_new_features, aligned_reference_features = align_feature_size(new_features, reference_features)

            matches = bf.knnMatch(aligned_reference_features, aligned_new_features, k=2)
            good_matches = [m for m, n in matches if m.distance < 0.75 * n.distance]
            similarity_score = len(good_matches)

            # 新しい比較結果をデータベースに保存
            if os.path.exists(result_db_path):
                with sqlite3.connect(result_db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('INSERT INTO comparison_results (base_image_name, compared_image_name, similarity_score) VALUES (?, ?, ?)',
                                   (new_image_name, image_name, similarity_score))
                    conn.commit()
        
        pb.value = pb.value + i
        pb_text.value=f'{round(pb.value*100,2)}%'
        page.update()
        comparison_results.append((image_name, similarity_score))

        # 進捗状況を表示
        progress = ((index + 1) / total_images) * 100
        print(f"Processing... {progress:.2f}% complete", end='\r')

    pb.value = 1.0
    pb_text.value=f'100%'
    page.update()
    print("\nComparison complete.")
    return comparison_results



#save_comparison_results_to_database 関数は、比較結果を comparison_results テーブルに保存します。このテーブルには、比較の基準となる画像の名前 base_image_name、比較された画像の名前 compared_image_name、そして類似度スコア similarity_score が含まれます。テーブルが存在しない場合は新しく作成されます。#
def save_comparison_results_to_database(db_path, comparison_results):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        # 結果を保存するためのテーブルを作成
        cursor.execute('''CREATE TABLE IF NOT EXISTS comparison_results (
                          id INTEGER PRIMARY KEY,
                          base_image_name TEXT,
                          compared_image_name TEXT,
                          similarity_score INTEGER)''')
        # 比較結果をデータベースに挿入
        for base_image_name, compared_image_name, similarity_score in comparison_results:
            cursor.execute('INSERT INTO comparison_results (base_image_name, compared_image_name, similarity_score) VALUES (?, ?, ?)',
                           (base_image_name, compared_image_name, similarity_score))
        conn.commit()


#このコードでは、ユーザーが「6」を選択した場合に、drawings.db データベースに接続し、features テーブルからすべてのエントリの id と image_name を取得して表示します。ユーザーはコマンドプロンプトに表示された番号を入力することで、対応するファイル名のデータを削除することができます。データが正常に削除された場合は、その旨が表示されます。
#delete_feature_by_name 関数は、指定された image_name に対応するデータを features テーブルから削除します。データベースにデータがない場合や、指定された番号のデータが存在しない場合は、適切なメッセージが表示されます。
def delete_feature_by_name(db_path, image_name):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM features WHERE image_name = ?', (image_name,))
        conn.commit()


#このコードでは、ユーザーが「7」を選択した場合に、result.db データベースに接続し、comparison_results テーブルからすべてのエントリの id、base_image_name、compared_image_name、similarity_score を取得して表示します。ユーザーはコマンドプロンプトに表示された番号を入力することで、対応する比較結果のデータを削除することができます。データが正常に削除された場合は、その旨が表示されます。
#delete_comparison_result_by_id 関数は、指定された id に対応するデータを comparison_results テーブルから削除します。データベースにデータがない場合や、入力された番号が無効な場合は、適切なメッセージが表示されます。
def delete_comparison_result_by_id(db_path, result_id):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM comparison_results WHERE id = ?', (result_id,))
        conn.commit()


#このコードでは、ユーザーが「8」を選択した場合にファイルダイアログを使用してPDFファイルを選択し、convert_pdf_to_png 関数を呼び出してPDFをPNGに変換します。変換されたPNGファイルは、カレントディレクトリに作成される「PDF→PNG」フォルダに保存されます。フォルダが存在しない場合は新しく作成されます。
#convert_from_path 関数は、PDFファイルの各ページを画像として読み込み、それらをリストとして返します。その後、各画像をPNG形式で保存します。ファイル名はページ番号に基づいて自動的に生成されます。
#注意：pdf2image ライブラリは内部でPopplerを使用しています。Popplerがシステムにインストールされていない場合は、pdf2image が正常に動作しない可能性があります。Popplerのインストール方法はOSによって異なりますので、必要に応じてインストールしてください。
def convert_pdf_to_png(pdf_path, output_folder):
    # PDFファイルのベース名を取得（拡張子を除く）
    pdf_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    
    images = convert_from_path(pdf_path)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for i, image in enumerate(images):
        # PDFファイル名を含むPNG画像のファイル名を生成
        image_name = f"{pdf_filename}_page_{i + 1}.png"
        image_path = os.path.join(output_folder, image_name)
        image.save(image_path, 'PNG')
        print(f"Saved: {image_path}")


def convert_tif_to_png(tif_path, output_folder):
    # TIFファイルのベース名を取得（拡張子を除く）
    tif_filename = os.path.splitext(os.path.basename(tif_path))[0]
    
    # TIFファイルを読み込む
    tif_image = Image.open(tif_path)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # TIFファイルが複数ページを含む場合、各ページを個別のPNGファイルとして保存
    i = 0
    while True:
        try:
            # PNG画像のファイル名を生成
            image_name = f"{tif_filename}_page_{i + 1}.png"
            image_path = os.path.join(output_folder, image_name)
            tif_image.save(image_path, 'PNG')
            print(f"Saved: {image_path}")
            
            # 次のページに進む
            i += 1
            tif_image.seek(i)
        except EOFError:
            # ページの終わりに達したら終了
            break

