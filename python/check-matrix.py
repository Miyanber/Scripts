#!/usr/bin/env python3
def matrix_multiply_checker(A, B):
    # 行列のサイズを確認
    rows_A, cols_A = len(A), len(A[0])
    rows_B, cols_B = len(B), len(B[0])

    if cols_A != rows_B:
        return "エラー: 左の列数と右の行数が一致しません。"

    # 結果を格納する行列を0で初期化
    result = [[0 for _ in range(cols_B)] for _ in range(rows_A)]
    
    print(f"--- 計算プロセス ({rows_A}x{cols_B}) ---")
    
    for i in range(rows_A):
        for j in range(cols_B):
            # 各要素の計算式を組み立てる
            terms = []
            val = 0
            for k in range(cols_A):
                product = A[i][k] * B[k][j]
                terms.append(f"({A[i][k]}×{B[k][j]})")
                val += product
            
            result[i][j] = val
            # プロセスを表示
            print(f"位置 [{i+1}, {j+1}]: {' + '.join(terms)} = {val}")
        print("-" * 30)

    return result

# --- 使い方 ---
# 5x5でも、ここを書き換えるだけでOKです
matrix_B = [
    [0, 1, 1, 0, 0],
    [1, 0, 1, 0, 0],
    [1, 1, 0, 0, 0],
    [0, 0, 0, 1, 0],
    [0, 0, 0, 0, 1] 
]
matrix_A = matrix_B


final_result = matrix_multiply_checker(matrix_A, matrix_B)

print("\n最終結果:")
for row in final_result:
    print(row)