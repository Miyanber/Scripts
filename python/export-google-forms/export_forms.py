#!/usr/bin/env python3
import argparse
import os
import re
import sys
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError

# ==============================================================
# 💡 【設定】 環境変数またはコマンドライン引数で上書き可能です
# ==============================================================

# 1. 入力HTMLファイル名
INPUT_HTML_FILE = os.getenv("EXPORT_FORMS_INPUT_HTML", "class_archive.html")

# 2. フォームをPDF保存するディレクトリ名
OUTPUT_DIR = os.getenv("EXPORT_FORMS_OUTPUT_DIR", "exported_forms")

# 3. Googleログイン情報が保存されているローカルなデータディレクトリ
#    初回実行時、このディレクトリが自動作成されます。
USER_DATA_DIR = os.getenv("EXPORT_FORMS_USER_DATA_DIR", "./playwright_google_context")

# 4. 必須: フォームと解答のPDF出力時に、自動で待ち合わせる時間 (ミリ秒)
#    フォームの読み込みが遅い場合に調整してください。
PAGE_LOAD_TIMEOUT = int(os.getenv("EXPORT_FORMS_TIMEOUT", "60000"))  # 60秒


# ==============================================================
# --------------------------------------------------------------
# 💡 【スクリプト本体】 ここから読み込んでください
# --------------------------------------------------------------
# ==============================================================

def sanitize_filename(title: str) -> str:
    """ファイル名として不正な文字をアンダースコアに置換する"""
    # OSで禁止されている文字や、ファイル名を汚染する可能性のある文字
    safe_title = re.sub(r'[\\/*?<>|:]', '_', title)
    # 連続する空白やアンダースコアを一つにまとめる
    safe_title = re.sub(r'[_\s]+', '_', safe_title).strip('_')
    return safe_title

def extract_form_urls(file_path: str) -> set:
    """
    指定されたHTMLファイルからGoogle FormのURLを抽出する。
    重複を排除し、セットとして返します。
    """
    if not os.path.exists(file_path):
        print(f"🛑 エラー: 指定されたHTMLファイルが見つかりません: {file_path}")
        return set()

    print(f"✨ ステップ1/3: HTMLファイルからURLを解析中...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"🛑 ファイル読み込みエラーが発生しました: {e}")
        return set()

    soup = BeautifulSoup(html_content, 'html.parser')
    found_urls = set()
    
    # Google Form特有のパターンを定義
    patterns = [
        r'docs\.google\.com/forms',
        r'forms\.gle'
    ]

    for link in soup.find_all('a', href=True):
        href = link['href']
        for pattern in patterns:
            if re.search(pattern, href):
                # 絶対URL化されていない場合（相対パスなど）の基本的な処理を組み込む
                if not href.startswith('http'):
                    # URLが適切に形成されていない場合はスキップ
                    continue
                found_urls.add(href)
                break

    print(f"✅ URL抽出完了。合計 {len(found_urls)} 件のユニークなフォームURLが見つかりました。")
    return found_urls

def process_forms(urls: set):
    """
    Playwrightを使用して、各URLをブラウザで開き、PDFとして保存する。
    """
    if not urls:
        print("処理するURLがありません。スクリプトを終了します。")
        return

    # 出力ディレクトリの作成
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"\n💾 PDFは以下のディレクトリに保存されます: {os.path.abspath(OUTPUT_DIR)}")

    # Playwrightセッションの開始
    print("\n🚀 ステップ2/3: ブラウザ自動操作を開始します。")
    try:
        # persistent_contextにより、ログイン状態を維持します
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR, 
                headless=False # デバッグ用：Trueにするとバックグラウンドで動作
            )
            from playwright.sync_api import Page
            page: Page = browser.pages[0] if browser.pages else browser.new_page()
            
            print("-" * 50)
            print("⚠️ 【重要】Googleアカウントのログインが必要な場合があります。")
            input(">> 処理を続行するには、ブラウザを開き、必要なアカウントに手動でログインしてから、Enterキーを押してください...")
            print("-" * 50)

            
            # フォーム処理のメインループ
            for i, url in enumerate(urls):
                print(f"\n[{i+1}/{len(urls)}] 🌐 処理開始: {url}")
                
                # フォームの閲覧処理（page.gotoとwait_until="networkidle"で十分な待ち時間を確保）
                try:
                    page.goto(url, wait_until="networkidle", timeout=PAGE_LOAD_TIMEOUT)
                    
                    if i == 0:
                        import time
                        time.sleep(30) # Google ログインに時間がかかる可能性があるため、最初のURLの読み込み後に追加で待機します。
                    
                    page.wait_for_selector('//*[@id="i5"]', timeout=PAGE_LOAD_TIMEOUT) # ページ全体が読み込まれるのを待つ
                    page.click('//*[@id="i5"]') # フォームの最初の質問をクリックして、完全に読み込まれたことを確認します。
                    
                    
                    
                    # タイトル取得
                    title = page.title()
                    print(f"   タイトル取得: {title}")

                    # ファイル名のためのサニタイズ
                    safe_filename = sanitize_filename(title)
                    file_path = os.path.join(OUTPUT_DIR, f"{safe_filename}.pdf")

                    # PDFの出力オプション設定
                    pdf_options = {
                        "format": "A4",
                        "print_background": True, # 背景グラフィックを含む
                        # "printDeadline": 30000 # 30秒のPDF生成制限
                    }
                    
                    # PDFの生成
                    page.pdf(path=file_path, **pdf_options)
                    print(f"   ✅ 成功: PDFを保存しました: {safe_filename}.pdf")

                except TimeoutError:
                    print(f"   ❌ スキップ: {url} はタイムアウトしました。ロードに時間がかかりすぎた可能性があります。")
                except Exception as e:
                    # 例外処理：特定のフォームで問題が発生しても停止しない
                    print(f"   🛑 致命的エラーを検知: {url} の処理中にエラーが発生しました。スキップし、次へ進みます。エラー内容: {e}")
                
                # 次のページ遷移前の短い待機（システムの負荷分散）
                import time
                time.sleep(2) 

            # 全ての処理が完了したら、最後に待機を促す
            print("\n\n=============================================================")
            print("✅ 全てのURLの処理が完了しました。")
            print("=============================================================")
            
            browser.close()

    except Exception as e:
        print(f"\n❌ 致命的なスクリプトエラーが発生しました: {e}")

def main():
    """メイン実行関数"""
    global INPUT_HTML_FILE, OUTPUT_DIR
    parser = argparse.ArgumentParser(description="HTMLファイルからGoogle FormsのURLを抽出し、PDFとして自動エクスポートします。")
    parser.add_argument("-i", "--input", default=INPUT_HTML_FILE, help=f"入力HTMLファイルパス (デフォルト: {INPUT_HTML_FILE})")
    parser.add_argument("-o", "--output", default=OUTPUT_DIR, help=f"出力ディレクトリ (デフォルト: {OUTPUT_DIR})")
    args = parser.parse_args()

    INPUT_HTML_FILE = args.input
    OUTPUT_DIR = args.output

    # 1. URL抽出
    urls = extract_form_urls(INPUT_HTML_FILE)
    
    if urls:
        # 2. フォーム処理実行
        process_forms(urls)

if __name__ == "__main__":
    main()

