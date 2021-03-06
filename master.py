import pickle
import time
import os

# pyinstaller --onefile master.py

with open('settings.txt', 'rt') as f:
    inp = f.read()

inp = inp.split('\n')
for i in range(len(inp)):
    if inp[i] == '':
        del inp[i]
inp[0] = float(inp[0])

for i in range(3, len(inp)):
    with open('start.pickle', 'wb') as f:
        pickle.dump([inp[0], inp[1], inp[2], inp[i]], f)
    os.startfile('autorecord.exe')
    while os.path.isfile(os.path.join(os.getcwd(), 'start.pickle')):
        time.sleep(0.25)
