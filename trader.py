import sys
from time import sleep
from threading import Thread
from dateutil.parser import parse
from haohaninfo import GOrder
from linebot import LineBotApi
from linebot.models import TextSendMessage

#with open('line.txt') as f:
token = '/v/dB8kM8/1Hk7YzbuSSHD0r/L8xXNCWwzdNN3Dv8t55bMeiZLJrQlc3Wppn/304LHFwxtdYWZVUR04CZ6mZ3OyJC3ISHorY33qgOIirwYkGTiaCdrrRFS6ia38+qY4Y1WZeCg0+6+3M5KScpwQneAdB04t89/1O/w1cDnyilFU=' #f.readline().strip()
id    = 'C8b99dd9ad3608f5be14f5e3ff8bdb4af' #f.readline().strip()
line_bot_api = LineBotApi(token)

prod1 = sys.argv[1]
prod2 = sys.argv[2]
qty   = sys.argv[3]
prod  = sys.argv[4]
broker = 'Capital_Future' if prod == 'TX00' else 'Simulator'
GOC = GOrder.GOCommand()
GOC.AddQuote(broker, prod)
GOC.AddQuote('Simulator', prod1+','+prod2)

def match2():
    global volume2, bought2, sold2
    for tick in GOrder.GOQuote().Describe('Simulator', 'match', prod2):
        volume2, bought2, sold2 = map(int, tick[4:])
def commission1():
    global buying1, selling1
    for tick in GOrder.GOQuote().Describe('Simulator', 'commission', prod1):
        _, buying1, _, selling1 = map(int, tick[2:])
def commission2():
    global buying2, selling2
    for tick in GOrder.GOQuote().Describe('Simulator', 'commission', prod2):
        _, buying2, _, selling2 = map(int, tick[2:])
Thread(target=match2).start()
Thread(target=commission1).start()
Thread(target=commission2).start()

seq_volume1, seq_b_s, seq_B_S = [], [], []
def diff(interval, sequence, time, value):
    sequence.append((time, value))
    for t, v in sequence[:]:
        if (parse(time) - parse(t)).seconds > interval:
            sequence.pop(0)
        else:
            return  value - v

def LINE(msg):
    try:
        line_bot_api.push_message(id, TextSendMessage(text=msg))
    except:
        print('LINE error')

def onset():
    global onboard, RODorder
    onboard = True
    RODorder = GOC.Order(broker, prod, do, str(price_within), qty, 'ROD', 'LMT', '0')
    sleep(3)
    LINE(str(GOC.MatchAccount(broker, RODorder)))

def offset():
    global onboard, done
    onboard = False
    GOC.Delete(broker, RODorder)
    stock = GOC.GetInStock(broker)
    if stock:
        IOCorder = GOC.Order(broker, prod, od, str(price), stock[0].split(',')[1].strip('-'), 'IOC', 'MKT', '0')
        sleep(3)
        LINE(str(GOC.MatchAccount(broker, IOCorder)))
        done = True

print('時間\t', '總量', '量/30s', '口差', '筆差', '口變/6s', '筆變/6s', '價', sep='\t')
volume2 = bought2 = sold2 = buying1 = selling1 = buying2 = selling2 = 0
onboard = done = False

for tick in GOrder.GOQuote().Describe('Simulator', 'match', prod1):
    time, price, lots, volume1, bought1, sold1 = tick[0], *map(int, tick[2:])

    stones = [  volume1 + volume2, 
        diff(30, seq_volume1, time, volume1), 
        buying1 + buying2 - selling1 - selling2, 
        sold1 + sold2 - bought1 - bought2, 
        diff(6, seq_b_s, time, buying1 + buying2 - selling1 - selling2), 
        diff(6, seq_B_S, time, sold1 + sold2 - bought1 - bought2)    ]
    print(time.split()[-1], *stones, price, sep='\t')
    info = time + '\n' + str(stones[1:]) + '\n' + str(price) + '\n'

    if 8 <= parse(time).hour < 11 and not done and not onboard:
        if stones[1] > 900:
            if (stones[2] > 2000 and stones[3] > 1000 and stones[4] > 50 and stones[5] > 50) or \
                (stones[2] < -2000 and stones[3] < -1000 and stones[4] < -70 and stones[5] < -70):
                do = 'B' if stones[2] > 0 else 'S'
                od = 'B' if stones[2] < 0 else 'S'
                price_within  = price + ( 2 if do == 'B' else  -2)
                price_to_win  = price + (12 if do == 'B' else -12)
                price_to_lose = price + (10 if do == 'S' else -10)
                LINE(info+'上車囉。。。')
                onset()
    elif onboard:
        if 13 <= parse(time).hour < 14:
            LINE(info+'被老司機趕下車了')
            offset()
        elif do == 'B' and price >= price_to_win or \
            do == 'S' and price <= price_to_win:
            LINE(info+'下車停利 (*´∀`)~♥')
            offset()
        elif do == 'B' and price <= price_to_lose or \
            do == 'S' and price >= price_to_lose:
            LINE(info+'下車停損 (╥﹏╥)')
            offset()
    elif not 8 <= parse(time).hour < 11:
        done = False