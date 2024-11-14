# このプログラムは特定のファイルのPDFをPNGに全変換する関数です。
import glob
import os
from pathlib import Path
from pdf2image import convert_from_path
import shutil

#インストールしたPopplerのパスを環境変数「PATH」へ追記する。
#OS自体に設定してあれば以下の2行は不要
path = os.getcwd() #exe実行ディレクトリpathを取得するのが重要
TESSERACT_PATH = path + '/poppler-23.10.0/Library/bin' #今回はexeと同じディレクトリに配置させる前提とする
os.environ["PATH"] += os.pathsep + TESSERACT_PATH


def pdfhenkan(file,folder):
 pdf_path = Path(file) # PDFファイルのパス
 
 pages = convert_from_path(str(pdf_path), 150)# PDF -> Image に変換（150dpi）

      # 画像ファイルを１ページずつ保存
 image_dir=Path(folder)# 画像ファイルを保存するファイルを選択
 for i, page in enumerate(pages):
         file_name = pdf_path.stem + "_{:02d}".format(i + 1) + ".png"
         image_path =  image_dir / file_name
         # pngで保存
         page.save(str(image_path), "png")

         count=i # ページ枚数
         
 dirname = os.path.dirname(str(pdf_path))


 print('PDF→PNG end')


