import os
import time
from datetime import datetime, timedelta
from pythonosc import udp_client

class ResolumeController:
    def __init__(self, target_time_file='target_time_multi.txt', osc_ip='127.0.0.1', osc_port=7000):
        # 初期化メソッド。ターゲット時間ファイル、OSCのIPとポートを設定し、再生時間を取得します。
        self.target_time_file = target_time_file
        self.osc_client = udp_client.SimpleUDPClient(osc_ip, osc_port)
        self.play_times = self.get_play_times()  # 複数の再生時間を取得

    def get_play_times(self):
        # 複数の再生時間を取得するメソッド。ファイルから時間を読み込みます。
        play_times = []
        if not os.path.exists(self.target_time_file):
            with open(self.target_time_file, 'w') as f:
                f.write('16:45\n17:00\n')  # デフォルトの時間を設定
            play_times.append(datetime.now().replace(hour=16, minute=45, second=0, microsecond=0))
            play_times.append(datetime.now().replace(hour=17, minute=0, second=0, microsecond=0))
        else:
            with open(self.target_time_file, 'r') as f:
                for line in f:
                    hours, minutes = map(int, line.strip().split(':'))
                    now = datetime.now()
                    play_time = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
                    if play_time < now:
                        play_time += timedelta(days=1)
                    play_times.append(play_time)
        return play_times

    def send_osc_command(self):
        # OSCコマンドを送信するメソッド。コラム1を選択するコマンドを送信します。
        try:
            self.osc_client.send_message('/composition/columns/1/connect', 1)
            time.sleep(0.1)  # コマンドの処理が間に合うように短い遅延を挿入

            print('\nコマンドを送信しました。プログラムを終了します。')
            return True
        except Exception as e:
            print(f'エラーが発生しました: {e}')
            return False

    def run(self):
        # メインの実行メソッド。指定された再生時間まで待機し、OSCコマンドを送信します。
        try:
            for play_time in self.play_times:
                while True:
                    now = datetime.now()
                    remaining = play_time - now
                    remaining_seconds = int(remaining.total_seconds())
                    if remaining_seconds <= 0:
                        for attempt in range(2):  # 2回まで再送信を試みる
                            if self.send_osc_command():
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
                    print(f'\r現在時刻: {current_time_str} | 再生時刻: {play_time_str} | 残り時間: {remaining_str}', end='')
                    time.sleep(1)
        except KeyboardInterrupt:
            print('\nプログラムが中断されました。')

if __name__ == '__main__':
    controller = ResolumeController()
    controller.run() 