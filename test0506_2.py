''' 전일종가대비 최고 상승중인 코인을 거래. 현재가 기록 후의 값들을 비교해 매수-매도가 산정. 지정가 거래 '''

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

# 해당 코인의 구매호가 (내림)
def get_buyhopeprice(timeprice, getprice):
    if timeprice < 100:
        buyhopeprice = float(getprice) // 0.01 * 0.01
        return buyhopeprice
    elif timeprice < 1000:
        buyhopeprice = float(getprice) // 1 * 1
        return buyhopeprice
    elif timeprice < 10000:
        buyhopeprice = float(getprice) // 5 * 5
        return buyhopeprice
    elif timeprice < 50000:
        buyhopeprice = float(getprice) // 10 * 10
        return buyhopeprice
    elif timeprice < 100000:
        buyhopeprice = float(getprice) // 50 * 50
        return buyhopeprice
    elif timeprice < 500000:
        buyhopeprice = float(getprice) // 100 * 100
        return buyhopeprice
    elif timeprice < 1000000:
        buyhopeprice = float(getprice) // 500 * 500
        return buyhopeprice
    else:
        buyhopeprice = float(getprice) // 1000 * 1000
        return buyhopeprice

# 해당 코인의 매도 호가
def get_sellhopeprice(timeprice, getprice):
    if timeprice < 100:
        sellhopeprice = (float(getprice) // 0.01 + 1) * 0.01
        return sellhopeprice
    elif timeprice < 1000:
        sellhopeprice = (float(getprice) // 1 + 1) * 1
        return sellhopeprice
    elif timeprice < 10000:
        sellhopeprice = (float(getprice) // 5 + 1) * 5
        return sellhopeprice
    elif timeprice < 50000:
        sellhopeprice = (float(getprice) // 10 + 1) * 10
        return sellhopeprice
    elif timeprice < 100000:
        sellhopeprice = (float(getprice) // 50 + 1) * 50
        return sellhopeprice
    elif timeprice < 500000:
        sellhopeprice = (float(getprice) // 100 + 1) * 100
        return sellhopeprice
    elif timeprice < 1000000:
        sellhopeprice = (float(getprice) // 500 + 1) * 500
        return sellhopeprice
    else:
        sellhopeprice = (float(getprice) // 1000 + 1) * 1000
        return sellhopeprice

# 해당 코인의 구매가능 갯수
def get_buyhopeamount(buyhopeprice, krw):
    hopeamount = round(float(krw) / float(buyhopeprice), 8) - 0.00000001
    return hopeamount
    


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
        targetprice = float(minprice) * 1.005
        if targetprice <= timeprice:
            buyhopeprice = get_buyhopeprice(timeprice, targetprice * 1.005)
            buyhopeamount = get_buyhopeamount(buyhopeprice, float(krw) * (1 - float(fee)))
            print(bestcoin + "을 " + str(buyhopeprice) + "에 지정가 매수를 주문합니다.")
            buy_result = upbit.buy_limit_order(bestcoin, buyhopeprice, buyhopeamount)
            buy_amount = 0
            while buy_amount == 0:   
                try:
                    dictbalance = get_dictbalance()
                    buy_amount = float(dictbalance[bestcoinab])
                except KeyError:
                    buy_amount = 0
            buy_total = (float(krw) - float(dictbalance['KRW'])) * 0.9995
            krw = dictbalance['KRW']
            buy_price = float(buy_total) / float(buy_amount)
            print("매수체결: " + bestcoin + " / 가격: " + str(round(buy_price)) + " / 수량: " + str(round(buy_amount, 2)) + " / 금액: " + str(round(buy_total)))
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
        warningprice = float(maxprice) * 0.995
        if warningprice >= timeprice:    
            sellhopeprice = get_sellhopeprice(timeprice, warningprice*0.995)
            sellhopeamount = buy_amount
            print(bestcoin + "을 " + str(sellhopeprice) + "에 지정가 매도를 주문합니다.")
            sell_result = upbit.sell_limit_order(bestcoin, sellhopeprice, sellhopeamount)
            crypt_amount = buy_amount
            while True:   
                dictbalance = get_dictbalance()
                try:
                    crypt_amount = dictbalance[bestcoinab]
                except:
                    crypt_amount = 0
                    pass
                if crypt_amount == 0:
                    break
            sell_amount = buy_amount
            sell_total = float(dictbalance['KRW']) - float(krw)
            sell_price = float(sell_total) / float(sell_amount)
            print("매도체결: " + bestcoin + " / 가격: " + str(round(sell_price)) + " / 수량: " + str(round(sell_amount, 2)) + " / 금액: " + str(round(sell_total)))
            krw = dictbalance['KRW']    
            rate = float(sell_total) / float(buy_total)
            rateac = float(rateac) * float(rate)
            print("매매손익 : " + str(round(float(sell_total) - float(buy_total) ,2)) + "원 / 매매수익률 : " + str(round(float(rate) * 100 - 100, 2)) + "%")
            print(str(starttime) + "부터의 누적손익 : " + str(round(float(krw) - float(startmoney), 2)) + " / 누적수익률 : " + str(round(float(rateac) * 100 - 100, 2)) + "%")
            break
    
    
    
    
    
    






