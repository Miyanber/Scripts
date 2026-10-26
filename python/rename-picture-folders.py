#!/usr/bin/env python3
import os
import re
import sys

# ==========================================
# 設定: USBメモリや写真フォルダのパス
# 引数で渡すか、実行時に入力してください
# ==========================================


def rename_folders(path):
    if not os.path.exists(path):
        print(f"Error: パスが見つかりません: {path}")
        return

    # パターン1: MM.DD.YYYY (月.日.年)
    # ^(\d{2})\.(\d{2})\.(\d{4})(.*)
    pattern_mdy = re.compile(r'^(\d{2})\.(\d{2})\.(\d{4})(.*)')

    # パターン2: YYYY.MM.DD (年.月.日)
    # ^(\d{4})\.(\d{2})\.(\d{2})(.*)
    pattern_ymd = re.compile(r'^(\d{4})\.(\d{2})\.(\d{2})(.*)')

    for folder_name in os.listdir(path):
        old_path = os.path.join(path, folder_name)
        
        # フォルダ以外はスキップ
        if not os.path.isdir(old_path):
            continue

        new_name = None

        # パターン1 (MM.DD.YYYY) にマッチするか確認
        match_mdy = pattern_mdy.match(folder_name)
        if match_mdy:
            month, day, year, extra = match_mdy.groups()
            new_name = f"{year}-{month}-{day}{extra}"

        else:
            # パターン2 (YYYY.MM.DD) にマッチするか確認
            match_ymd = pattern_ymd.match(folder_name)
            if match_ymd:
                year, month, day, extra = match_ymd.groups()
                new_name = f"{year}-{month}-{day}{extra}"

        # リネーム実行
        if new_name and new_name != folder_name:
            new_path = os.path.join(path, new_name)
            try:
                os.rename(old_path, new_path)
                print(f"Renamed: {folder_name} -> {new_name}")
            except Exception as e:
                print(f"Failed: {folder_name} -> {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_dir = sys.argv[1].strip()
    else:
        target_dir = input("対象フォルダパス（例: E:/Data や D:\\Photos）を入力してください: ").strip()

    if not target_dir:
        print("エラー: パスが入力されていません。終了します。")
        sys.exit(1)

    rename_folders(target_dir)
    print("\n完了しました。")