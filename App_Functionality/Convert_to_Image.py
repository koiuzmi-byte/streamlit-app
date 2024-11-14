# 画像の特徴量を抽出してデータベースに保存する

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

def PDF_to_Image(pdf_path, output_folder):
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

def TIF_to_Image(tif_path, output_folder):
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

# 画像から特徴量を抽出する
def extract_features(image_path):
    # ファイルパスに日本語が含まれる場合、適切なエンコーディングを指定する
    image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sift = cv2.SIFT_create()
    keypoints, descriptors = sift.detectAndCompute(gray, None)

    # 画像ファイルのベース名を取得（拡張子を除く）
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    # 「_」で区切られたファイル名の部分を取得
    subfolder_name = base_name.split('_')[0]
    
    # 「計算済み画像」フォルダ内にサブフォルダのパスを生成
    output_subfolder = os.path.join("計算済み画像", subfolder_name)
    if not os.path.exists(output_subfolder):
        os.makedirs(output_subfolder)
    
    # 保存する画像のファイルパスを生成
    output_path = os.path.join(output_subfolder, f"{base_name}.png")
    
    # 画像をエンコードしてファイルに書き込む（日本語パス対応）
    _, encoded_image = cv2.imencode('.png', image)
    with open(output_path, 'wb') as file:
        file.write(encoded_image)
    
    return descriptors

# 画像から特徴量を抽出する
def extract_features_AKAZE(image_path):
    image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    akaze = cv2.AKAZE_create()
    keypoints, descriptors = akaze.detectAndCompute(gray, None)
    
    # 画像ファイルのベース名を取得（拡張子を除く）
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    # 「_」で区切られたファイル名の部分を取得
    subfolder_name = base_name.split('_')[0]
    
    # 「計算済み画像」フォルダ内にサブフォルダのパスを生成
    output_subfolder = os.path.join("計算済み画像", subfolder_name)
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
def compare_with_all_features(new_features, all_features, new_image_name, result_db_path):
    comparison_results = []
    bf = cv2.BFMatcher()
    existing_results_dict = {}
    
    # ユーザーに既存の比較結果を使用するかどうかを尋ねる
    use_existing_results = input("既存の比較結果を使用しますか？ [y/n]: ").lower() == 'y'

    # result.dbが存在するかチェックし、存在しない場合は新しくデータベースとテーブルを作成,存在する場合は既存の比較結果を取得
    if not os.path.exists(result_db_path):
        create_database_and_table(result_db_path)
    # result.dbが存在し、既存の結果を使用する場合は比較結果を取得
    if use_existing_results and os.path.exists(result_db_path):
        with sqlite3.connect(result_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT compared_image_name, similarity_score
                              FROM comparison_results
                              WHERE base_image_name = ?''', (new_image_name,))
            existing_results = cursor.fetchall()
            existing_results_dict = {name: score for name, score in existing_results}
    total_images = len(all_features)
    for index, (image_name, feature_vector) in enumerate(all_features):
        if image_name == new_image_name:  # 同じ名前の場合はスキップ
            continue

        # 既存の結果があり、それを使用する場合
        if use_existing_results and image_name in existing_results_dict:
            print(str(image_name)+"は前のデータを使用します")
            similarity_score = existing_results_dict[image_name]
        else:
            # 新しい比較を行う
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

        comparison_results.append((image_name, similarity_score))

        # 進捗状況を表示
        progress = ((index + 1) / total_images) * 100
        print(f"Processing... {progress:.2f}% complete", end='\r')

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

def main():
    db_path = 'drawings_AKAZE.db'  # データベースのパスを指定
    result_db_path = 'result_AKAZE.db'  # 結果を保存するデータベースのパス
    while True:
        print("\n初期選択画面")
        print("\n1: 画像（png）の特徴量を計算する")
        print("2: 選択した画像の類似度を計算する")
        print("3: アプリを終了")
        print("4: データベース(drawings.db)の中身を開く")
        print("5: データベース(result.db)の中身を開く")
        print("6: データベース(drawings.db)の特定のデータを削除")
        print("7: データベース(result.db)の特定のデータを削除")
        print("8: PDFをPNGに変換する（「PDF→PNG」フォルダに保存）")
        print("9: TIFをPNGに変換する（「TIF→PNG」フォルダに保存）")
        print("10: PDF→PNG内の特徴量を計算")
        choice = input("\n選択してください (1/2/3/4/5/6/7/8/9/10): ")
        if choice == "1":
            root = tk.Tk()
            root.withdraw()
            file_paths = filedialog.askopenfilenames(title="Select image", filetypes=(("Image files", "*.png;*.jpg"), ("All files", "*.*")))
            # 全てのファイルを上書き保存するかユーザーに尋ねる
            overwrite_all = input("全てのファイルを上書き保存しますか？ [y/n]: ").lower() == 'y'
            for file_path in file_paths:
                new_image_name = os.path.splitext(os.path.basename(file_path))[0]
                print(new_image_name)
                new_features = extract_features_AKAZE(file_path)
                save_features_to_database_compressed(db_path, new_image_name, new_features,overwrite_all)
                print(str(new_image_name)+"が終了")
            print("データ入力が終了しました")
                
        elif choice == "2":
            root = tk.Tk()
            root.withdraw()
            file_paths = filedialog.askopenfilenames(
                title="Select image",
                filetypes=(("Image files", "*.png;*.jpg"), ("All files", "*.*"))
            )
            start = time.time()  # 現在時刻（処理開始前）を取得
            for file_path in file_paths:
                new_image_name = os.path.splitext(os.path.basename(file_path))[0]
                new_features = retrieve_features_by_name_from_database_compressed(db_path, new_image_name)
                if new_features is not None:
                    all_features = retrieve_all_features_from_database_compressed(db_path)
                    comparison_results = compare_with_all_features(new_features, all_features, new_image_name, result_db_path)
                    # 結果を類似度が高い順にソート
                    comparison_results.sort(key=lambda x: x[1], reverse=True)
                    print("")
                    print(f"画像の類似度が高い順に並べます")
                    # 結果を表示する
                    if not comparison_results:
                        print("データがありません")
                    else:
                        # 類似度スコアが10以下の場合はすべての結果を表示
                        if len(comparison_results) <= 10:
                            for i, (image_name, similarity_score) in enumerate(comparison_results):
                                print(f"{i + 1}: 「{new_image_name}」と「{image_name}」の画像の類似度: {similarity_score}")
                        # 類似度スコアが10以上の場合は上位10個の結果のみを表示
                        else:
                            for i in range(10):
                                image_name, similarity_score = comparison_results[i]
                                print(f"{i + 1}: 「{new_image_name}」と「{image_name}」の画像の類似度: {similarity_score}")
                else:
                    print(f"画像「{new_image_name}」の特徴量がデータベースに見つかりませんでした。")
            end = time.time()  # 現在時刻（処理完了後）を取得
            time_diff = end - start  # 処理完了後の時刻から処理開始前の時刻を減算する
            print("実行時間")
            print(time_diff)  # 処理にかかった時間データを使用


        elif choice == "3":
            break
        
        elif choice == "4":
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT image_name, descriptor_size, dtype FROM features")
                rows = cursor.fetchall()
                print("\nデータベースの中身:")
                for row in rows:
                    print(f"画像名: {row[0]}, ディスクリプタサイズ: {row[1]}, データ型: {row[2]}")

        elif choice == "5":
            with sqlite3.connect(result_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT base_image_name, compared_image_name, similarity_score FROM comparison_results")
                rows = cursor.fetchall()
                print("\n「result.db」の中身:")
                for row in rows:
                    print(f"基準画像名: {row[0]}, 比較画像名: {row[1]}, 類似度スコア: {row[2]}")
        
        elif choice == "6":
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, image_name FROM features")
                rows = cursor.fetchall()
                if rows:
                    print("\nデータベース内のデータ:")
                    for row in rows:
                        print(f"番号: {row[0]}, ファイル名: {row[1]}")
                    selected_id = input("削除するデータの番号を入力してください: ")
                    selected_image_name = next((row[1] for row in rows if str(row[0]) == selected_id), None)
                    if selected_image_name:
                        delete_feature_by_name(db_path, selected_image_name)
                        print(f"「{selected_image_name}」のデータを削除しました。")
                    else:
                        print("指定された番号のデータは存在しません。")
                else:
                    print("データベースにデータがありません。")


        elif choice == "7":
            with sqlite3.connect(result_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, base_image_name FROM comparison_results GROUP BY base_image_name")
                rows = cursor.fetchall()
                if rows:
                    print("\n「result.db」の基準画像名:")
                    for row in rows:
                        print(f"番号: {row[0]}, 基準画像名: {row[1]}")
                    selected_id = input("削除する基準画像名の番号を入力してください: ")
                    try:
                        selected_id = int(selected_id)
                        # 選択された番号に対応する基準画像名を取得
                        selected_base_image_name = next((row[1] for row in rows if row[0] == selected_id), None)
                        if selected_base_image_name:
                            # 基準画像名に関連する全ての比較結果を削除
                            cursor.execute('DELETE FROM comparison_results WHERE base_image_name = ?', (selected_base_image_name,))
                            conn.commit()
                            print(f"基準画像名「{selected_base_image_name}」に関連する比較結果を削除しました。")
                        else:
                            print("選択された番号に対応する基準画像名が見つかりません。")
                    except ValueError:
                        print("無効な番号です。数字を入力してください。")
                    except sqlite3.IntegrityError as e:
                        print(f"エラーが発生しました: {e}")
                else:
                    print("「result.db」に比較結果のデータがありません。")

        elif choice == "8":
            root = tk.Tk()
            root.withdraw()
            pdf_paths = filedialog.askopenfilenames(
                title="Select PDF files",
                filetypes=(("PDF files", "*.pdf"), ("All files", "*.*"))
            )
            if pdf_paths:
                output_folder = os.path.join(os.getcwd(), "PDF→PNG")
                for pdf_path in pdf_paths:
                    convert_pdf_to_png(pdf_path, output_folder)

            else:
                print("PDFファイルが選択されませんでした。")
        
        elif choice == "9":
            root = tk.Tk()
            root.withdraw()
            tif_paths = filedialog.askopenfilenames(
                title="Select TIF files",
                filetypes=(("TIF files", "*.tif;*.tiff"), ("All files", "*.*"))
            )
            if tif_paths:
                output_folder = os.path.join(os.getcwd(), "TIF→PNG")
                for tif_path in tif_paths:
                    convert_tif_to_png(tif_path, output_folder)
            else:
                print("TIFファイルが選択されませんでした。")

        elif choice == "10":
            pdf_to_png_folder = os.path.join(os.getcwd(), "PDF→PNG")
            overwrite_all = input("全てのファイルを上書き保存しますか？ [y/n]: ").lower() == 'y'
            if os.path.exists(pdf_to_png_folder) and os.listdir(pdf_to_png_folder):
                image_files = [os.path.join(pdf_to_png_folder, f) for f in os.listdir(pdf_to_png_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                for image_path in image_files:
                    image_name = os.path.splitext(os.path.basename(image_path))[0]
                    features = extract_features_AKAZE(image_path)
                    if features is not None:
                        save_features_to_database_compressed(db_path, image_name, features,overwrite_all)
                        print(f"特徴量を計算し、データベースに保存しました: {image_name}")
                    else:
                        print(f"特徴量を計算できませんでした: {image_name}")
             # ユーザーに「PDF→PNG」フォルダの中身を空にするか確認
            empty_folder = input("PDF→PNGフォルダを空にしますか？ [y/n]: ").lower() == 'y'
            if empty_folder:
               # 「PDF→PNG」フォルダ内のファイルを削除して空にする
               for file_path in image_files:
                   os.remove(file_path)
               print("「PDF→PNG」フォルダの中身を空にしました。")
            else:
                print("「PDF→PNG」フォルダが存在しないか空です。")
               # 「PDF→PNG」フォルダ内のファイルを削除して空にする


        else :
            print("そのコマンドはありません。最初に戻ります")

if __name__ == "__main__":
    main()


 



