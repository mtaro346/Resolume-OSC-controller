import os
import time
from datetime import datetime, timedelta
from pythonosc import udp_client
import csv

class ResolumeController:
    def __init__(self, target_time_file='target_time_multi.csv', osc_ip='127.0.0.1', osc_port=7000):
        # 初期化メソッド。ターゲット時間ファイル、OSCのIPとポートを設定し、再生時間を取得します。
        self.target_time_file = target_time_file
        self.osc_client = udp_client.SimpleUDPClient(osc_ip, osc_port)
        self.play_times = self.get_play_times()  # 複数の再生時間とコラム番号を取得

    def get_play_times(self):
        # 複数の再生時間とコラム番号を取得するメソッド。CSVファイルから時間とコラム番号を読み込みます。
        play_times = []
        if not os.path.exists(self.target_time_file):
            with open(self.target_time_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([1, '16:45'])  # デフォルトのコラム番号と時間を設定
                writer.writerow([1, '17:00'])
            play_times.append((datetime.now().replace(hour=16, minute=45, second=0, microsecond=0), 1))
            play_times.append((datetime.now().replace(hour=17, minute=0, second=0, microsecond=0), 1))
        else:
            with open(self.target_time_file, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row or len(row) < 2 or not row[0].isdigit():  # 空行や不完全な行、不正なデータをスキップ
                        continue
                    column = int(row[0])
                    try:
                        hours, minutes = map(int, row[1].split(':'))
                    except ValueError:
                        print(f"無効な時間形式: {row[1]}")
                        continue
                    now = datetime.now()
                    play_time = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
                    if play_time < now:
                        play_time += timedelta(days=1)
                    play_times.append((play_time, column))
        
        # 現在時刻から近い順に並べ替え
        play_times.sort(key=lambda x: x[0])
        return play_times

    def send_osc_command(self, column):
        # OSCコマンドを送信するメソッド。指定されたコラムを選択するコマンドを送信します。
        try:
            self.osc_client.send_message(f'/composition/columns/{column}/connect', 1)
            time.sleep(0.1)  # コマンドの処理が間に合うように短い遅延を挿入

            print(f'\nコラム{column}にコマンドを送信しました。')
            return True
        except Exception as e:
            print(f'エラーが発生しました: {e}')
            return False

    def run(self):
        # メインの実行メソッド。指定された再生時間まで待機し、OSCコマンドを送信します。
        try:
            for play_time, column in self.play_times:
                while True:
                    now = datetime.now()
                    remaining = play_time - now
                    remaining_seconds = int(remaining.total_seconds())
                    if remaining_seconds <= 0:
                        for attempt in range(2):  # 2回まで再送信を試みる
                            if self.send_osc_command(column):
                                break
                            print(f'再試行 {attempt + 1}/2')
                            time.sleep(1)
                        else:
                            with open('error_log.txt', 'a') as log_file:
                                log_file.write(f'{datetime.now()}: コマンド送信に失敗しました。\n')
                            print('エラーが発生しました。エラーログを確認してください。')
                        break  # 次のスケジュールに進む
                    hours, remainder = divmod(remaining_seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    current_time_str = now.strftime('%H:%M:%S')
                    play_time_str = play_time.strftime('%H:%M:%S')
                    remaining_str = f'{hours}時間{minutes}分{seconds}秒'
                    print(f'\r現在時刻: {current_time_str} | 再生時刻: {play_time_str} | 再生コラム: {column} | 残り時間: {remaining_str}', end='')
                    time.sleep(1)
        except KeyboardInterrupt:
            print('\nプログラムが中断されました。')

if __name__ == '__main__':
    controller = ResolumeController()
    controller.run() 