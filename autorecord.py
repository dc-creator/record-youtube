import requests
import os
import time
import subprocess
import datetime
import pickle
import argparse
import sys
import traceback
import random
import json


# pyinstaller --onefile autorecord.py

def makelog(msg):
    i = 1
    while os.path.isfile(os.path.join(os.getcwd(), 'loga' + str(i) + '.txt')):
        i += 1
    with open('loga' + str(i) + '.txt', 'wt') as f:
        f.write(msg)


class TwitchRecorder:
    def __init__(self):
        # global configuration
        self.client_id = "jzkbprff40iqj646a697cyrvl0zt2m6"  # don't change this
        self.refresh = None
        self.recorded_path = os.getcwd()

        # user configuration
        self.username = None
        self.quality = None
        self.videostatus = None

    def run(self):
        """
        # make sure the interval to check user availability is not less than 15 seconds
        if self.refresh < 15:
            print("Check interval should not be lower than 15 seconds.")
            self.refresh = 15
            print("System set check interval to 15 seconds.")
        """

        print("Checking for", self.username, "every", self.refresh, "seconds. Record with", self.quality, "quality.")
        self.loopcheck()

    def check_user(self):
        # 0: online,
        # 1: offline,
        # 2: not found,
        # 3: error
        info = None
        status = 3
        try:
            h = {"Client-ID": self.client_id, "Accept": "application/vnd.twitchtv.v5+json"}
            r = requests.get(f"https://api.twitch.tv/kraken/users?login={self.username}", headers=h)
            user_id = r.json().get("users", [{}])[0].get("_id", "")

            r = requests.get(f"https://api.twitch.tv/kraken/streams/{user_id}", headers=h, timeout=15)
            r.raise_for_status()
            info = r.json()
            if info['stream'] is None:
                status = 1
            else:
                status = 0
        except json.decoder.JSONDecodeError:
            status = 2

        return status, info

    def loopcheck(self):
        while True:
            status, info = self.check_user()

            if status == 2:
                sys.exit('????????? ???????????? ????????? ', self.username, '??? ???????????? ????????? ????????????')

            elif status == 3:
                print(datetime.datetime.now().strftime("%Hh%Mm%Ss"), "???????????? ?????? ????????? ???????????? 1??? ?????? ????????? ???????????????")
                time.sleep(60)

            elif status == 1:
                print(self.username, "????????? ??????????????????", self.refresh, "??? ?????? ?????????????????????.")
                time.sleep(self.refresh)

            elif status == 0:
                print(self.username, "????????????")

                while True:
                    recorded_filename = ''
                    for i in range(20):
                        recorded_filename += random.choice('abcdefghijklmnopqrstuvwxyz')
                    recorded_filename += '.mp4'
                    if not os.path.isfile(recorded_filename):
                        break

                res = 'recording was successful\n'

                # start streamlink process
                subprocess.call(
                    ["streamlink", "--twitch-disable-hosting", "--twitch-disable-ads", "twitch.tv/" + self.username,
                     self.quality, "-o", recorded_filename])

                if os.path.isfile(recorded_filename) is False:
                    print('????????????, ?????? ????????? ?????? ???????????????')
                    res = subprocess.Popen(
                        ["streamlink", "--twitch-disable-hosting", "--twitch-disable-ads", "twitch.tv/" + self.username,
                         'best', "-o", recorded_filename])

                print("????????? ??????")

                videoname = info['stream']['created_at'][:10].replace('-', '') \
                            + ' ' + info['stream']['channel']['display_name'].replace('_', '')

                arg = argparse.Namespace(auth_host_name='localhost', noauth_local_webserver=False,
                                         auth_host_port=[8080, 8090], logging_level='ERROR',
                                         file=recorded_filename, title=videoname,
                                         description='', category='22',
                                         keywords='', privacyStatus=self.videostatus, res=res)
                while True:
                    if not os.path.isfile(os.path.join(os.getcwd(), 'temp.pickle')):
                        with open('temp.pickle', 'wb') as f:
                            pickle.dump(arg, f)
                        break
                    print("temp.pickle ????????? ??????????????? ???????????????....\n?????? ??? ???????????? ?????? ????????? ????????? ???????????? ???????????????")
                    time.sleep(5)

                os.startfile('upload_video.exe')
                print('????????? ???????????? ???????????? ??????')
                print('15??? ?????? ?????? ????????? ???????????????')
                time.sleep(15)


def main():
    try:
        twitch_recorder = TwitchRecorder()

        data = [30.0, '480p', 'unlisted', 'sunnyglass55']

        try:
            with open('start.pickle', 'rb') as f:
                data = pickle.load(f)
        except FileNotFoundError:
            pass
        finally:
            try:
                os.remove('start.pickle')
            except FileNotFoundError:
                pass

        twitch_recorder.refresh = data[0]
        twitch_recorder.quality = data[1]
        twitch_recorder.videostatus = data[2]
        twitch_recorder.username = data[3]

        twitch_recorder.run()

    except Exception as e:
        makelog(traceback.format_exc())
        print(e)
        print('?????? ??????\n',
              '??? ??? ?????? ????????? ???????????????\n',
              'loga(??????).txt ??? ????????? ??? ?????? ??????\n',
              'https://github.com/dc-creator/record-youtube/issues ??? ???????????????\n',
              '??? ??????????????? 10??? ?????? ???????????????')
        time.sleep(10)
        raise


if __name__ == "__main__":
    main()
