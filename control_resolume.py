import os
import time
from datetime import datetime, timedelta
from pythonosc import udp_client

class ResolumeController:
    def __init__(self, target_time_file='target_time.txt', osc_ip='127.0.0.1', osc_port=7000):
        self.target_time_file = target_time_file
        self.osc_client = udp_client.SimpleUDPClient(osc_ip, osc_port)
        self.play_time = self.get_play_time()

    def get_play_time(self):
        if not os.path.exists(self.target_time_file):
            with open(self.target_time_file, 'w') as f:
                f.write('hours: 16\nminutes: 45\n')
            return datetime.now().replace(hour=16, minute=45, second=0, microsecond=0)
        else:
            with open(self.target_time_file, 'r') as f:
                lines = f.readlines()
                hours = int(lines[0].split(':')[1].strip())
                minutes = int(lines[1].split(':')[1].strip())
                now = datetime.now()
                play_time = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
                if play_time < now:
                    play_time += timedelta(days=1)
                return play_time

    def send_osc_command(self):
        # クリップを選択するOSCコマンドを送信（必要に応じてアドレスを変更してください）
        self.osc_client.send_message('/composition/layers/1/clips/1/select', 1)
        time.sleep(0.1)  # コマンドの処理が間に合うように短い遅延を挿入

        # 再生状態に設定するOSCコマンドを送信
        self.osc_client.send_message('/composition/layers/1/clips/1/transport/position/behaviour/playdirection', 2)
        self.osc_client.send_message('/composition/selectedclip/transport/position/behaviour/playdirection', 2)

        # 元のOSCコマンドを送信
        self.osc_client.send_message('/composition/layers/1/clips/1/connect', 1)
        print('\nコマンドを送信しました。プログラムを終了します。')

    def run(self):
        try:
            while True:
                now = datetime.now()
                remaining = self.play_time - now
                remaining_seconds = int(remaining.total_seconds())
                if remaining_seconds <= 0:
                    self.send_osc_command()
                    break
                hours, remainder = divmod(remaining_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                current_time_str = now.strftime('%H:%M:%S')
                play_time_str = self.play_time.strftime('%H:%M:%S')
                remaining_str = f'{hours}時間{minutes}分{seconds}秒'
                print(f'\r現在時刻: {current_time_str} | 再生時刻: {play_time_str} | 残り時間: {remaining_str}', end='')
                time.sleep(1)
        except KeyboardInterrupt:
            print('\nプログラムが中断されました。')

if __name__ == '__main__':
    controller = ResolumeController()
    controller.run() 