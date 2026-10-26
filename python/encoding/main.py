#!/usr/bin/env python3
import os
import sys
import chardet


def convert_to_utf8(target_dir):
    # フォルダ内を再帰的に歩き回る
    for root, dirs, files in os.walk(target_dir):
        for filename in files:
            file_path = os.path.join(root, filename)
            
            # バイナリモードで読み込んで文字コードを判定
            try:
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                    
                # ファイルが空の場合はスキップ
                if not raw_data:
                    continue
                
                # エンコードの判定
                res = chardet.detect(raw_data)
                encoding = res['encoding']
                confidence = res['confidence']

                # 判定できなかった、または既にUTF-8（ASCII含む）の場合はスキップ
                if encoding is None or encoding.upper() == 'UTF-8' or encoding.upper() == 'ASCII':
                    print(f"Skip: {file_path} (Already {encoding})")
                    continue

                # 判定したエンコードでデコードし、UTF-8で上書き保存
                print(f"Converting: {file_path} ({encoding} -> UTF-8, Confidence: {confidence:.2f})")
                
                content = raw_data.decode(encoding)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            except Exception as e:
                print(f"Error: Could not process {file_path}. Reason: {e}")

if __name__ == "__main__":
    target_directory = sys.argv[1] if len(sys.argv) > 1 else './target'
    if not os.path.exists(target_directory):
        print(f"エラー: 指定されたディレクトリが存在しません: {target_directory}")
        print("使用法: python main.py [対象ディレクトリパス (デフォルト: ./target)]")
        sys.exit(1)
    convert_to_utf8(target_directory)