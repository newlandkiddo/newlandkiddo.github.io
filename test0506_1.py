''' 전일종가대비 최고 상승중인 코인을 거래. 현재가 기록 후의 값들을 비교해 매수-매도가 산정. 시장가 거래.'''

''' 함수 정의 '''
import time
import pyupbit
import datetime

# 전체 잔고조회
def get_dictbalance():
    dict1 = {}
    balances = upbit.get_balances()
    time.sleep(0.06)
    for b in balances:
        dict1[b['currency']] = b['balance']
    return dict1

# 거래소에 등록된 코인명 모두 가져오기
def get_listcoin():
    markets = pyupbit.get_tickers()
    list1 = []
    for market in markets:
        if 'KRW-' in market:
            list1.append(market)
    return list1

# 해당 코인의 현재가 가져오기
def get_current(coin):
    price = pyupbit.get_current_price(coin)
    time.sleep(0.06) 
    return price

# 해당 코인의 전날 종가 가져오기
def get_close(coin):
    price = pyupbit.get_ohlcv(coin, count = 2)['close'][0]
    time.sleep(0.06)
    return price

# 해당 코인의 전날 종가



''' 로그인 및 수수료 등 기타 정보 입력'''
# access = ""
# secret = ""
access = "cmywD4HSiZ2hD89EurZglKbrWrsk5ylmNrPBKW8M"
secret = "SV1K5xsmgkVZjg4V5GkivMW6m5KUq7EisvxIBsdx"
fee = 0.0005



''' 로그인 '''
upbit = pyupbit.Upbit(access, secret)
print("로그인 완료했습니다.")



''' 잔고조회 '''
dictbalance = get_dictbalance()
krw = float(dictbalance["KRW"])
startmoney = krw
starttime = datetime.datetime.now()
rateac = 1
print("잔고: " + str(dictbalance))



''' 모든 코인 이름 가져오기 '''
print("거래중인 모든 코인명을 불러옵니다.")
listcoin = get_listcoin()
# print(listcoin)



''' 모든 코인의 전날 종가 가져오기 '''
print("모든 코인의 전날 종가를 불러웁니다.")
dictclose = {}
for i in listcoin:
    dictclose[i] = get_close(i)
# print(dictclose)



''' 매수 매도 반복문 시작 '''
while True:
    ''' 모든 코인의 현재가 가져와서 전일대비 상승비율 계산 후 최고 상승중인 코인 이름 출력하기 '''
    print("모든 코인의 현재가를 불러옵니다.")
    dictcurrent = {}
    for i in listcoin:
        dictcurrent[i] = get_current(i)
    # print(dictcurrent)
    print("전일대비 최고 상승중인 코인을 검색합니다.")
    dictrate = {}
    for i in listcoin:
        dictrate[i] = dictcurrent[i] / dictclose[i]
    # print(dictrate)
    for coin, rate in dictrate.items():
        if rate == max(dictrate.values()):
            bestcoin = coin
            bestcoinab = bestcoin[4:]
    print("거래할 코인: " + bestcoin)

    ''' 매수를 위한 현재가 기록 시작 '''
    print("매수를 위해 현재가 기록을 시작합니다.")
    listavg = []
    dictrecord = {}
    while True:
        listrecord = []
        for i in range(1,11):
            timeprice = get_current(bestcoin)
            listrecord.append(timeprice)
        listrecord.remove(max(listrecord))
        listrecord.remove(max(listrecord))
        listrecord.remove(min(listrecord))
        listrecord.remove(min(listrecord))
        # print(listrecord)
        avgprice = float(sum(listrecord)) / float(len(listrecord))
        listavg.append(avgprice)
        dictrecord['min'] = min(listavg)
        minprice = dictrecord['min']
        # print(avgprice, dictrecord)

        ''' 매수목표가 설정 및 매수 주문'''
        targetprice = minprice * 1.01
        if targetprice <= timeprice:
            buy_result = upbit.buy_market_order(bestcoin, krw*(1-fee))
            buy_amount = 0
            while buy_amount == 0:   
                try:
                    dictbalance = get_dictbalance()
                    buy_amount = float(dictbalance[bestcoinab])
                except KeyError:
                    buy_amount = 0
            buy_price = float(timeprice)
            buy_total = float(buy_amount * buy_price)
            print("매수: " + bestcoin + " / 가격: " + str(buy_price) + " / 수량: " + str(round(buy_amount, 2)) + " / 금액: " + str(round(buy_total, 2)))
            break



    ''' 매도를 위한 현재가 기록 시작 '''
    print("매도를 위해 현재가 기록을 시작합니다.")
    listavg = []
    dictrecord = {}
    while True:
        listrecord = []
        for i in range(1,11):
            timeprice = get_current(bestcoin)
            listrecord.append(timeprice)
        listrecord.remove(max(listrecord))
        listrecord.remove(max(listrecord))
        listrecord.remove(min(listrecord))
        listrecord.remove(min(listrecord))
        # print(listrecord)
        avgprice = float(sum(listrecord)) / float(len(listrecord))
        listavg.append(avgprice)
        dictrecord['max'] = max(listavg)
        maxprice = dictrecord['max']
        # print(avgprice, dictrecord)

        ''' 매도목표가 설정 및 매도 주문'''
        warningprice = maxprice * 0.99
        if warningprice >= timeprice:    
            sell_result = upbit.sell_market_order(bestcoin, buy_amount)
            sell_total = 0
            while sell_total <= 5000:   
                try:
                    dictbalance = get_dictbalance()
                    sell_total = float(dictbalance['KRW'])
                except KeyError:
                    sell_total = 0
            sell_price = float(sell_total) / float(buy_amount)
            sell_amount = float(sell_total) / float(sell_price)
            print("매도: " + bestcoin + " / 가격: " + str(sell_price) + " / 수량: " + str(round(sell_amount, 2)) + " / 금액: " + str(round(sell_total, 2)))
            krw = float(sell_total)        
            rate = krw / buy_total
            rateac = rateac * rate
            print("손익 : " + str(round(krw - buy_total ,2)) + "원 / 수익률 : " + str(round(rate * 100 - 100, 2)) + "%")
            print(str(starttime) + "부터의 누적손익 : " + str(round(krw - startmoney, 2)) + " / 누적수익률 : " + str(round(rateac * 100 - 100, 2)) + "%")
            break
    
    
    
    
    
    






