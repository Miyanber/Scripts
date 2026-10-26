#!/usr/bin/env python3
import argparse
import os
import sys
from PyPDF2 import PdfReader, PdfWriter


def right_to_left(input_pdf):
    if not os.path.exists(input_pdf):
        print(f"エラー: 指定されたファイルが存在しません: {input_pdf}")
        sys.exit(1)

    output_pdf = input_pdf.replace(".pdf", "_reordered.pdf")
    if output_pdf == input_pdf:
        output_pdf = f"{input_pdf}_reordered.pdf"

    writer = PdfWriter()
    reader = PdfReader(input_pdf)

    total_pages = len(reader.pages)

    if total_pages % 2 != 0:
        print("警告: 総ページ数が2の倍数ではありません。空白ページが含まれている可能性があります。")

    for page_num in range(total_pages // 2):
        writer.add_page(reader.pages[page_num * 2 + 1])
        writer.add_page(reader.pages[page_num * 2 + 0])

    with open(output_pdf, "wb") as f:
        writer.write(f)

    print("出力完了:", output_pdf)


def main():
    parser = argparse.ArgumentParser(description="2ページずつ見開きでスキャンされた右開きPDFの各見開きペア順序（左右）を並び替えます。")
    parser.add_argument("pdf_path", help="並び替え対象のPDFファイルパス")
    args = parser.parse_args()

    right_to_left(args.pdf_path)


if __name__ == "__main__":
    main()