from __future__ import(absolute_import, division, print_function, unicode_literals)

import datetime
import os.path
import sys

import backtrader as bt

class TestStrategy(bt.Strategy):
        def log(self, txt, dt=None):
                dt = dt or self.datas[0].datetime.date(0)
                print('%s, %s' % (dt.isoformat(), txt))

        def __init__(self):
                self.dataclose = self.datas[0].close

        def next(self):
                self.log('Close, %.2f' % self.dataclose[0])

                if self.dataclose[0] < self.dataclose[-1]:
                        if self.dataclose[-1] < self.dataclose[-2]:
                                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                                self.buy()

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TestStrategy)

    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, '..\\backtrader\datas\orcl-1995-2014.txt')

    data = bt.feeds.YahooFinanceCSVData(dataname=datapath,
                                        fromdate=datetime.datetime(2000,1,1),
                                        todate=datetime.datetime(2000,12,31),
                                        reverse=False)

    cerebro.adddata(data)

    cerebro.broker.setcash(100000.0)
    print('Starting Portfolio value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio value: %.2f' % cerebro.broker.getvalue())