# Scripts Collection

日常的なタスク自動化、ファイル操作、データ処理、Webスクレイピングなどを効率化するための汎用スクリプト集です。  
Python および Node.js / JavaScript で書かれた独立したツール群で構成されています。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18%2B-green.svg)](https://nodejs.org/)

---

## 目次

1. [リポジトリ構成とツール一覧](#リポジトリ構成とツール一覧)
2. [動作環境・前提条件](#動作環境前提条件)
3. [セットアップ手順](#セットアップ手順)
4. [各スクリプトの使い方・実行例](#各スクリプトの使い方実行例)
   - [Python ツール群](#python-ツール群)
   - [JavaScript / Web ツール群](#javascript--web-ツール群)
5. [セキュリティ・機密情報の管理](#セキュリティ機密情報の管理)
6. [コントリビューション・Issue報告](#コントリビューションissue報告)
7. [ライセンス](#ライセンス)

---

## リポジトリ構成とツール一覧

```text
Scripts/
├── js/
│   ├── chromium_test/         # JR特急空席確認スクレイピング (Playwright)
│   ├── test/                  # 非同期処理等の検証用スクリプト
│   └── hls_viewer.html        # HLS (.m3u8) 動画ストリーミング再生プレイヤー
├── python/
│   ├── booklet-to-normal/     # 面付けスキャンPDFのページ順序並び替え
│   ├── check-matrix.py        # 行列積の計算プロセス可視化・検算
│   ├── data_analysis.py       # ディレクトリ走査と分散計算アルゴリズム比較
│   ├── drive-folder-copy/     # Google Drive フォルダ再帰・並列コピーツール
│   ├── encoding/              # テキストファイルの文字コード判定・一括UTF-8変換
│   ├── export-google-forms/   # HTMLからGoogle Formsを抽出しPDF一括保存
│   ├── rename-picture-folders.py # 日付形式フォルダ名のISO一括正規化
│   └── 予定分析/              # 所要時間・期限に基づくタスク自動スケジューリング
├── .env.example               # 環境変数テンプレート
├── .gitignore                 # バージョン管理除外設定
├── LICENSE                    # MIT ライセンス
├── README.md                  # 本ドキュメント
└── requirements.txt           # Python共通依存パッケージ定義
```

| ディレクトリ / ファイル | 言語 | 役割・概要 |
| :--- | :--- | :--- |
| `python/booklet-to-normal/booklet_to_normal.py` | Python | 小冊子（面付け）でスキャンされたPDFを通常の読書順に並び替え |
| `python/booklet-to-normal/right_to_left_pdf.py` | Python | 2ページ見開きでスキャンされた右開きPDFの左右順序を反転整列 |
| `python/encoding/main.py` | Python | 指定ディレクトリ内のテキストファイルの文字コードを自動判定しUTF-8へ一括変換 |
| `python/drive-folder-copy/main.py` | Python | Google Drive上の指定フォルダ配下をフォルダ階層ごとマルチスレッドで並列コピー |
| `python/export-google-forms/export_forms.py` | Python | 保存されたHTMLからGoogleフォームURLを抽出し、Playwright経由でPDF一括保存 |
| `python/rename-picture-folders.py` | Python | `MM.DD.YYYY` などの表記揺れがあるフォルダ名を `YYYY-MM-DD` に一括リネーム |
| `python/check-matrix.py` | Python | 行列の積（掛け算）の各成分ごとの計算式・途中式をターミナル上に可視化 |
| `python/data_analysis.py` | Python | 指定ディレクトリ内のファイルサイズから分散（定義 vs 分散公式）の計算速度を比較 |
| `python/予定分析/analize.py` | Python | 締切日・所要時間・日毎の空き時間からスケジュールを自動割り当て |
| `js/hls_viewer.html` | HTML/JS | ブラウザ上で `.m3u8` (HLS) ストリーミング動画をプレビューできるプレイヤー |
| `js/chromium_test/index.js` | Node.js | Playwright を利用した JR サンライズ瀬戸・出雲の空席状況自動巡回テスト |

---

## 動作環境・前提条件

- **Python**: 3.9 以上
- **Node.js**: 18.x 以上 (npm または yarn, pnpm)
- **OS**: Windows / macOS / Linux (クロスプラットフォーム対応)

---

## セットアップ手順

### 1. リポジトリのクローン
```bash
git clone https://github.com/Miyanber/Scripts.git
cd Scripts
```

### 2. Python 環境のセットアップ
仮想環境の作成と依存ライブラリのインストールを推奨します：

```bash
# 仮想環境を作成して有効化
python -m venv .venv

# Windows (PowerShell) の場合
.venv\Scripts\Activate.ps1
# macOS / Linux の場合
source .venv/bin/activate

# 依存パッケージの一括インストール
pip install -r requirements.txt

# Playwright 用ブラウザバイナリの導入 (export-google-forms 等を使用する場合)
playwright install chromium
```

### 3. Node.js 環境のセットアップ (JSツールを使用する場合)
```bash
# chromium_test ディレクトリ
cd js/chromium_test
npm install
npx playwright install chromium
cd ../..
```

### 4. 環境変数の設定 (必要に応じて)
ルートディレクトリの `.env.example` をコピーして `.env` を作成し、必要に応じて設定してください：
```bash
cp .env.example .env
```

---

## 各スクリプトの使い方・実行例

### Python ツール群

#### 1. 小冊子スキャンPDFの並び替え (`booklet-to-normal`)
面付け印刷された小冊子をスキャンしたPDFを、1ページずつ通常の読書順に並び替えます。
```bash
# 基本実行 (左開き・横書き)
python python/booklet-to-normal/booklet_to_normal.py path/to/document.pdf

# 内側からスキャンした場合（--reverse）
python python/booklet-to-normal/booklet_to_normal.py path/to/document.pdf --reverse

# 縦書き・右開き冊子の場合（--right-to-left）
python python/booklet-to-normal/booklet_to_normal.py path/to/document.pdf --right-to-left

# 見開き2ページスキャンの左右並び替え
python python/booklet-to-normal/right_to_left_pdf.py path/to/document.pdf
```
※出力は入力ファイル名と同じディレクトリに `_reordered.pdf` として保存されます。

#### 2. 文字コードの一括UTF-8変換 (`encoding`)
対象ディレクトリ内の全テキストファイルの文字コード（Shift_JIS, EUC-JP, CP932等）を自動判定し、UTF-8で上書き保存します。
```bash
# 引数で対象ディレクトリを指定
python python/encoding/main.py path/to/target_directory

# 引数省略時はカレント配下の ./target を処理
python python/encoding/main.py
```

#### 3. Google Drive フォルダの並列コピー (`drive-folder-copy`)
Google Drive 上のフォルダ階層とファイルを、Google Drive API を用いて高速に別フォルダへ複製します。
```bash
cd python/drive-folder-copy

# 1. Google Cloud Console より OAuth 2.0 クライアント認証情報を取得し
#    python/drive-folder-copy/credentials.json として配置（credentials.example.json 参照）

# 2. 実行 (引数にコピー元のフォルダIDを指定、または実行時に対話入力)
python main.py <SOURCE_FOLDER_ID>
```

#### 4. Google Forms の PDF一括保存 (`export-google-forms`)
受講履歴やアーカイブHTMLから Google Forms のリンクを自動抽出し、ログイン状態でPDF化します。
```bash
# 入力HTMLファイルと出力先ディレクトリを指定して実行
python python/export-google-forms/export_forms.py -i archive.html -o ./exported_forms

# デフォルト設定 (class_archive.html -> ./exported_forms/) で実行
python python/export-google-forms/export_forms.py
```

#### 5. 写真フォルダ名の日付正規化 (`rename-picture-folders.py`)
`05.21.2024` や `2024.05.21` といった日付形式のフォルダ名を、ソートしやすい `YYYY-MM-DD` 形式に一括変換します。
```bash
# 引数に対象ディレクトリを指定
python python/rename-picture-folders.py "D:/Photos"

# 引数を省略した場合は対話プロンプトで入力を求められます
python python/rename-picture-folders.py
```

#### 6. 行列積の検算・プロセス可視化 (`check-matrix.py`)
```bash
python python/check-matrix.py
```

#### 7. ファイル走査と分散計算ベンチマーク (`data_analysis.py`)
```bash
python python/data_analysis.py [対象フォルダパス]
```

#### 8. スケジュール自動割り当て (`予定分析`)
```bash
python "python/予定分析/analize.py"
```

---

### JavaScript / Web ツール群

#### 1. HLS動画プレイヤー (`js/hls_viewer.html`)
任意のWebブラウザで `js/hls_viewer.html` をダブルクリックして開きます。  
上部の入力ボックスに再生したい `.m3u8` ストリームのURLを入力して「読み込み」をクリックすることで再生できます。

#### 2. JR空席確認スクレイピング (`js/chromium_test`)
```bash
cd js/chromium_test
node index.js
```

---

## セキュリティ・機密情報の管理

本リポジトリではセキュリティおよびプライバシー保護のため、以下の対策を徹底しています：

- **資格情報の分離**: APIキー、OAuthクライアントシークレット（`credentials.json`）、アクセストークン（`token.json`）、`.env` ファイルなどはすべて `.gitignore` の対象となっています。
- **機密情報のコミット禁止**: 機密情報を含むファイルや個人データはコミットしないでください。設定値は環境変数またはサンプルの `*.example` ファイルを参考に設定してください。

---

## コントリビューション・Issue報告

バグ報告や機能提案、プルリクエストを歓迎します。

1. **Issue 報告**: バグや機能要望がある場合は、再現手順や動作環境（OS、言語バージョン）を添えて GitHub Issues にご起票ください。
2. **プルリクエスト (PR)**:
   - 変更内容を分かりやすく記述してください。
   - 機密情報（個人のパス、トークン、プライベートなURL等）が含まれていないことを事前に確認してください。
   - 新規スクリプトを追加する場合は、スクリプト先頭への適切な Shebang の記述と `README.md` への追記をお願いします。

---

## ライセンス

本リポジトリは [MIT License](LICENSE) の下で公開されています。商用・非商用を問わず自由にご利用・改変いただけます。
