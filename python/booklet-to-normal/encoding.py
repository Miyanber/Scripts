#!/usr/bin/env python3
def main():
    import os
    import sys
    from glob import glob
    import codecs
    import os.path

    ### ユーザ操作受付処理 ###
    #格納元フォルダの入力
    input_folder = input("対象ファイルが格納されたフォルダパスを入力してください。：")
    if not os.path.exists(input_folder):
        print("入力されたフォルダは存在しません。")
        sys.exit()

    #変換後文字コードの入力
    after_encode =""
    for i in range(1,3):
        input_number = input("変換対象文字コードを選択してください[1 -> SJIS | 2 -> UTF-8]：")
        if input_number == "1":
            after_encode = "cp932" # 'Shift_JIS'とするとWindows環境依存文字が書き込めなくてエラーとなる
            break
        elif input_number == "2":
            after_encode = "utf-8"
            break
        else:
            print("次のリストから選択してください [1 -> SJIS | 2 -> UTF-8]")
            continue
    else:
        print("不正な値が入力されました。")
        sys.exit()

    ### 変換対象ファイル抽出処理 ###
    #格納フォルダ内の全ファイルパスを取得
    file_paths = glob(os.path.join(input_folder, '*'))
    textfile_paths = []

    #テキストファイルのみを抽出してリスト化
    def findFiles(paths):
        for path in paths:
            # パスのファイル名がない場合はディレクトリ
            fileName = str(os.path.basename(path))
            
            if os.path.isfile(path):
                if mime_type_detector(path) == "text/plain":
                    #MIMEがtext/plainの場合、リストに追加
                    textfile_paths.append(path)
            elif os.path.isdir(path):
                paths2 = glob(os.path.join(path, '*'))
                findFiles(paths2)

                
    findFiles(file_paths)
            

    ### 変換前文字コード取得処理 ###
    #テキストファイルの文字コードを取得してファイル名をキーとしたdictに登録
    path_encode_dict = {}
    for path in textfile_paths: 
        encode = textfile_encode_detector(path)
        path_encode_dict[path] = encode


    ### ファイル文字コード変換処理 ###
    for path,before_encode in path_encode_dict.items():
        #元ファイルのデータ取得
        bf = codecs.open(path,'r',encoding=before_encode)
        print(path, before_encode)
        data = bf.read()
        bf.close()

        #新しい文字コードに変換して出力
        af = codecs.open(path,'w',encoding=after_encode)
        af.write(data)
        af.close()

#文字コード判定関数
def textfile_encode_detector(file_path):
    """
    file_pathで指定したファイルの文字コードを返す
    :param file_path:文字コードを判別したいファイルパス
    :return: ファイル名がキー、文字コードが値のdict
    """
    #テキストファイルの文字コード判定（推定）にはChardetを利用
    from chardet.universaldetector import UniversalDetector
    detector = UniversalDetector() 
    encode_type = ""
    with open(file_path,'rb') as f:
        for line in f.readlines():
            detector.feed(line)
            if detector.done:
                break
        detector.close()
        encode_type = detector.result['encoding']
    if encode_type == "Windows-1254" or encode_type == "Windows-1252":
        encode_type = "cp932"
    return encode_type

#ファイル形式判定関数
def mime_type_detector(file_path):
    """
    file_pathで指定したファイル種別をpython-magicで判定し、MIME形式で返す
    :param file_path:ファイル種別を判別したいファイルパス
    :return: MIMEタイプ
    """
    import magic
    # python-magicを利用することで、バイナリーのパターンからファイル形式を判定（推定）可能
    mime_type = magic.from_buffer(open(file_path,'rb').read(2048),mime=True)
    return mime_type

if __name__ == '__main__':
    main()
