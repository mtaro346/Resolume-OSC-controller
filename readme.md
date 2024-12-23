# Resolume Controller

このプロジェクトは、OSC（Open Sound Control）プロトコルを使用してResolumeを制御するPythonスクリプトです。指定された時間に特定のコラムを選択するためのコマンドを送信します。


## 現場で使う人向けの説明
distフォルダ内にある拡張子がexeとなっているものだけをダウンロードしてください。
ダウンロード後に起動すると自動的にスケジュール設定用のテキストファイル（またはCSVファイル）が作成されます。
自動で作成されたファイルを参考に自身でスケジュールを設定してください。
使用方法がわからない場合は制作者までお問い合わせください。（asukaoita@gmail.com）



## 必要条件（以下開発者向け）
- Python 3.x
- `python-osc` ライブラリ

## インストール

1. Pythonがインストールされていることを確認してください。
2. 必要なライブラリをインストールします。

   ```bash
   pip install python-osc
   ```

## 使用方法

1. `target_time_multi.csv` ファイルを編集して、再生したい時間とコラム番号を設定します。ファイルのフォーマットは以下の通りです：

   ```
   コラム番号, HH:MM
   ```

   例：
   ```
   1, 16:45
   1, 17:00
   ```

2. スクリプトを実行します。

   ```bash
   python control_resolume_only_column_multi.py
   ```

3. スクリプトは指定された時間に自動的にOSCコマンドを送信します。

## 機能

- 指定された時間にResolumeの特定のコラムを選択するOSCコマンドを送信します。
- `target_time_multi.csv` ファイルから再生時間とコラム番号を読み込みます。
- コマンド送信に失敗した場合、最大2回まで再試行します。
- エラーが発生した場合、`error_log.txt` にログを記録します。

## 注意事項

- `target_time_multi.csv` ファイルが存在しない場合、デフォルトの時間とコラム番号が設定されます。
- スクリプトは、現在の時間よりも過去の時間が指定された場合、翌日の同じ時間に設定します。

## ライセンス

このプロジェクトはMITライセンスの下で提供されています。