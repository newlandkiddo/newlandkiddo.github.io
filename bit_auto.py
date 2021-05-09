import time
import pyupbit
import datetime

access = "your-access"
secret = "your-secret"

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("로그인 완료했습니다.")

# 분석할 코인 목록 (전일대비 상승율 10위)
listcoin = ["KRW-ANKR", "KRW-BCHA", "KRW-ELF", "KRW-AXS", "KRW-MANA", "KRW-WAXP", "KRW-DOGE", "KRW-SAND", "KRW-DAWN", "KRW-ETC"]

# 거래할 코인 및 k값 설정
listcoinsper = []

import pyupbit
import numpy as np

for i in listcoin:
    coinname = i
    print(i)
    listk = []
    listper = []
    df = pyupbit.get_ohlcv(i, count = 7)
    for k in np.arange(0.1, 1.0, 0.1):     

        df['range'] = (df['high'] - df['low']) * k
        df['target'] = df['open'] + df['range'].shift(1)
        fee = 0.0005
        df['ror'] = np.where(df['high'] > df['target'], df['close'] / df['target'] - fee, 1)
        ror = df['ror'].cumprod()[-2]

        print("%.1f %f" % (k, ror))
        listk.append(k)
        listper.append(ror) 
    choicek = round(10*listk[listper.index(max(listper))])/10
    choiceper = max(listper)
    listcoinsper.append(choiceper)
bestper = max(listcoinsper)
bestcoin = listcoin[listcoinsper.index(max(listcoinsper))]

df = pyupbit.get_ohlcv(bestcoin, count = 7)
for k in np.arange(0.1, 1.0, 0.1):
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)
    fee = 0.0005
    df['ror'] = np.where(df['high'] > df['target'], df['close'] / df['target'] - fee, 1)
    ror = df['ror'].cumprod()[-2]
    print("%.1f %f" % (k, ror))
    listk.append(k)
    listper.append(ror) 
bestk = round(10*listk[listper.index(max(listper))])/10

coinname = bestcoin
coinname2 = bestcoin[4:]
pernum = bestper
knum = bestk
print("거래할 코인은 " + coinname2 + "입니다.")
print("예상수익률은 " + str(pernum - fee*2) + "입니다.")
print("최적 k값은 " + str(knum) + "입니다.")

# 매수, 매도 기준가 설정
df = pyupbit.get_ohlcv(coinname, interval="day", count=2)
buy_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * bestk
sell_price = df.iloc[0]['close'] - (df.iloc[0]['high'] - df.iloc[0]['low']) * 0.1
print("매수 기준가는 " + str(buy_price) + "입니다.")
print("매도 기준가는 " + str(sell_price) + "입니다.")

# 자동매매 시작
print("자동매매 프로그램을 시작합니다.")
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time(coinname)
        end_time = start_time + datetime.timedelta(days=1)
        if start_time + datetime.timedelta(seconds=10) < now < end_time:
            current_price = get_current_price(coinname)
            if buy_price < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    buy_result = upbit.buy_market_order(coinname, krw*0.9995)
                    print("매수합니다. " + coinname2 + str(buy_result))
            elif sell_price > current_price:
                btc = get_balance(coinname2)
                if btc * current_price > 5000:
                    sell_result = upbit.sell_market_order(coinname, btc*0.9995)
                    print("매도합니다."  + coinname +  str(sell_result))

# # 매일 09:00:00 ~ 09:00:10에는 최적 코인과 k값 갱신
        else:
            listcoinsper = []

            for i in listcoin:
                coinname = i
                print(i)
                listk = []
                listper = []
                df = pyupbit.get_ohlcv(i, count = 7)
                for k in np.arange(0.1, 1.0, 0.1):     

                    df['range'] = (df['high'] - df['low']) * k
                    df['target'] = df['open'] + df['range'].shift(1)
                    fee = 0.0005
                    df['ror'] = np.where(df['high'] > df['target'], df['close'] / df['target'] - fee, 1)
                    ror = df['ror'].cumprod()[-2]

                    print("%.1f %f" % (k, ror))
                    listk.append(k)
                    listper.append(ror) 
                choicek = round(10*listk[listper.index(max(listper))])/10
                choiceper = max(listper)
                listcoinsper.append(choiceper)
            bestper = max(listcoinsper)
            bestcoin = listcoin[listcoinsper.index(max(listcoinsper))]
            bestcoin2 = bestcoin[4:]

            df = pyupbit.get_ohlcv(coinname, count = 7)
            for k in np.arange(0.1, 1.0, 0.1):
                df['range'] = (df['high'] - df['low']) * k
                df['target'] = df['open'] + df['range'].shift(1)
                fee = 0.0005
                df['ror'] = np.where(df['high'] > df['target'], df['close'] / df['target'] - fee, 1)
                ror = df['ror'].cumprod()[-2]
                print("%.1f %f" % (k, ror))
                listk.append(k)
                listper.append(ror) 
            bestk = round(10*listk[listper.index(max(listper))])/10

            if coinname != bestcoin:
                print("코인을 변경합니다. 이에 따라 기존 " + coinname2 + "를 모두 처분합니다.")
                btc = get_balance(coinname2)
                if btc * current_price > 5000:
                    sell_result = upbit.sell_market_order(coinname, btc*0.9995)
                    print("매도합니다."  + coinname +  str(sell_result))
                print("새로 거래할 코인은 " + bestcoin2 + "입니다.")
                coinname = bestcoin
                coinname2 = bestcoin[4:]
                pernum = bestper
                knum = bestk
                print("최적 k값을 " + str(knum) + "로 채택합니다.")
                print("예상수익률은 " + str(pernum - fee*2) + "입니다.")

            elif knum != bestk:
                print("최적 k값이 " + str(knum) + "에서 " + str(bestk) + "(으)로 변경되었습니다.")
                coinname = bestcoin
                coinname2 = bestcoin[4:]
                pernum = bestper
                knum = bestk
                print("거래할 코인은 " + coinname2 + "로 유지됩니다.")
                print("최적 k값을 " + str(knum) + "로 채택합니다.")
                print("예상수익률은 " + str(pernum - fee*2) + "입니다.")
            else:
                print("현 상태를 유지합니다.")
                coinname = bestcoin
                coinname2 = bestcoin[4:]
                pernum = bestper
                knum = bestk
                print("거래할 코인은 " + coinname2 + "입니다.")
                print("최적 k값을 " + str(knum) + "로 채택합니다.")
                print("예상수익률은 " + str(pernum - fee*2) + "입니다.")



        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1) 