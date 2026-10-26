#!/usr/bin/env python3
import argparse
import os
import sys
from PyPDF2 import PdfReader, PdfWriter


def reorder_booklet(input_pdf, reverse=False, left_to_right=True):
    """reorders booklet

    Args:
        input_pdf (str): 変換するPDFのファイルパス.
        reverse (bool, optional): 逆順にするかどうか（内側からスキャンを取った際に利用）. Defaults to False.
        left_to_right (bool, optional): 横書き（左開き）かどうか. Defaults to True.
    """
    if not os.path.exists(input_pdf):
        print(f"エラー: 指定されたファイルが存在しません: {input_pdf}")
        sys.exit(1)

    output_pdf = input_pdf.replace(".pdf", "_reordered.pdf")
    if output_pdf == input_pdf:
        output_pdf = f"{input_pdf}_reordered.pdf"

    writer = PdfWriter()
    reader = PdfReader(input_pdf)

    total_pages = len(reader.pages)

    if total_pages % 4 != 0:
        print("警告: 総ページ数が4の倍数ではありません。空白ページが含まれている可能性があります。")

    if reverse:
        for page_num in reversed(range(total_pages // 4)):
            writer.add_page(reader.pages[page_num * 4 + 2])
            writer.add_page(reader.pages[page_num * 4 + 3])
            writer.add_page(reader.pages[page_num * 4 + 0])
            writer.add_page(reader.pages[page_num * 4 + 1])
        with open(output_pdf, "wb") as f:
            writer.write(f)

        reader = PdfReader(output_pdf)
        writer = PdfWriter()

    total_pages = len(reader.pages)

    for page_num in range(total_pages // 4):
        if left_to_right:
            writer.add_page(reader.pages[page_num * 4 + 1])
            writer.add_page(reader.pages[page_num * 4 + 2])
        else:
            writer.add_page(reader.pages[page_num * 4 + 0])
            writer.add_page(reader.pages[page_num * 4 + 3])

    for page_num in reversed(range(total_pages // 4)):
        if left_to_right:
            writer.add_page(reader.pages[page_num * 4 + 3])
            writer.add_page(reader.pages[page_num * 4 + 0])
        else:
            writer.add_page(reader.pages[page_num * 4 + 2])
            writer.add_page(reader.pages[page_num * 4 + 1])

    with open(output_pdf, "wb") as f:
        writer.write(f)

    print("出力完了:", output_pdf)


def main():
    parser = argparse.ArgumentParser(description="小冊子（面付け）スキャンされたPDFを通常のページ順に並び替えます。")
    parser.add_argument("pdf_path", help="並び替え対象のPDFファイルパス")
    parser.add_argument("--reverse", action="store_true", help="内側からスキャンした場合など、逆順から開始する場合に指定")
    parser.add_argument("--right-to-left", dest="left_to_right", action="store_false", default=True, help="縦書き・右開き（右から左へ読む冊子）の場合に指定")
    args = parser.parse_args()

    reorder_booklet(args.pdf_path, reverse=args.reverse, left_to_right=args.left_to_right)


if __name__ == "__main__":
    main()