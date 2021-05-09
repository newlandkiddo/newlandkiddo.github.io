''' 전일대비 상승률이 가장 최고인 코인을 변동성 돌파 전략으로 매수매도. 전일대비 상승률 1위가 바뀔 때마다 매도후 새로 매수함'''

''' 함수 정의 및 사전 설정 '''

import time
import pyupbit
import datetime
import numpy as np
import datetime

def get_target_price(ticker, k):
    # 변동성 돌파 전략으로 매수 목표가 설정
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    time.sleep(0.1)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_warning_price(ticker, k):
    # 변동성 돌파 전략으로 매도 목표가 설정
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    time.sleep(0.1)
    warning_price = df.iloc[0]['close'] - (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return warning_price

def get_ror(coin, k=0.5):
    #  k값별 수익률 구하는 백테스팅 
    df = pyupbit.get_ohlcv(coin, count = 7)
    time.sleep(0.1)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)
    fee = 0.0005
    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'] - fee,
                         1)
    ror = df['ror'].cumprod()[-2]
    return ror

def get_start_time(ticker):
    # 시작 시간 조회
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

''' 로그인 정보 입력'''
# access = ""
# secret = ""
access = "cmywD4HSiZ2hD89EurZglKbrWrsk5ylmNrPBKW8M"
secret = "SV1K5xsmgkVZjg4V5GkivMW6m5KUq7EisvxIBsdx"

''' 로그인 '''
upbit = pyupbit.Upbit(access, secret)
print("로그인 완료했습니다.")
fee = 0.0005

''' 잔고조회 '''
dictbalance = {}
balances = upbit.get_balances()
for b in balances:
    dictbalance[b['currency']] = b['balance']
krw = float(dictbalance["KRW"])
startmoney = krw
starttime = datetime.datetime.now()
print("잔고: " + str(dictbalance))

''' 코인 첫 구매 전까지 전일대비 상승률 최고인 코인과 최적 k값, 그리고 매수 목표가와 현재가를 비교한 후 매수하는 코드 반복'''
buy_total = 0
while True:

    while buy_total == 0:

        ''' 모든 코인 이름 가져오기 '''
        print("거래중인 모든 코인명을 불러옵니다.")
        markets = pyupbit.get_tickers()
        listcoin = []
        for market in markets:
            if 'KRW-' in market:
                listcoin.append(market)
        # print(listcoin)

        # 간단하게 테스트 할 때는 비트코인 하나만 사용
        # listcoin = ["KRW-BTC"]

        ''' 코인 현재가, 전날 종가, 전일대비 상승률 가져오기 '''
        print("모든 코인의 현재가, 전날 종가, 전일대비 상승률을 가져옵니다.")
        dictcoinsprice1 = {}
        dictcoinsyesper1 = {}

        for i in listcoin:
            # print(i)
            try:
                price = pyupbit.get_current_price(i) 
                time.sleep(0.1)
                dictcoinsprice1[i] = price
                # print(price)
                yesprice = pyupbit.get_ohlcv(i, count = 2)['close'][0]
                time.sleep(0.1)
                # print(yesprice)
                yesper = price / yesprice
                dictcoinsyesper1[i] = yesper
                
            except:
                dictcoinsprice1[i] = 0
                dictcoinsyesper1[i] = 0
                # print(0)
        # print(dictcoinsprice1)
        # print(dictcoinsyesper1)

        # pyupbit.get_ohlcv(i, count = 2)['close'][0]


        ''' 전일대비 상승률이 최고인 코인 선별하기 '''
        print("전일대비 상승률이 최고인 코인을 알아봅니다.")
        for coin, rate in dictcoinsyesper1.items():
            if rate == max(dictcoinsyesper1.values()):
                bestcoin1 = str(coin)
                bestcoinab1 = str(bestcoin1[4:])
        print("전일대비 상승률이 최고인 코인은 " + bestcoin1 + "입니다.")


        ''' 전일대비 상승률이 최고인 코인 k값 구하기 '''
        print("백테스팅으로 수익률이 최고인 k값을 구합니다.")
        listk = []
        listper = []

        for k in np.arange(0.1, 1.0, 0.1):
            ror = get_ror(bestcoin1, k)
            # print("%.1f %f" % (k, ror))
            listk.append(k)
            listper.append(ror) 
        bestror = max(listper)
        bestk = listk[listper.index(bestror)]
        print("최적 k값은 " + str(bestk) + "이고, 예상수익률은 " + str(bestror) + "입니다.")

        ''' 코인과 k값으로 매수, 매도하기 '''
        print("현재가와 매수목표가를 비교합니다.")
        target_price = get_target_price(bestcoin1, bestk)
        time.sleep(0.1)
        if target_price < pyupbit.get_current_price(bestcoin1):
            time.sleep(0.1)
            if krw >= 5000:
                buy_result = upbit.buy_market_order(bestcoin1, krw*(1-fee))
                #################### sell_result, buy_result는 dict의 key로 locked를 쓴다.
                time.sleep(5)
                print(buy_result)
                buy_total = float(buy_result['locked'])
                dictbalance = {}
                balances = upbit.get_balances()
                time.sleep(0.1)
                for b in balances:
                    dictbalance[b['currency']] = b['balance']
                buy_amount = float(dictbalance[bestcoinab1])
                buy_price = buy_total / buy_amount
                krw = float(dictbalance['KRW'])
                
                print(bestcoin1 + " " + str(buy_amount) + "을 " + str(buy_price) + "에 " + str(buy_total) + "원 매수했습니다. ")

                
            else: 
                print("KRW 잔액이 부족해 매수하지 않습니다.")
        else:
            print("현재가가 매수목표가보다 낮아 매수를 진행하지 않습니다.")

    ''' 1분마다 전일대비 최고 상승률인 코인 갱신하기 '''
    while buy_total != 0:
        # try:      
        print("현재시간은 " + str(datetime.datetime.now()) + "입니다.")
        print("전일대비 상승률이 최고인 코인을 업데이트 합니다.")
        # time.sleep(60)

        print("거래중인 모든 코인명을 불러옵니다.")
        markets = pyupbit.get_tickers()
        listcoin = []
        for market in markets:
            if 'KRW-' in market:
                listcoin.append(market)
        # print(listcoin)
        print("모든 코인의 현재가, 전날 종가, 전일대비 상승률을 가져옵니다.")
        dictcoinsprice2 = {}
        dictcoinsyesper2 = {}

        for i in listcoin:
            # print(i)
            try:
                price = pyupbit.get_current_price(i) 
                time.sleep(0.1)
                dictcoinsprice2[i] = price
                # print(price)
                yesprice = pyupbit.get_ohlcv(i, count = 2)['close'][0]
                time.sleep(0.1)
                # print(yesprice)1
                yesper = price / yesprice
                dictcoinsyesper2[i] = yesper
                
            except:
                dictcoinsprice2[i] = 0
                dictcoinsyesper2[i] = 0
                # print(0)
        # print(dictcoinsprice2)
        # print(dictcoinsyesper2)
        print("전일대비 상승률이 최고인 코인을 다시 검색합니다.")
        for coin, rate in dictcoinsyesper2.items():
            if rate == max(dictcoinsyesper2.values()):
                bestcoin2 = str(coin)
                bestcoinab2 = str(bestcoin2[4:])
        # print(bestcoin2)
        if bestcoin2 == bestcoin1:
            print("전일대비 최고 상승중인 코인이 " + bestcoin1 + "로 동일합니다.")
            fee = 0.0005
            currentprice = float(pyupbit.get_current_price(bestcoin1))
            time.sleep(0.1)
            print("현 상황을 유지합니다. 현재 수익률은 " + str(currentprice / buy_price - fee * 2) + "입니다.")
            rateac = (currentprice * buy_amount - startmoney) / startmoney - fee
            print(str(starttime) + "부터의 손익은 " + str(round(startmoney * rateac, 2)) + "이고, 누적수익률은 " + str(round(rateac * 100, 2)) + "%입니다.")
            if buy_price * 0.99 > pyupbit.get_current_price(bestcoin1):
                time.sleep(0.1)
                print("현재가가 1%이상 하락해 매도를 진행합니다.")
                if buy_amount * pyupbit.get_current_price(bestcoin1) >= 5000:
                    time.sleep(0.1)
                    sell_result = upbit.sell_market_order(bestcoin1, buy_amount)
                    time.sleep(5)
                    print(sell_result)
                    sell_amount = float(sell_result['locked'])
                    dictbalance = {}
                    balances = upbit.get_balances()
                    time.sleep(0.1)
                    for b in balances:
                        dictbalance[b['currency']] = b['balance']
                    krw = float(dictbalance['KRW'])
                    sell_price = krw / sell_amount
                    sell_total = krw
                    print(bestcoin1 + "을 " + str(sell_price) + "에 " + str(sell_total) + "원 매도했습니다.")
                    print("수익은 " + str(sell_total - buy_total) + "입니다.")
                    buy_total = 0

                    
                else:
                    print("코인 개수가 부족해 매도하지 않습니다.")

        elif bestcoin2 != bestcoin1:
            print("전일대비 상승중인 코인이 " + bestcoin2 + "로 변경되었습니다. 변경 후 유지되는지 1분동안 지켜봅니다.")
            time.sleep(60)
            dictcoinsprice3 = {}
            dictcoinsyesper3 = {}
            for i in listcoin:
                # print(i)
                try:
                    price = pyupbit.get_current_price(i) 
                    time.sleep(0.1)
                    dictcoinsprice2[i] = price
                    # print(price)
                    yesprice = pyupbit.get_ohlcv(i, count = 2)['close'][0]
                    time.sleep(0.1)
                    # print(yesprice)1
                    yesper = price / yesprice
                    dictcoinsyesper3[i] = yesper
                except:
                    dictcoinsprice3[i] = 0
                    dictcoinsyesper3[i] = 0
            for coin, rate in dictcoinsyesper3.items():
                if rate == max(dictcoinsyesper3.values()):
                    bestcoin3 = str(coin)
                    bestcoinab3 = str(bestcoin3[4:])
            if bestcoin2 == bestcoin3:
                print("전일대비 최고 상승중인 코인이 " + bestcoin2 + "로 변경 후 유지됩니다.")
                print(bestcoin1 + "을 매도하고, " + bestcoin2 + "를 매수합니다.")
                sell_price = pyupbit.get_current_price(bestcoin1)
                if buy_amount * pyupbit.get_current_price(bestcoin1) > 5000:
                    time.sleep(0.1)
                    sell_result = upbit.sell_market_order(bestcoin1, buy_amount)
                    time.sleep(5)
                    print(sell_result)
                    sell_amount = float(sell_result['locked'])
                    dictbalance = {}
                    balances = upbit.get_balances()
                    time.sleep(0.1)
                    for b in balances:
                        dictbalance[b['currency']] = b['balance']
                    krw = float(dictbalance['KRW'])
                    sell_price = krw / sell_amount
                    sell_total = krw
                    print(bestcoin1 + "을 " + str(sell_price) + "에 " + str(sell_total) + "원 매도했습니다.")
                    print("손익은 " + str(krw - buy_total) + "원입니다.")

                    print("백테스팅으로 수익률이 최고인 k값을 구합니다.")
                    listk = []
                    listper = []

                    for k in np.arange(0.1, 1.0, 0.1):
                        ror = get_ror(bestcoin2, k)
                        # print("%.1f %f" % (k, ror))
                        listk.append(k)
                        listper.append(ror) 
                    bestror = max(listper)
                    bestk = listk[listper.index(bestror)]
                    print("최적 k값은 " + str(bestk) + "이고, 예상수익률은 " + str(bestror) + "입니다.")
                    # print(bestk, bestror)        
                            
                    print("매수를 진행합니다.")
                    target_price = get_target_price(bestcoin2, bestk)
                    time.sleep(0.1)
                    if target_price < pyupbit.get_current_price(bestcoin2):
                        time.sleep(0.1)
                        print("현재가가 매수목표가보다 높게 설정되어 매수를 진행합니다.")
                        krw = float(dictbalance['KRW'])
                        if krw > 5000:
                            buy_result = upbit.buy_market_order(bestcoin2, krw*0.9995)
                            time.sleep(5)
                            print(buy_result)
                            buy_total = float(buy_result['locked'])
                            dictbalance = {}
                            balances = upbit.get_balances()
                            time.sleep(0.1)
                            for b in balances:
                                dictbalance[b['currency']] = b['balance']
                            buy_amount = float(dictbalance[bestcoinab2])
                            buy_price = buy_total / buy_amount
                            print(bestcoin2 + "을 " + str(buy_price) + "에 " + str(buy_total) + "원 매수했습니다. ")                
                            krw = float(dictbalance['KRW'])
                bestcoin1 = bestcoin2
            elif bestcoin2 != bestcoin3:
                print("전일대비 최고 상승중인 코인이 변경 후 유지되지 않아, 현 상태를 유지합니다.")

            



    # except:
    #     pass



