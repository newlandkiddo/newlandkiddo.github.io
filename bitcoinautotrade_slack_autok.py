import time
import pyupbit
import datetime
import requests

access = "cmywD4HSiZ2hD89EurZglKbrWrsk5ylmNrPBKW8M"
secret = "SV1K5xsmgkVZjg4V5GkivMW6m5KUq7EisvxIBsdx"
myToken = "xoxb-1999106260742-2006115860355-QZp7pDEJqfcMSBKar8AxG2CF"

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_warning_price(ticker, k):
    """변동성 돌파 전략으로 매도 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    warning_price = df.iloc[0]['close'] - (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return warning_price

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

# 최적 k값 찾기 함수 정의
import pyupbit
import numpy as np


def get_ror(k=0.5):
    df = pyupbit.get_ohlcv("KRW-BTC", count = 7)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    fee = 0.0005
    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'] - fee,
                         1)

    ror = df['ror'].cumprod()[-2]
    return ror


# 로그인
upbit = pyupbit.Upbit(access, secret)
print("로그인 완료했습니다.")
# 시작 메세지 슬랙 전송
post_message(myToken,"#crypto", "로그인 완료했습니다.")

# 현재 최적 k값 찾기
listk = []
listper = []

for k in np.arange(0.1, 1.0, 0.1):
    ror = get_ror(k)
    print("%.1f %f" % (k, ror))
    listk.append(k)
    listper.append(ror) 
bestk = listk[listper.index(max(listper))]
print("최적 k값을 찾았습니다. k =", bestk)


# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time + datetime.timedelta(seconds=10) < now < end_time:
            print("자동 매매 프로그램을 시작합니다.")
            target_price = get_target_price("KRW-BTC", bestk)
            current_price = get_current_price("KRW-BTC")
            warning_price = get_warning_price("KRW-BTC", bestk)
            if target_price < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    buy_result = upbit.buy_market_order("KRW-BTC", krw*0.9995)
                    post_message(myToken,"#crypto", "BTC buy : " +str(buy_result))
                    print("매수합니다. BTC ", buy_result)
            elif warning_price > current_price:
                btc = get_balance("BTC")
                if btc > 0.00008:
                    sell_result = upbit.sell_market_order("KRW-BTC", btc*0.9995)
                    post_message(myToken,"#crypto", "BTC buy : " +str(sell_result))
                    print("매도합니다. BTC ", sell_result)
        
# 9시에 최적 k값 찾기
        else: 
            print("최적 k값을 다시 찾습니다.")
            listk = []
            listper = []

            for k in np.arange(0.1, 1.0, 0.1):
                ror = get_ror(k)
                print("%.1f %f" % (k, ror))
                listk.append(k)
                listper.append(ror) 
            bestk = listk[listper.index(max(listper))]
            print(bestk)
#           btc = get_balance("BTC")
#            if btc > 0.00008:
#                upbit.sell_market_order("KRW-BTC", btc*0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)