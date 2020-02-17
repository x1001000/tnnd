import os
os.system('chcp 950')
from time import sleep
from threading import Thread
from datetime import datetime, timedelta, time as dtime
from dateutil.parser import parse
from haohaninfo import GOrder
from linebot import LineBotApi
from linebot.models import TextSendMessage

#with open('line.txt') as f:
token = '1efrfG/5kHZatudAt23L6zarS7bTfsJYcUmV2kmg5DvF2ArPX87bIxx2x1hXMT9E8Y+YAAZQ0pIJ9sltiGgt4zNSKwRiON11+7LTnBWw7im5+qVyrboj0paDuTvZBCFzHgN2JzMEQEjkZVvgfNaEPQdB04t89/1O/w1cDnyilFU=' #f.readline().strip()
id    = 'C8b99dd9ad3608f5be14f5e3ff8bdb4af' #f.readline().strip()
line_bot_api = LineBotApi(token)

try:
    user = input('TNND幹員編號(001=陳董 002=阿倍 003=團長): ')
    user = ['千仔', '陳董', '阿倍', '團長'][int(user)]
except:
    print(f'TNND幹員{user}不存在！')
    exit()
daytraders = ['陳董', '阿倍']
daytrading = '1' if user in daytraders else '0'

os.system('cls')
print(f'{user}您好，我是爽爽弟！\n')
month =   input('請問近月代碼: ')
qty =     input('請問進場幾口: ') #sys.argv[3]
job = int(input('請問進場幾趟: '))
print()
gold = [1001000]*10          #1001000.io
gold[1]   = int(input('請問觸發通知上車的 近30秒成交量 大於: '))
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
    global volume2, bought2, sold2
    for tick in GOrder.GOQuote().Describe('Simulator', 'match', prod2):
        try:
            volume2, bought2, sold2 = map(int, tick[4:])
        except:
            continue
def commission1():
    global buying1, selling1
    for tick in GOrder.GOQuote().Describe('Simulator', 'commission', prod1):
        try:
            _, buying1, _, selling1 = map(int, tick[2:])
        except:
            continue
def commission2():
    global buying2, selling2
    for tick in GOrder.GOQuote().Describe('Simulator', 'commission', prod2):
        try:
            _, buying2, _, selling2 = map(int, tick[2:])
        except:
            continue
Thread(target=match2).start()
Thread(target=commission1).start()
Thread(target=commission2).start()

seq_volume1, seq_b_s, seq_B_S = [], [], []
def diff(sequence, value, seconds=30):
    sequence.append((time, value))
    for t, v in sequence[:]:
        if parse(time) - parse(t) > timedelta(seconds=seconds):
            sequence.pop(0)
        else:
            return  value - v

def zeroing(clock, minutes):
    global clk1, clk5
    result = False
    while parse(time).time() >= clock:
        minute = clock.minute + minutes
        hour   = clock.hour + minute//60
        clock  = dtime(hour%24, minute%60)
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
    global onboard, RODorder
    onboard = True
    RODorder = GOC.Order(broker, prod, on, str(price_within), qty, 'ROD', 'LMT', '0')
    sleep(2)
    try:
        int(RODorder)
    except:
        RODorder = GOC.GetAccount(broker, 'All')[-1].split(',')[0]
    LINE('委託紀錄：\n' + str(GOC.GetAccount(broker, RODorder)) + 
        '\n成交紀錄：\n' + str(GOC.MatchAccount(broker, RODorder)) + 
        '\n' + user + '確認一下喔！')

def offset():
    global onboard, todo
    onboard, todo = False, todo-1
    GOC.Delete(broker, RODorder)
    stock = GOC.GetInStock(broker)
    if stock:
        IOCorder = GOC.Order(broker, prod, off, str(price), stock[0].split(',')[1].strip('-'), 'IOC', 'MKT', '0')
        sleep(2)
        try:
            int(IOCorder)
        except:
            IOCorder = GOC.GetAccount(broker, 'All')[-1].split(',')[0]
        LINE('委託紀錄：\n' + str(GOC.GetAccount(broker, IOCorder)) + 
            '\n成交紀錄：\n' + str(GOC.MatchAccount(broker, IOCorder)) + 
            '\n' + user + '確認一下喔！')

print('時間\t', '總量', '量/30s', '口差', '筆差', '口變', '筆變', '價', sep='\t')
volume2 = bought2 = sold2 = buying1 = selling1 = buying2 = selling2 = stones2 = stones3 = close = 0
onboard, todo, first, clk1, clk5, K = False, job, True if user == '陳董' else False, dtime(0,0), dtime(0,0), [0,0,0,0,0]

for tick in GOrder.GOQuote().Describe('Simulator', 'match', prod1):
    try:
        time, price, lots, volume1, bought1, sold1 = tick[0], *map(int, tick[2:])
    except:
        continue

    stones = [
        volume1 + volume2,
        diff(seq_volume1, volume1),
        buying1 - selling1 + buying2 - selling2,
        sold1 - bought1 + sold2 - bought2,
        buying1 - selling1 + buying2 - selling2 - stones2,
        sold1 - bought1 + sold2 - bought2       - stones3]
    if zeroing(clk1, 1):
        K.pop(0)
        K.pop(0)
        K.append(close)
        K.append(price)
    close = price
    if zeroing(clk5, 5):
        stones2, stones3, stones[4], stones[5] = stones[2], stones[3], 0, 0
    print(time.split()[-1], *stones, price, sep='\t')
    info = time + '\n' + str(stones[1:]) + '\n' + str(K[:-1]) + '\n' + str(price) + '\n' + user

    if 8 <= parse(time).hour < 13 and first and stones[1] > 900:
        first = False
        LINE(info[:-2]+'今日首班車來囉！')
    
    if 9 <= parse(time).hour < 12 and not onboard and todo:
        if stones[1] > gold[1]:
            if  stones[2] > gold[2] and stones[3] > gold[3] and stones[4] > gold[4] and stones[5] > gold[5] and K[3] > K[2] and K[1] >= K[0] or \
                stones[2] < gold[6] and stones[3] < gold[7] and stones[4] < gold[8] and stones[5] < gold[9] and K[3] < K[2] and K[1] <= K[0]:
                s_p, s_l = (p, l) if abs(K[3] - K[2]) < abs(K[1] - K[0]) else (P, L)
                on, off = ('B', 'S') if stones[5] > 0 else ('S', 'B')
                price_within  = price + (rod if on == 'B' else -rod)
                price_to_win  = price + (s_p if on == 'B' else -s_p)
                price_to_lose = price - (s_l if on == 'B' else -s_l)
                LINE(info+'上車做'+('多' if on == 'B' else '空')+'。。。')
                onset()
    elif onboard:
        if 13 <= parse(time).hour < 14:
            LINE(info+'被老司機趕下車了')
            offset()
        elif on == 'B' and price >= price_to_win or \
            on == 'S' and price <= price_to_win:
            LINE(info+'下車停利 (*´∀`)~♥')
            offset()
        elif on == 'B' and price <= price_to_lose or \
            on == 'S' and price >= price_to_lose:
            LINE(info+'下車停損 (╥﹏╥)')
            offset()
    elif not 8 <= parse(time).hour < 13:
        todo, first = job, True if user == '陳董' else False