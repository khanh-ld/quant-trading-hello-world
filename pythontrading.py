import pandas_datareader as pdr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

# Test GET API
aapl = pdr.get_data_yahoo('AAPL', start=datetime.datetime(2006, 10, 1), end = datetime.datetime(2012, 1, 1))

# Define a function that helps to get a ticker's data from start date to end date
def get(tickers, startdate, enddate):
    def data(ticker):
        return(pdr.get_data_yahoo(ticker, start=startdate, end=enddate))
    datas = map(data, tickers)
    return(pd.concat(datas, keys=tickers, names=['Ticker','Date']))
tickers = ['AAPL','MSFT','IBM','GOOG']
all_data = get(tickers, datetime.datetime(2006, 10, 1), datetime.datetime(2012, 1, 1))

# Initialize the short and long windows
short_window = 40
long_window = 100

# Initialize a signal DataFrame with a signal column
signals = pd.DataFrame(index=aapl.index)
signals['signal'] = 0.0

# Create a short simple moving average over the short window
signals['short_mavg'] = aapl['Close'].rolling(window=short_window, min_periods=1, center=False).mean()

# Create a long simple moving average over the long window
signals['long_mavg'] = aapl['Close'].rolling(window=long_window, min_periods=1, center=False).mean()

# Create signals
signals['signal'][short_window:] = np.where(signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1.0, 0.0)

# Generate trading orders
signals['positions'] = signals['signal'].diff()

# Initialize the plot figure
fig = plt.figure()

# Add a subplot and label for y-axis
ax1 = fig.add_subplot(111, ylabel='Price in $')

# Plot the closing price
aapl['Close'].plot(ax=ax1, color='r', lw=2.)

# Plot the short and long moving averages
signals[['short_mavg', 'long_mavg']].plot(ax=ax1, lw=2.)

# Plot the buy signals
ax1.plot(signals.loc[signals.positions ==1.0].index, signals.short_mavg[signals.positions==1.0], '^', markersize=10, color='m')

# Plot the sell signals
ax1.plot(signals.loc[signals.positions ==-1.0].index, signals.short_mavg[signals.positions==-1.0], 'v', markersize=10, color='k')

plt.show()

# Set the initial capital
initial_capital=float(100000.0)

# Create a DataFrame 'positions'
positions = pd.DataFrame(index=signals.index).fillna(0.0)

# Buy 100 shares
positions['AAPL'] = 100 * signals['signal']

# Initialize a portfolio with value owned
portfolio = positions.multiply(aapl['Adj Close'], axis = 0)

# Store the difference in shares owned
pos_diff = positions.diff()

# Add 'holdings' to portfolio
portfolio['holdings'] = (positions.multiply(aapl['Adj Close'], axis =0)).sum(axis=1)

# Add 'cash' to portfolio
portfolio['cash'] = initial_capital - (pos_diff.multiply(aapl['Adj Close'], axis=0)).sum(axis=1).cumsum()

# Add 'total' to portfolio
portfolio['total'] = portfolio['cash'] + portfolio['holdings']

# Add 'retuns' to portfolio
portfolio['returns'] = portfolio['total'].pct_change()

print(portfolio.head())

plt.clf()

fig = plt.figure()

ax1 = fig.add_subplot(111, ylabel='Portfolio value in $')

# Plot the quity curve in dollars
portfolio['total'].plot(ax=ax1, lw=2.)

ax1.plot(portfolio.loc[signals.positions == 1.0].index, portfolio.total[signals.positions == 1.0], '^', markersize=10, color='m')
ax1.plot(portfolio.loc[signals.positions == -1.0].index, portfolio.total[signals.positions == -1.0], 'v', markersize=10, color='k')

plt.show()


