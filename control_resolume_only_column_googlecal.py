import os
import datetime
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from pythonosc import udp_client

class ResolumeController:
    def __init__(self, pc_name, osc_ip='127.0.0.1', osc_port=7000):
        self.pc_name = pc_name
        self.osc_client = udp_client.SimpleUDPClient(osc_ip, osc_port)

    def get_calendar_events(self):
        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        service = build('calendar', 'v3', credentials=creds)

        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        return events

    def process_calendar_events(self, events):
        valid_events = []

        # イベントのリストを作成
        for event in events:
            event_summary = event['summary']
            if ',' in event_summary:
                name, command = event_summary.split(',')
                if name.strip() == self.pc_name:
                    start_time_str = event['start'].get('dateTime', event['start'].get('date'))
                    start_time = datetime.datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                    valid_events.append((name.strip(), command.strip(), start_time))
            # プライバシーのため、他のイベントはログに表示しない

        # イベントを開始時間でソート
        valid_events.sort(key=lambda x: x[2])

        # ログにすべてのイベントを羅列
        print("イベントリスト:")
        for name, command, start_time in valid_events:
            print(f"{name},{command} {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # 各イベントのカウントダウンを表示
        for name, command, start_time in valid_events:
            now = datetime.datetime.now(datetime.timezone.utc)
            if start_time < now:
                print(f"過去の時間のため無視されます: {start_time}")
            else:
                print(f"カウントダウンを開始します: {name},{command} {start_time.strftime('%H:%M')}")
                time_to_start = (start_time - now).total_seconds()
                while time_to_start > 0:
                    print(f"{name},{command} {start_time.strftime('%H:%M')} 残り{int(time_to_start)}秒", end='\r')
                    time.sleep(1)
                    time_to_start -= 1

                if command == 'run':
                    self.send_osc_command('/composition/columns/1/connect', 1)
                elif command == 'stop':
                    self.send_osc_command('/composition/columns/1/disconnect', 1)

    def send_osc_command(self, address, value):
        try:
            self.osc_client.send_message(address, value)
            print(f'OSCコマンドを送信しました: {address} {value}')
        except Exception as e:
            print(f'エラーが発生しました: {e}')

    def run(self):
        try:
            events = self.get_calendar_events()
            self.process_calendar_events(events)
        except KeyboardInterrupt:
            print('\nプログラムが中断されました。')

if __name__ == '__main__':
    controller = ResolumeController(pc_name="A")
    controller.run() 
