__author__ = 'lottiwang'
import tushare as ts
import talib as ta
import matplotlib.pyplot as plt
from futuquant.open_context import *
import datetime
import numpy as np
import pandas as pb
import matplotlib.dates as mdate
import matplotlib.ticker as ticker
import threading
import  time
from WhiteGuardStock import WhiteGuardStockCore

TRADE_ENV = 1
TRADA_ACTION_BUY=0
TRADA_ACTION_SELL=1
test_mode = True
LOCK_PASS= '851226'
TIME_K = 15
class AutoFutuTrade:
    def __init__(self):
        #self.quote_ctx = OpenQuoteContext(api_ip, api_port)
        self.wgs= WhiteGuardStockCore()
        self.last_buy_point = 0;
        self.last_sell_point = 0;
        pass


    def start_trade(self,stock_id):
        self.trade_code = stock_id
        self.timer = threading.Timer(3.0, self.auto_trade, [stock_id])
        self.timer.start()

    #测试用的函数
    def auto_trade(self,stock_id):
        #print("hello %s" % name)
        df=self.wgs.get_stock_dmi_my_signal_min(self.trade_code,TIME_K)
        #print(df)
        #df.to_csv("data/dmi.csv")
        #在这里决策要不要买,粗暴点，AAJ小于多少才买,且算AJJ是不是出了底部拐点。

        minaaj = ta.MIN(df['AAJ'].values[:-1], timeperiod=12)[-1]
        minaaj_index = ta.MININDEX(df['AAJ'].values[:-1], timeperiod=12)[-1]
        #print(minaaj,minaaj_index,df.iat[-1,-1],stock_id)
        #最新的AAJ小于0，且大于低谷，并且低谷就是近一段时间的最低值，确认反转
        if df.iat[-1,-1] < 0 and df.iat[-2,-1] < df.iat[-1,-1] and df.iat[-2,-1] == minaaj and minaaj != self.last_buy_point:
        #if test_mode == True:
             print("[%s] [%s] 触发买入条件,AAJ为%s 索引为%d"%(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())),stock_id,df.iat[-1,-1],minaaj_index))
             self.make_buy_order(LOCK_PASS,stock_id,TRADE_ENV,TRADA_ACTION_BUY)
             self.last_buy_point = minaaj
        # #在这里决策要不要买卖,粗暴点，把持仓扫一遍
        #if df.iat[-1,-1] > 0 and df.iat[-2,-1] > df.iat[-1,-1]:
        self.make_sell_order(LOCK_PASS,TRADE_ENV,TRADA_ACTION_SELL)
        self.timer = threading.Timer(3.0, self.auto_trade, [stock_id])
        self.timer.start()


    def make_buy_order(self,unlock_password, stock_id, trade_env,order_side):
        self.wgs.open_trade_make_order(unlock_password, stock_id, trade_env,order_side,1)


    def make_sell_order(self,unlock_password,trade_env,order_side):
        df = self.wgs.get_current_position_list(TRADE_ENV)
        for i in range(0, len(df)):
            if int(df.iloc[i]['can_sell_qty']) > 0:
                df_dmi = self.wgs.get_stock_dmi_my_signal_min(df.iloc[i]['code'],TIME_K)
                maxaaj = ta.MAX(df_dmi['AAJ'].values[:-1], timeperiod=12)[-1]
                maxaaj_index = ta.MAXINDEX(df_dmi['AAJ'].values[:-1], timeperiod=12)[-1]
                #print(maxaaj,maxaaj_index,df_dmi.iat[-1,-1],df.iloc[i]['code'])
                if df_dmi.iat[-1,-1] > 0 and df_dmi.iat[-2,-1] > df_dmi.iat[-1,-1] and df_dmi.iat[-2,-1] == maxaaj and self.last_sell_point != maxaaj: #AAJ大于多少卖出,且算AJJ是不是出了顶部拐点。
                    print("[%s] [%s] 触发卖出条件,AAJ为%s 索引为%d"%(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())),df.iloc[i]['code'],df_dmi.iat[-1,-1],maxaaj_index))
                    self.wgs.open_trade_make_order(LOCK_PASS,df.iloc[i]['code'],trade_env,order_side,1)
                    self.last_sell_point = maxaaj
            #print(df_dmi)
        #self.wgs.open_trade_make_order(unlock_password, stock_id, trade_env,order_side)

    def clear(self):
        self.wgs.clear_quote()




if __name__ == "__main__":
    aft = AutoFutuTrade()
    aft.wgs.start_hk_market(TRADE_ENV)
    aft.start_trade('HK.02382')


