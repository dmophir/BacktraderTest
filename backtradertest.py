from __future__ import(absolute_import, division, print_function, unicode_literals)

import datetime
import os.path
import sys

import backtrader as bt

# Create a Strategy
class TestStrategy(bt.Strategy):
        params = (
                ('maperiod', 15),
                ('printlog', False),
        )
        def log(self, txt, dt=None):
                # Logging function for this strategy
                dt = dt or self.datas[0].datetime.date(0)
                print('%s, %s' % (dt.isoformat(), txt))

        def __init__(self):
                # Keep a reference to the 'close' line in the data[0] dataseries
                self.dataclose = self.datas[0].close

                # Keep track of pending orders and buy price/commission
                self.order = None
                self.buyprice = None
                self.buycomm = None

                # MovingSimpleAverage indicator
                self.sma = bt.indicators.SimpleMovingAverage(
                        self.datas[0], period=self.params.maperiod)

                # Indicators for the plotting show
                bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
                bt.indicators.WeightedMovingAverage(self.datas[0], period=25,
                                                    subplot=True)
                bt.indicators.StochasticSlow(self.datas[0])
                bt.indicators.MACDHisto(self.datas[0])
                rsi = bt.indicators.RSI(self.datas[0])
                bt.indicators.SmoothedMovingAverage(rsi, period=10)
                bt.indicators.ATR(self.datas[0], plot=False)

        def notify_order(self, order):
                if order.status in [order.Submitted, order.Accepted]:
                        # Buy/Sell order submitted/accepted to/by broker - Nothing to do
                        return

                # Check if an order has been completed
                # Attention: broker could reject order if not enough cash
                if order.status in [order.Completed]:
                        if order.isbuy():
                                self.log(
                                        'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                                        (order.executed.price,
                                         order.executed.value,
                                         order.executed.comm))
                                self.buyprice = order.executed.price
                                self.buycomm = order.executed.comm
                        else:  # Sell
                                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                                         (order.executed.price,
                                          order.executed.value,
                                          order.executed.comm))

                        self.bar_executed = len(self)

                elif order.status in [order.Canceled, order.Margin, order.Rejected]:
                        self.log('Order Canceled/Margin/Rejected')

                # Log no pending order
                self.order = None

        def notify_trade(self, trade):
                if not trade.isclosed:
                        return

                self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                         (trade.pnl, trade.pnlcomm))

        def next(self):
                # Log closing price of the series from reference
                self.log('Close, %.2f' % self.dataclose[0])

                # Check if an order is pending to prevent double orders
                if self.order:
                        return

                # Check if we are in the market
                if not self.position:

                        # If not, then maybe if...
                        if self.dataclose[0] > self.sma[0]:

                                # Buy with default params
                                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                                # Track created order to prevent duplicates
                                self.order = self.buy()
                else:
                        if self.dataclose[0] < self.sma[0]:

                                # Sell with default params
                                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                                # Track created order to prevent duplicates
                                self.order = self.sell()

if __name__ == '__main__':
        # Instantiate cerebro object
        cerebro = bt.Cerebro()

        # Give cerebro strategy
        cerebro.addstrategy(TestStrategy)

        # Datas are in a subfolder of the samples. Need to find where the script is
        # because it could have been called from anywhere
        modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
        datapath = os.path.join(modpath, '..\\backtrader\datas\orcl-1995-2014.txt')

        # Create a Data Feed
        data = bt.feeds.YahooFinanceCSVData(dataname=datapath,
                                        fromdate=datetime.datetime(2000, 1, 1),
                                        todate=datetime.datetime(2000, 12, 31),
                                        reverse=False)

        # Feed cerebro data feed
        cerebro.adddata(data)

        # set starting cash
        cerebro.broker.setcash(1000.0)

        # Add a FixedSize sizer according to the stake
        cerebro.addsizer(bt.sizers.FixedSize, stake=10)

        # Set commission rate
        cerebro.broker.setcommission(commission=0.0)

        # Print our starting conditions
        print('Starting Portfolio value: %.2f' % cerebro.broker.getvalue())

        # Run through data feed
        cerebro.run()

        # Print final results
        print('Final Portfolio value: %.2f' % cerebro.broker.getvalue())

        # Plot results
        cerebro.plot()