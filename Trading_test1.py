import urllib
import urllib2
import json
import time
import hmac,hashlib
import requests
import sys
import hmac
import httplib

api_key = 'API_KEYS'
api_secret = 'SECRET_API_KEYS'
api_key_e = 'API_KEYS'
api_secret_e = 'SECRET_API_KEYS'
save = ''

#btc-e stuff
def trade(bORs,xrate,hm):#put pair for ltc
    nonce = int(round(time.time()-1461691111)*10)
    parms = {"method":"Trade",
             "pair":"ltc_btc",
             "type":bORs,
             "rate":xrate,
             "amount":hm,
             "nonce":nonce
             }
    parms = urllib.urlencode(parms)
    hashed = hmac.new(api_secret_e,digestmod=hashlib.sha512)
    hashed.update(parms)
    signature = hashed.hexdigest()

    headers = {"Content-type":"application/x-www-form-urlencoded",
               "Key":api_key_e,
               "Sign":signature}

    conn = httplib.HTTPSConnection("btc-e.com")
    conn.request("POST","/tapi",parms,headers)

    response = conn.getresponse()
    print(response.status, response.reason)

    resp = json.load(response)
    print (resp)

#nothin
def createTimeStamp(datestr, format="%Y-%m-%d %H:%M:%S"):
    return time.mktime(time.strptime(datestr, format))

#Poloniex stuff
class poloniex:
    def __init__(self, APIKey, Secret):
        self.APIKey = APIKey
        self.Secret = Secret

    def post_process(self, before):
        after = before

        # Add timestamps if there isnt one but is a datetime
        if('return' in after):
            if(isinstance(after['return'], list)):
                for x in xrange(0, len(after['return'])):
                    if(isinstance(after['return'][x], dict)):
                        if('datetime' in after['return'][x] and 'timestamp' not in after['return'][x]):
                            after['return'][x]['timestamp'] = float(createTimeStamp(after['return'][x]['datetime']))
                            
        return after
    
    #non-test
    def api_query(self, command, req={}):

        if(command == "returnTicker" or command == "return24Volume"):
            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + command))
            return json.loads(ret.read())
        elif(command == "returnOrderBook"):
            ret = urllib2.urlopen(urllib2.Request('http://poloniex.com/public?command=' + command + '&currencyPair=' + str(req['currencyPair'])))
            return json.loads(ret.read())
        elif(command == "returnMarketTradeHistory"):
            ret = urllib2.urlopen(urllib2.Request('http://poloniex.com/public?command=' + "returnTradeHistory" + '&currencyPair=' + str(req['currencyPair'])))
            return json.loads(ret.read())
        else:
            req['command'] = command
            req['nonce'] = int(time.time()*1000)
            post_data = urllib.urlencode(req)

            sign = hmac.new(self.Secret, post_data, hashlib.sha512).hexdigest()
            headers = {
                'Sign': sign,
                'Key': self.APIKey
            }

            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/tradingApi', post_data, headers))
            jsonRet = json.loads(ret.read())
            print ("this is jsonRet : " + str(jsonRet))
            global save
            save = jsonRet
            return self.post_process(jsonRet)


    def returnTicker(self):
        return self.api_query("returnTicker")

    def return24Volume(self):
        return self.api_query("return24Volume")

    def returnOrderBook (self, currencyPair):
        return self.api_query("returnOrderBook", {'currencyPair': currencyPair})

    def returnMarketTradeHistory (self, currencyPair):
        return self.api_query("returnMarketTradeHistory", {'currencyPair': currencyPair})


    # Returns all of your balances.
    # Outputs: 
    # {"BTC":"0.59098578","LTC":"3.31117268", ... }
    def returnBalances(self):
        return self.api_query('returnBalances')

    # Returns your open orders for a given market, specified by the "currencyPair" POST parameter, e.g. "BTC_XCP"
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs: 
    # orderNumber   The order number
    # type          sell or buy
    # rate          Price the order is selling or buying at
    # Amount        Quantity of order
    # total         Total value of order (price * quantity)
    def returnOpenOrders(self,currencyPair):
        return self.api_query('returnOpenOrders',{"currencyPair":currencyPair})


    # Returns your trade history for a given market, specified by the "currencyPair" POST parameter
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs: 
    # date          Date in the form: "2014-02-19 03:44:59"
    # rate          Price the order is selling or buying at
    # amount        Quantity of order
    # total         Total value of order (price * quantity)
    # type          sell or buy
    def returnTradeHistory(self,currencyPair):
        return self.api_query('returnTradeHistory',{"currencyPair":currencyPair})

    # Places a buy order in a given market. Required POST parameters are "currencyPair", "rate", and "amount". If successful, the method will return the order number.
    # Inputs:
    # currencyPair  The curreny pair
    # rate          price the order is buying at
    # amount        Amount of coins to buy
    # Outputs: 
    # orderNumber   The order number
    def buy(self,currencyPair,rate,amount):
        return self.api_query('buy',{"currencyPair":currencyPair,"rate":rate,"amount":amount})

    # Places a sell order in a given market. Required POST parameters are "currencyPair", "rate", and "amount". If successful, the method will return the order number.
    # Inputs:
    # currencyPair  The curreny pair
    # rate          price the order is selling at
    # amount        Amount of coins to sell
    # Outputs: 
    # orderNumber   The order number
    def sell(self,currencyPair,rate,amount):
        return self.api_query('sell',{"currencyPair":currencyPair,"rate":rate,"amount":amount})

    # Cancels an order you have placed in a given market. Required POST parameters are "currencyPair" and "orderNumber".
    # Inputs:
    # currencyPair  The curreny pair
    # orderNumber   The order number to cancel
    # Outputs: 
    # succes        1 or 0
    def cancel(self,currencyPair,orderNumber):
        return self.api_query('cancelOrder',{"currencyPair":currencyPair,"orderNumber":orderNumber})

    # Immediately places a withdrawal for a given currency, with no email confirmation. In order to use this method, the withdrawal privilege must be enabled for your API key. Required POST parameters are "currency", "amount", and "address". Sample output: {"response":"Withdrew 2398 NXT."} 
    # Inputs:
    # currency      The currency to withdraw
    # amount        The amount of this coin to withdraw
    # address       The withdrawal address
    # Outputs: 
    # response      Text containing message about the withdrawal
    def withdraw(self, currency, amount, address):
        return self.api_query('withdraw',{"currency":currency, "amount":amount, "address":address})

#start

x = poloniex(api_key,api_secret)

#print (x.returnBalances()['DOGE'])
#selltrade = x.sell("BTC_DOGE",0.00000090,449.43157638)
#print(selltrade)

##volume
#polo data
url = 'https://poloniex.com/public?command=returnTicker'
json_obj = urllib2.urlopen(url)
data = json.load(json_obj)
#btc-e data
urls = 'https://btc-e.com/api/3/depth/ltc_btc'
json_objs = urllib2.urlopen(urls)
datas = json.load(json_objs)

#polo bids
highest_bid = data['BTC_LTC']['highestBid']
print(highest_bid)
polo_sell = x.returnOrderBook("BTC_LTC")['bids'][0][1]
print("(sell)Highest bid Polo volume is : " + str(polo_sell))

#polo ask
lowest_ask = data['BTC_LTC']['lowestAsk']
print(lowest_ask)
polo_buy = x.returnOrderBook("BTC_LTC")['asks'][0][1]
print("(buy)Lowest Ask Polo volume is : " + str(polo_buy))

#btc-e bid
highest_bids = datas['ltc_btc']['bids']
#print(highest_bids[0][0])
btc_sell = highest_bids[0][1]
print("(sell)Highest bid btc-e volume is : " + str(btc_sell))

#btc-e ask
lowest_asks = datas['ltc_btc']['asks']
#print(lowest_asks)
btc_buy = lowest_asks[0][1]
print("(buy)Lowest Ask btc-e volume is : " + str(btc_buy))

#################
#User Input here#
#################
satoshi = '0.00000020'
amount = '800.00000000'


#Start main stuff
while(True):
    while (True):
        #while loop check time delay
        start_time = time.time()
        
        #polo data
        url = 'https://poloniex.com/public?command=returnTicker'
        json_obj = urllib2.urlopen(url)
        data = json.load(json_obj)
        #print(data['BTC_LTC'])
        #print("Polo HIGH price : "+str(data['BTC_LTC']['lowestAsk']))
        #print("Polo LOW price : "+str(data['BTC_LTC']['highestBid']))
        polo_high = float(data['BTC_LTC']['lowestAsk'])
        polo_low = float(data['BTC_LTC']['highestBid'])

        #ltc btc-e data output
        url = 'https://btc-e.com/api/3/ticker/ltc_btc'
        json_obj = urllib2.urlopen(url)
        data = json.load(json_obj)
        #print("BTC-e HIGH price : "+str(data['ltc_btc']['buy']))
        #print("BTC-e LOW price : "+str(data['ltc_btc']['sell']))
        btc_high = float(data['ltc_btc']['buy'])
        btc_low = float(data['ltc_btc']['sell'])

        #calculation
        profit_check1 = round(((btc_low/polo_high)*100)-100,2)  
        profit_check2 = round(((polo_low/btc_high)*100)-100,2)

        count = 0
        #check profit
        if (polo_high < btc_low and profit_check1 > 1.50): #change to 1 later
            print ("TRADING OPPORTUNITY : buy from polo sell to btc-e. profit is : " +
                   str(profit_check1) + " %")
            count = 1
            break
        if (btc_high < polo_low and profit_check2 > 1.50): #change to 1 later
            print ("TRADING OPPORTUNITY : buy from btc-e sell to polo. profit is : " +
                   str(profit_check2) + " %")
            count = 2
            break
        if (count == 0):
            print ("NO OPPORTUNITY or less than 1.50%")
            #if (profit_check1 > 0):
            print(profit_check1)
            #if (profit_check2 > 0):
            print (profit_check2)
            time.sleep(6)
            ddengle = 1
        #if (count != 0):

        #time elapsed
        nu = 0
        if (ddengle == 1):
            nu = 6
        elapsed = time.time() - start_time - nu
        print("Current Time Delay check : %.3f" % elapsed)
        
        #time.sleep(3)

    #Engage in Trading
    print ("Sieze Opportunity -> engage in Trading")
    #buy from polo
    if (count == 1):
        if (min(btc_sell,polo_buy) > 5):
            x.buy("BTC_LTC",lowest_ask,0.1)
            print("just bought LTC from polo")
        else:
            print("Sorry, volume less than 5LTC. too dangerous")
            break
    #buy from btc-e
    if (count == 2):
        if (min(btc_buy,polo_sell) > 5):
            trade('buy',lowest_asks[0][0],0.1)
            print("just bought LTC from btc-e")
        else:
            print("Sorry, volume less than 5LTC. too dangerous")
            break

    #save['resultingTrades'] = [{u'tradeID': u'734709', u'rate': u'0.00000049', u'amount': u'430.43157638', u'date': u'2016-04-27 21:16:29', u'total': u'0.00021091', u'type': u'sell'}]
    #print(save)
    if (count == 1):
        #success trade stage 1
        if (save['resultingTrades'] != []):
            print("resulting trade is null")
            break

        #fail trade stage 1
        if (save['resultingTrades'] == []):
            print ("no resulting trades")
            print ("canceling order")
            x.cancel("BTC_LTC",save['orderNumber'])

            if (save['success'] == 0 ):
                print ("Cancelling unsuccessful... Terminating")
                print (save)
                sys.exit("some error message FIX IT")

            if (save['success'] == 1 and save['amount'] == amount) :
                print ("canceling successful")
                time.sleep(6)
    #sell to btc-e
    if (count == 1):
        trade('sell',highest_bids[0][0],0.1)
        print("sell to btc-e")
        break
    #sell to polo
    if (count == 2):
        x.sell("BTC_LTC",lowest_ask,0.1)
        print("sell to polo")
        break

    
        
#try:
#    print (save['orderNumber'])
#except KeyError:
#    print ("error")
elapsed = time.time() - start_time
print("Current Time Delay check : %.3f" % elapsed)



    
# 

