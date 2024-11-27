import os
import time
from datetime import datetime
from pythonosc import udp_client
import traceback

class ResolumeController:
    def __init__(self, osc_ip='127.0.0.1', osc_port=7000):
        self.osc_client = udp_client.SimpleUDPClient(osc_ip, osc_port)

    def send_osc_command(self):
        try:
            # コラム1を選択するためのOSCコマンドを送信
            self.osc_client.send_message('/composition/columns/1/connect', 1)
            time.sleep(0.1)  # コマンドの処理が間に合うように短い遅延を挿入

            # 再生状態に設定するOSCコマンドを送信
            #self.osc_client.send_message('/composition/layers/1/clips/1/transport/position/behaviour/playdirection', 2)
            #self.osc_client.send_message('/composition/layers/2/clips/1/transport/position/behaviour/playdirection', 2)
            #self.osc_client.send_message('/composition/layers/3/clips/1/transport/position/behaviour/playdirection', 2)
            #self.osc_client.send_message('/composition/selectedclip/transport/position/behaviour/playdirection', 2)

            # 元のOSCコマンドを送信
            #self.osc_client.send_message('/composition/layers/1/clips/1/connect', 1)
            print('\nコマンドを送信しました。プログラムを終了します。')
            return True
        except Exception as e:
            print(f'エラーが発生しました: {e}')
            traceback.print_exc()
            return False

    def run(self):
        try:
            time.sleep(1)  # 1秒の遅延を追加
            self.send_osc_command()
        except Exception as e:
            print(f'エラーが発生しました: {e}')
            traceback.print_exc()

if __name__ == '__main__':
    controller = ResolumeController()
    controller.run() 