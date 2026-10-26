#!/usr/bin/env python3
import os
import sys
import time
import random
import socket
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/drive']
MAX_WORKERS = 4 
TIMEOUT_SECONDS = 120
socket.setdefaulttimeout(TIMEOUT_SECONDS)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(BASE_DIR, 'token.json')
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials.json')

def get_creds():
    """認証情報を取得する（これ自体は一度でOK）"""
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"認証ファイルが見つかりません: {CREDENTIALS_PATH}\n"
                    "Google Cloud ConsoleからOAuth 2.0クライアント認証情報をダウンロードし、"
                    "credentials.json として配置してください。"
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    return creds


def execute_with_backoff(request):
    """指数的バックオフ"""
    for n in range(6):
        try:
            return request.execute()
        except HttpError as e:
            if e.resp.status in [403, 429, 500, 502, 503, 504]:
                time.sleep((2 ** n) + random.random())
            else:
                raise e
    return request.execute()

def copy_worker(file_info, id_mapping, creds):
    """各スレッドで実行される関数。スレッドごとにServiceを生成する"""
    # 重要：スレッドごとに新しいserviceを作ることでSSLエラーを回避
    service = build('drive', 'v3', credentials=creds, cache_discovery=False)
    
    try:
        new_parent_id = id_mapping[file_info['source_parent_id']]
        file_metadata = {
            'name': file_info['name'],
            'parents': [new_parent_id]
        }
        execute_with_backoff(service.files().copy(fileId=file_info['id'], body=file_metadata, supportsAllDrives=True))
        time.sleep(random.uniform(0.1, 0.2)) # 気持ち程度のインターバル
    except Exception as e:
        print(f"\n⚠️ ファイル {file_info['name']} でエラー: {e}")

def scan_folder(service, folder_id, folder_list, file_list):
    """(メインスレッド用) 構造スキャン"""
    query = f"'{folder_id}' in parents and trashed = false"
    results = execute_with_backoff(service.files().list(
        q=query, fields="nextPageToken, files(id, name, mimeType)",
        supportsAllDrives=True, includeItemsFromAllDrives=True
    ))
    items = results.get('files', [])
    for item in items:
        item['source_parent_id'] = folder_id
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            folder_list.append(item)
            scan_folder(service, item['id'], folder_list, file_list)
        else:
            file_list.append(item)

def main():
    creds = get_creds()
    # メイン用のservice
    main_service = build('drive', 'v3', credentials=creds, cache_discovery=False)

    if len(sys.argv) > 1:
        folder_a_id = sys.argv[1].strip()
    else:
        folder_a_id = input("コピー元のフォルダIDを入力: ").strip()

    if not folder_a_id:
        print("フォルダIDが指定されていません。終了します。")
        return


    try:
        folder_a_metadata = execute_with_backoff(main_service.files().get(
            fileId=folder_a_id, fields='name', supportsAllDrives=True))
        folder_name = folder_a_metadata['name']

        print(f"🔍 スキャン中...")
        all_folders, all_files = [], []
        scan_folder(main_service, folder_a_id, all_folders, all_files)
        
        # 親フォルダ作成
        root_folder_b = execute_with_backoff(main_service.files().create(
            body={'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}, fields='id'))
        
        id_mapping = {folder_a_id: root_folder_b['id']}

        # フォルダ構築 (シングルスレッド)
        if all_folders:
            print(f"📁 フォルダ構造を再現中...")
            for folder in tqdm(all_folders, desc="Folders"):
                new_f = execute_with_backoff(main_service.files().create(
                    body={'name': folder['name'], 'mimeType': 'application/vnd.google-apps.folder',
                          'parents': [id_mapping[folder['source_parent_id']]]}, fields='id'))
                id_mapping[folder['id']] = new_f['id']

        # ファイル並列コピー (スレッドごとにServiceを生成)
        if all_files:
            print(f"🚀 並列コピー中 (Workers: {MAX_WORKERS})...")
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                # 引数を固定するためにlambdaを使用
                list(tqdm(executor.map(lambda f: copy_worker(f, id_mapping, creds), all_files), 
                          total=len(all_files), desc="Files"))

        print(f"\n✨ 完了しました！")

    except Exception as e:
        print(f"\n❌ エラー: {e}")
    finally:
        input("\nEnterで終了...")

if __name__ == '__main__':
    main()