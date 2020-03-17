import os
os.system('chcp 950')
from threading import Thread
from datetime import datetime, timedelta, time as dtime
from dateutil.parser import parse
from haohaninfo import GOrder
from linebot import LineBotApi
from linebot.models import TextSendMessage

#with open('line.txt') as f:
#token = 'a1jS7SiQ1UKS86CAn+mBVbuWhblGCBy06qM8++yF6x17TjVEvR/jWQrp14qGFwk3LHFwxtdYWZVUR04CZ6mZ3OyJC3ISHorY33qgOIirwYkAwUh9KW4pLjUFJG+FCh0InF2dBUo4ses5oKpUb0ABWQdB04t89/1O/w1cDnyilFU=' #f.readline().strip()
token = '1efrfG/5kHZatudAt23L6zarS7bTfsJYcUmV2kmg5DvF2ArPX87bIxx2x1hXMT9E8Y+YAAZQ0pIJ9sltiGgt4zNSKwRiON11+7LTnBWw7im5+qVyrboj0paDuTvZBCFzHgN2JzMEQEjkZVvgfNaEPQdB04t89/1O/w1cDnyilFU=' # 爽爽弟
id    = 'C8b99dd9ad3608f5be14f5e3ff8bdb4af' #f.readline().strip()
line_bot_api = LineBotApi(token)

try:
    user = input('TNND幹員編號(001=陳董 002=阿倍 003=團長): ')
    user = ['千仔', '陳董', '阿倍', '團長'][int(user)]
except:
    print(f'TNND幹員{user}不存在！')
    exit()

os.system('cls')
print(f'{user}您好，我是爽爽！\n')
month =   input('請問近月代碼: ')
qty =     input('請問進場幾口: ') #sys.argv[3]
job = int(input('請問進場幾趟: '))
print()
gold = [1001000]*10             #1001000.io
gold[1]   = int(input('請問觸發通知上車的 近60秒成交量 大於: '))
g,o,l,d   = map(int, input('且做多的 口差 筆差 口差變動 筆差變動 大於: ').split())
gold[2:6] = g,o,l,d
g,o,l,d   = map(int, input('或做空的 口差 筆差 口差變動 筆差變動 小於: ').split())
gold[6: ] = g,o,l,d
print()
rod = int(input('請問觸發通知點的 幾點內 才上車: '))
P,L = map(int, input('請問大範圍的下車 停利點 停損點: ').split())
p,l = map(int, input('請問小範圍的下車 停利點 停損點: ').split())
print()
year = str(datetime.now().year)[-1]
prod1 = 'TXF' + month + year #sys.argv[1]
prod2 = 'TXF' + (chr(ord(month)+1) + year if month !='L' else 'A' +chr(ord(year)+1)) #sys.argv[2]
prod  = 'TX00' if user != '千仔' else prod1 #sys.argv[4]
broker = 'Capital_Future' if prod == 'TX00' else 'Simulator'
GOC = GOrder.GOCommand()
GOC.AddQuote(broker, prod)
GOC.AddQuote('Simulator', prod1+','+prod2)

def match2():
    global Volume2, bought2, sold2
    for tick in GOrder.GOQuote().Describe('Simulator', 'match', prod2):
        try:
            Volume2, bought2, sold2 = map(int, tick[4:])
        except:
            continue
def commission1():
    global Buying1, Selling1
    for tick in GOrder.GOQuote().Describe('Simulator', 'commission', prod1):
        try:
            buying1, Buying1, selling1, Selling1 = map(int, tick[2:])
        except:
            continue
def commission2():
    global Buying2, Selling2
    for tick in GOrder.GOQuote().Describe('Simulator', 'commission', prod2):
        try:
            buying2, Buying2, selling2, Selling2 = map(int, tick[2:])
        except:
            continue
Thread(target=match2).start()
Thread(target=commission1).start()
Thread(target=commission2).start()

queue = []
def diff(queue, value, seconds=60):
    queue.append((time, value))
    for t, v in queue[:]:
        if parse(time) - parse(t) > timedelta(seconds=seconds):
            queue.pop(0)
        else:
            return  value - v

def zeroing(clock, minutes):
    global clk1, clk5
    result = False
    while parse(time).time() >= clock:
        minute = clock.minute + minutes
        hour   = clock.hour + minute//60
        clock  = dtime(hour%24, minute%60, 1)   # 冰火每五分零秒末紀錄
        result =  True
    if minutes == 1:
        clk1 = clock
    else:
        clk5 = clock
    return result

def LINE(msg):
    try:
        line_bot_api.push_message(id, TextSendMessage(text=msg))
    except:
        print('LINE error')

def onset():
    global RODorder
    RODorder = GOC.Order(broker, prod, on, str(price_within), str(qty), 'ROD', 'LMT', '1')
    try:
        int(RODorder)
        GA = GOC.GetAccount(broker, RODorder)
        MA = GOC.MatchAccount(broker, RODorder)
        LINE(info + f'委託序號\n{GA[0][:-2]}')
    except:
        LINE(info + f'錯誤訊息：{RODorder}')
def offset():
    GOC.Delete(broker, RODorder)
    stock = GOC.GetInStock(broker)
    if stock:
        IOCorder = GOC.Order(broker, prod, off, str(price), stock[0].split(',')[1].strip('-'), 'IOC', 'MKT', '1')
        try:
            int(IOCorder)
            GA = GOC.GetAccount(broker, IOCorder)
            MA = GOC.MatchAccount(broker, IOCorder)
            LINE(info + f'委託序號\n{GA[0][:-2]}')
        except:
            LINE(info + f'錯誤訊息：{IOCorder}')

def plan():
    global onboard, delay, todo, clk, on, off, price_within, price_to_win, price_to_lose, info
    if 9 <= parse(time).hour < 12 and not onboard and not delay and todo and clk != clk5:
        if stones[1] > gold[1] and (
            stones[2] > gold[2] and stones[3] > gold[3] and stones[4]+stonez[4] > gold[4] and stones[5]+stonez[5] > gold[5] and 0 < stonez[4] < 900 and 0 < stonez[5] < 700 and K[3] > K[2] and K[1] >= K[0] or
            stones[2] < gold[6] and stones[3] < gold[7] and stones[4]+stonez[4] < gold[8] and stones[5]+stonez[5] < gold[9] and 0 > stonez[4] >-900 and 0 > stonez[5] >-700 and K[3] < K[2] and K[1] <= K[0] ):
            onboard, clk = True, clk5
            s_p, s_l = (p, l) if abs(K[3] - K[2]) < abs(K[1] - K[0]) else (P, L)
            on, off = ('B', 'S') if stonez[5] > 0 else ('S', 'B')
            price_within  = price + (rod if on == 'B' else -rod)
            price_to_win  = price + (s_p if on == 'B' else -s_p)
            price_to_lose = price - (s_l if on == 'B' else -s_l)
            info += f"上車做{'多' if on == 'B' else '空'}。。。\n\n"
            onset()
    elif onboard:
        if 13 <= parse(time).hour < 14:
            onboard, delay, todo = False, False, job
            info += '被老司機趕下車了\n\n'
            offset()
        elif on == 'B' and price <= price_to_lose or \
             on == 'S' and price >= price_to_lose:
            onboard, delay, todo = False, False, todo-1
            info += '下車停損 (╥﹏╥)\n\n'
            offset()
        elif on == 'B' and price >= price_to_win or \
             on == 'S' and price <= price_to_win:
            onboard, delay, todo = False, price_to_win, todo-1
    elif delay:
        if on == 'B' and price > price_to_win or \
           on == 'S' and price < price_to_win:
            price_to_win = delay + (1 if on == 'B' else -1)
        elif on == 'B' and price < price_to_win or \
             on == 'S' and price > price_to_win:
            delay = False
            info += '下車停利 (*´∀`)~♥\n\n'
            offset()
    elif not 8 <= parse(time).hour < 14:
        onboard, delay, todo = False, False, job

onboard, delay, todo, clk, clk1, clk5, K, close, stonez = False, False, job, dtime(), dtime(), dtime(), [0]*5, 0, [0]*6

print('時間\t', '總量', '量/60s', '口差', '筆差', '口變', '筆變', '價', sep='\t')
for tick in GOrder.GOQuote().Describe('Simulator', 'match', prod1):
    try:
        time, price, Lots, Volume1, bought1, sold1 = tick[0], *map(int, tick[2:])
    except:
        continue
    try:
        bought2
    except:
        continue
    try:
        Buying1
    except:
        continue
    try:
        Buying2
    except:
        continue

    stones = [Volume1 + Volume2]
    stones.append(diff(queue, Volume1))
    stones.append(Buying1 - Selling1 + Buying2 - Selling2)
    stones.append(sold1 - bought1 + sold2 - bought2)
    stones.append(stones[2] - stonez[2])
    stones.append(stones[3] - stonez[3])
    if zeroing(clk1, 1):
        K.pop(0)
        K.pop(0)
        K.append(close)
        K.append(price)
        if delay:
            delay = price_to_win = price
    close = price
    if zeroing(clk5, 5):
        stonez = stones[:]
        stones[4:] = 0, 0

    print(time.split()[-1], *stones, price, sep='\t')
    info = f'{time}\n{stones[1:]}\n{stonez[1:]}\n{K[:-1]}\n{price}\n{user}'
    plan()