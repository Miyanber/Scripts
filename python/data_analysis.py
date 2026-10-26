#!/usr/bin/env python3
import os
import sys
import time

# 対象フォルダをコマンドライン引数またはカレントディレクトリから取得
if len(sys.argv) > 1:
    folder_path = sys.argv[1]
else:
    folder_path = "."
    print(f"対象フォルダが指定されていないため、カレントディレクトリ ({os.path.abspath(folder_path)}) を対象とします。")
    print("使用法: python data_analysis.py <対象フォルダパス>\n")

if not os.path.exists(folder_path):
    print(f"エラー: 指定されたフォルダが存在しません: {folder_path}")
    sys.exit(1)

sizes = []

for root, dirs, files in os.walk(folder_path):
    for file in files:
        fp = os.path.join(root, file)
        try:
            sizes.append(os.path.getsize(fp))
        except OSError:
            pass

sizes_len = len(sizes)
if sizes_len == 0:
    print(f"警告: '{folder_path}' 内にファイルが見つかりませんでした。")
    sys.exit(0)


print(f"""
###### 計算対象のデータ ######
データ配列: {sizes}
データ配列の要素数: {sizes_len}
############
""")

# 分散公式を利用して分散を計算
times_a = []
times_b = []
loop_size = 1000

# 定義
for _ in range(loop_size):
    start = time.perf_counter()
    
    mean = sum(sizes) / sizes_len
    temp_sum = 0
    for size in sizes:
        temp_sum += (size - mean)**2
    variance_a = temp_sum / sizes_len
    
    end = time.perf_counter()
    times_a.append(end - start)

# 分散公式
for _ in range(loop_size):
    start = time.perf_counter()
    
    temp_sum = sum(sizes)
    temp_sum_2 = sum(x**2 for x in sizes) # 内包表記で高速化
    variance_b = temp_sum_2 / sizes_len - (temp_sum / sizes_len)**2
    
    end = time.perf_counter()
    times_b.append(end - start)
    
time_a = sum(times_a) / loop_size
time_b = sum(times_b) / loop_size

print(f"""###### 定義通りに計算した結果 ######
分散の値: {variance_a}
{loop_size}回の処理時間の平均: {time_a}
############
""")

print(f"""###### 分散公式を利用して計算した結果 ######
分散の値: {variance_b}
{loop_size}回の処理時間の平均: {time_b}
############
""")