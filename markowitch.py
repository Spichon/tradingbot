from tradingbot.strategy import sma_strategy
from tradingbot.strategy import ema_strategy
from tradingbot.strategy import ichimoku_kinko_hyo_strategy
from tradingbot.cotation import cotation_kraken
from tradingbot.asset import asset_crypto
from tradingbot.portfolio import portfolio_manager
from tradingbot.account import kraken_account_wrapper
import matplotlib.pyplot as plt
import yaml
import pyfolio as pf
import os
import pandas as pd
os.environ['key'] = '++UMX5o2Y/wYNe6c5bh3RHkOhtsXQJgnWoKyKylfvLxH8EotobLKT5vP'
os.environ['secret'] = 'KObDBcajmeCLRGHmPUf4qhd0nO4yGd/B9ii47esXPIdsXKgyxTeHMmdxF/QpzMeNfbST4oPkJhAcPJc5e5ZpWQ=='
kraken_account = kraken_account_wrapper()
public_kraken = cotation_kraken()
my_portefolio = portfolio_manager(kraken_account)

sma_strat = sma_strategy('SMA', 12, 24)
ema_strat = ema_strategy('EMA', 12, 24)
ichimo_strat = ichimoku_kinko_hyo_strategy('ICHIMO')

with open(r'config.yml') as file:
    assets = yaml.load(file, Loader=yaml.FullLoader)['assets']
    for asset in assets:
        temp_asset = asset_crypto(asset=asset, cotation_place=public_kraken)
        temp_asset.add_strategy(sma_strat)
        temp_asset.add_strategy(ema_strat)
        temp_asset.add_strategy(ichimo_strat)
        my_portefolio.add_asset(temp_asset)

datas = my_portefolio.get_assets_ohlc(240)
datas

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import quandl
import scipy.optimize as sco
plt.style.use('fivethirtyeight')
np.random.seed(777)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.optimize as sco
plt.style.use('fivethirtyeight')
np.random.seed(777)
plt.figure(figsize=(14, 7))
for c in datas.columns.values:
    plt.plot(datas.index, datas[c], lw=3, alpha=0.8,label=c)
plt.legend(loc='upper left', fontsize=12)
plt.ylabel('price in $')

plt.show()
returns = datas.pct_change()
plt.figure(figsize=(14, 7))
for c in datas.columns.values:
    plt.plot(datas.index, datas[c], lw=3, alpha=0.8,label=c)
plt.legend(loc='upper right', fontsize=12)
plt.ylabel('daily returns')

plt.show()
plt.show()
returns = datas.pct_change()
plt.figure(figsize=(14, 7))
for c in returns.columns.values:
 plt.plot(returns.index, returns[c], lw=3, alpha=0.8,label=c)
plt.legend(loc='upper right', fontsize=12)
plt.ylabel('daily returns')

plt.show()
def portfolio_annualised_performance(weights, mean_returns, cov_matrix):
     returns = np.sum(mean_returns * weights) * 252
     std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
     return std, returns
 
 
 def random_portfolios(num_portfolios, mean_returns, cov_matrix, risk_free_rate):
     results = np.zeros((3, num_portfolios))
     weights_record = []
     for i in xrange(num_portfolios):
         weights = np.random.random(4)
         weights /= np.sum(weights)
         weights_record.append(weights)
         portfolio_std_dev, portfolio_return = portfolio_annualised_performance(weights, mean_returns, cov_matrix)
         results[0, i] = portfolio_std_dev
         results[1, i] = portfolio_return
         results[2, i] = (portfolio_return - risk_free_rate) / portfolio_std_dev
     return results, weights_record
 
returns = datas.pct_change()
 mean_returns = datas.mean()
 cov_matrix = datas.cov()
 num_portfolios = 25000
 risk_free_rate = 0.0178
def display_simulated_ef_with_random(mean_returns, cov_matrix, num_portfolios, risk_free_rate):
     results, weights = random_portfolios(num_portfolios, mean_returns, cov_matrix, risk_free_rate)
 
     max_sharpe_idx = np.argmax(results[2])
     sdp, rp = results[0, max_sharpe_idx], results[1, max_sharpe_idx]
     max_sharpe_allocation = pd.DataFrame(weights[max_sharpe_idx], index=table.columns, columns=['allocation'])
     max_sharpe_allocation.allocation = [round(i * 100, 2) for i in max_sharpe_allocation.allocation]
     max_sharpe_allocation = max_sharpe_allocation.T
 
     min_vol_idx = np.argmin(results[0])
     sdp_min, rp_min = results[0, min_vol_idx], results[1, min_vol_idx]
     min_vol_allocation = pd.DataFrame(weights[min_vol_idx], index=table.columns, columns=['allocation'])
     min_vol_allocation.allocation = [round(i * 100, 2) for i in min_vol_allocation.allocation]
     min_vol_allocation = min_vol_allocation.T
 
     print("-" * 80)
     print("Maximum Sharpe Ratio Portfolio Allocation\n")
     print("Annualised Return:", round(rp, 2))
     print("Annualised Volatility:", round(sdp, 2))
     print("\n")
     print(max_sharpe_allocation)
     print("-" * 80)
     print("Minimum Volatility Portfolio Allocation\n")
     print("Annualised Return:", round(rp_min, 2))
     print("Annualised Volatility:", round(sdp_min, 2))
     print("\n")
     print(min_vol_allocation)
 
     plt.figure(figsize=(10, 7))
     plt.scatter(results[0, :], results[1, :], c=results[2, :], cmap='YlGnBu', marker='o', s=10, alpha=0.3)
     plt.colorbar()
     plt.scatter(sdp, rp, marker='*', color='r', s=500, label='Maximum Sharpe ratio')
     plt.scatter(sdp_min, rp_min, marker='*', color='g', s=500, label='Minimum volatility')
     plt.title('Simulated Portfolio Optimization based on Efficient Frontier')
     plt.xlabel('annualised volatility')
     plt.ylabel('annualised returns')
     plt.legend(labelspacing=0.8)

def portfolio_annualised_performance(weights, mean_returns, cov_matrix):
     returns = np.sum(mean_returns * weights) * 252
     std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
     return std, returns
 
 
 def random_portfolios(num_portfolios, mean_returns, cov_matrix, risk_free_rate):
     results = np.zeros((3, num_portfolios))
     weights_record = []
     for i in range(num_portfolios):
         weights = np.random.random(4)
         weights /= np.sum(weights)
         weights_record.append(weights)
         portfolio_std_dev, portfolio_return = portfolio_annualised_performance(weights, mean_returns, cov_matrix)
         results[0, i] = portfolio_std_dev
         results[1, i] = portfolio_return
         results[2, i] = (portfolio_return - risk_free_rate) / portfolio_std_dev
     return results, weights_record
 
display_simulated_ef_with_random(mean_returns, cov_matrix, num_portfolios, risk_free_rate)

returns = datas.pct_change()
mean_returns = datas.mean()
cov_matrix = datas.cov()
num_portfolios = 25000
risk_free_rate = 0.0178

returns

mean_returns

cov_matrix

results, weights = random_portfolios(num_portfolios, mean_returns, cov_matrix, risk_free_rate)

def portfolio_annualised_performance(weights, mean_returns, cov_matrix):
     returns = np.sum(mean_returns * weights) * 252
     std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
     return std, returns
 
 
 def random_portfolios(num_portfolios, mean_returns, cov_matrix, risk_free_rate):
     results = np.zeros((12, num_portfolios))
     weights_record = []
     for i in range(num_portfolios):
         weights = np.random.random(12)
         weights /= np.sum(weights)
         weights_record.append(weights)
         portfolio_std_dev, portfolio_return = portfolio_annualised_performance(weights, mean_returns, cov_matrix)
         results[0, i] = portfolio_std_dev
         results[1, i] = portfolio_return
         results[2, i] = (portfolio_return - risk_free_rate) / portfolio_std_dev
     return results, weights_record

def portfolio_annualised_performance(weights, mean_returns, cov_matrix):
     returns = np.sum(mean_returns * weights) * 252
     std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
     return std, returns
 
 
 def random_portfolios(num_portfolios, mean_returns, cov_matrix, risk_free_rate):
     results = np.zeros((3, num_portfolios))
     weights_record = []
     for i in range(num_portfolios):
         weights = np.random.random(13)
         weights /= np.sum(weights)
         weights_record.append(weights)
         portfolio_std_dev, portfolio_return = portfolio_annualised_performance(weights, mean_returns, cov_matrix)
         results[0, i] = portfolio_std_dev
         results[1, i] = portfolio_return
         results[2, i] = (portfolio_return - risk_free_rate) / portfolio_std_dev
     return results, weights_record

display_simulated_ef_with_random(mean_returns, cov_matrix, num_portfolios, risk_free_rate)

def display_simulated_ef_with_random(mean_returns, cov_matrix, num_portfolios, risk_free_rate):
     results, weights = random_portfolios(num_portfolios, mean_returns, cov_matrix, risk_free_rate)
 
     max_sharpe_idx = np.argmax(results[2])
     sdp, rp = results[0, max_sharpe_idx], results[1, max_sharpe_idx]
     max_sharpe_allocation = pd.DataFrame(weights[max_sharpe_idx], index=datas.columns, columns=['allocation'])
     max_sharpe_allocation.allocation = [round(i * 100, 2) for i in max_sharpe_allocation.allocation]
     max_sharpe_allocation = max_sharpe_allocation.T
 
     min_vol_idx = np.argmin(results[0])
     sdp_min, rp_min = results[0, min_vol_idx], results[1, min_vol_idx]
     min_vol_allocation = pd.DataFrame(weights[min_vol_idx], index=datas.columns, columns=['allocation'])
     min_vol_allocation.allocation = [round(i * 100, 2) for i in min_vol_allocation.allocation]
     min_vol_allocation = min_vol_allocation.T
 
     print("-" * 80)
     print("Maximum Sharpe Ratio Portfolio Allocation\n")
     print("Annualised Return:", round(rp, 2))
     print("Annualised Volatility:", round(sdp, 2))
     print("\n")
     print(max_sharpe_allocation)
     print("-" * 80)
     print("Minimum Volatility Portfolio Allocation\n")
     print("Annualised Return:", round(rp_min, 2))
     print("Annualised Volatility:", round(sdp_min, 2))
     print("\n")
     print(min_vol_allocation)
 
     plt.figure(figsize=(10, 7))
     plt.scatter(results[0, :], results[1, :], c=results[2, :], cmap='YlGnBu', marker='o', s=10, alpha=0.3)
     plt.colorbar()
     plt.scatter(sdp, rp, marker='*', color='r', s=500, label='Maximum Sharpe ratio')
     plt.scatter(sdp_min, rp_min, marker='*', color='g', s=500, label='Minimum volatility')
     plt.title('Simulated Portfolio Optimization based on Efficient Frontier')
     plt.xlabel('annualised volatility')
     plt.ylabel('annualised returns')
     plt.legend(labelspacing=0.8)
 
display_simulated_ef_with_random(mean_returns, cov_matrix, num_portfolios, risk_free_rate)

plt.show()
def neg_sharpe_ratio(weights, mean_returns, cov_matrix, risk_free_rate):
     p_var, p_ret = portfolio_annualised_performance(weights, mean_returns, cov_matrix)
     return -(p_ret - risk_free_rate) / p_var
 
 def max_sharpe_ratio(mean_returns, cov_matrix, risk_free_rate):
     num_assets = len(mean_returns)
     args = (mean_returns, cov_matrix, risk_free_rate)
     constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
     bound = (0.0,1.0)
     bounds = tuple(bound for asset in range(num_assets))
     result = sco.minimize(neg_sharpe_ratio, num_assets*[1./num_assets,], args=args,
                         method='SLSQP', bounds=bounds, constraints=constraints)
 
def portfolio_volatility(weights, mean_returns, cov_matrix):
     return portfolio_annualised_performance(weights, mean_returns, cov_matrix)[0]
 
 def min_variance(mean_returns, cov_matrix):
     num_assets = len(mean_returns)
     args = (mean_returns, cov_matrix)
     constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
     bound = (0.0,1.0)
     bounds = tuple(bound for asset in range(num_assets))
 
     result = sco.minimize(portfolio_volatility, num_assets*[1./num_assets,], args=args,
                         method='SLSQP', bounds=bounds, constraints=constraints)
 
     return result
 
 def efficient_return(mean_returns, cov_matrix, target):
     num_assets = len(mean_returns)
     args = (mean_returns, cov_matrix)
 
     def portfolio_return(weights):
         return portfolio_annualised_performance(weights, mean_returns, cov_matrix)[1]
 
     constraints = ({'type': 'eq', 'fun': lambda x: portfolio_return(x) - target},
                    {'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
     bounds = tuple((0,1) for asset in range(num_assets))
     result = sco.minimize(portfolio_volatility, num_assets*[1./num_assets,], args=args, method='SLSQP', bounds=bounds, constraints=constraints)
     return result
 
 
 def efficient_frontier(mean_returns, cov_matrix, returns_range):
     efficients = []
     for ret in returns_range:
         efficients.append(efficient_return(mean_returns, cov_matrix, ret))
     return efficients
 
def display_calculated_ef_with_random(mean_returns, cov_matrix, num_portfolios, risk_free_rate):
     results, _ = random_portfolios(num_portfolios, mean_returns, cov_matrix, risk_free_rate)
 
     max_sharpe = max_sharpe_ratio(mean_returns, cov_matrix, risk_free_rate)
     sdp, rp = portfolio_annualised_performance(max_sharpe['x'], mean_returns, cov_matrix)
     max_sharpe_allocation = pd.DataFrame(max_sharpe.x, index=datas.columns, columns=['allocation'])
     max_sharpe_allocation.allocation = [round(i * 100, 2) for i in max_sharpe_allocation.allocation]
     max_sharpe_allocation = max_sharpe_allocation.T
 
     min_vol = min_variance(mean_returns, cov_matrix)
     sdp_min, rp_min = portfolio_annualised_performance(min_vol['x'], mean_returns, cov_matrix)
     min_vol_allocation = pd.DataFrame(min_vol.x, index=datas.columns, columns=['allocation'])
     min_vol_allocation.allocation = [round(i * 100, 2) for i in min_vol_allocation.allocation]
     min_vol_allocation = min_vol_allocation.T
 
     print("-" * 80)
     print("Maximum Sharpe Ratio Portfolio Allocation\n")
     print("Annualised Return:", round(rp, 2))
     print("Annualised Volatility:", round(sdp, 2))
     print("\n")
     print(max_sharpe_allocation)
     print("-" * 80)
     print("Minimum Volatility Portfolio Allocation\n")
     print("Annualised Return:", round(rp_min, 2))
     print("Annualised Volatility:", round(sdp_min, 2))
     print("\n")
     print(min_vol_allocation)
 
     plt.figure(figsize=(10, 7))
     plt.scatter(results[0, :], results[1, :], c=results[2, :], cmap='YlGnBu', marker='o', s=10, alpha=0.3)
     plt.colorbar()
     plt.scatter(sdp, rp, marker='*', color='r', s=500, label='Maximum Sharpe ratio')
     plt.scatter(sdp_min, rp_min, marker='*', color='g', s=500, label='Minimum volatility')
 
     target = np.linspace(rp_min, 0.32, 50)
     efficient_portfolios = efficient_frontier(mean_returns, cov_matrix, target)
     plt.plot([p['fun'] for p in efficient_portfolios], target, linestyle='-.', color='black',
              label='efficient frontier')
     plt.title('Calculated Portfolio Optimization based on Efficient Frontier')
     plt.xlabel('annualised volatility')
     plt.ylabel('annualised returns')
     plt.legend(labelspacing=0.8)
 
display_calculated_ef_with_random(mean_returns, cov_matrix, num_portfolios, risk_free_rate)

max_sharpe = max_sharpe_ratio(mean_returns, cov_matrix, risk_free_rate)
max_sharpe
max_sharpe['x']

def max_sharpe_ratio(mean_returns, cov_matrix, risk_free_rate):
     num_assets = len(mean_returns)
     args = (mean_returns, cov_matrix, risk_free_rate)
     constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
     bound = (0.0,1.0)
     bounds = tuple(bound for asset in range(num_assets))
     result = sco.minimize(neg_sharpe_ratio, num_assets*[1./num_assets,], args=args,
                            method='SLSQP', bounds=bounds, constraints=constraints)
 
max_sharpe = max_sharpe_ratio(mean_returns, cov_matrix, risk_free_rate)
def max_sharpe_ratio(mean_returns, cov_matrix, risk_free_rate):
     num_assets = len(mean_returns)
     args = (mean_returns, cov_matrix, risk_free_rate)
     constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
     bound = (0.0,1.0)
     bounds = tuple(bound for asset in range(num_assets))
     result = sco.minimize(neg_sharpe_ratio, num_assets*[1./num_assets,], args=args,
                            method='SLSQP', bounds=bounds, constraints=constraints)
     return result
 
display_calculated_ef_with_random(mean_returns, cov_matrix, num_portfolios, risk_free_rate)

plt.show()
def display_ef_with_selected(mean_returns, cov_matrix, risk_free_rate):
     max_sharpe = max_sharpe_ratio(mean_returns, cov_matrix, risk_free_rate)
     sdp, rp = portfolio_annualised_performance(max_sharpe['x'], mean_returns, cov_matrix)
     max_sharpe_allocation = pd.DataFrame(max_sharpe.x, index=datas.columns, columns=['allocation'])
     max_sharpe_allocation.allocation = [round(i * 100, 2) for i in max_sharpe_allocation.allocation]
     max_sharpe_allocation = max_sharpe_allocation.T
 
     min_vol = min_variance(mean_returns, cov_matrix)
     sdp_min, rp_min = portfolio_annualised_performance(min_vol['x'], mean_returns, cov_matrix)
     min_vol_allocation = pd.DataFrame(min_vol.x, index=datas.columns, columns=['allocation'])
     min_vol_allocation.allocation = [round(i * 100, 2) for i in min_vol_allocation.allocation]
     min_vol_allocation = min_vol_allocation.T
 
     an_vol = np.std(returns) * np.sqrt(252)
     an_rt = mean_returns * 252
 
     print("-" * 80)
     print("Maximum Sharpe Ratio Portfolio Allocation\n")
     print("Annualised Return:", round(rp, 2))
     print("Annualised Volatility:", round(sdp, 2))
     print("\n")
     print(max_sharpe_allocation)
     print("-" * 80)
     print("Minimum Volatility Portfolio Allocation\n")
     print("Annualised Return:", round(rp_min, 2))
     print("Annualised Volatility:", round(sdp_min, 2))
     print("\n")
     print(min_vol_allocation)
     print("-" * 80)
     print("Individual Stock Returns and Volatility\n")
     for i, txt in enumerate(table.columns):
         print(txt, ":", "annuaised return", round(an_rt[i], 2), ", annualised volatility:", round(an_vol[i], 2))
     print("-" * 80)
 
     fig, ax = plt.subplots(figsize=(10, 7))
     ax.scatter(an_vol, an_rt, marker='o', s=200)
 
     for i, txt in enumerate(table.columns):
         ax.annotate(txt, (an_vol[i], an_rt[i]), xytext=(10, 0), textcoords='offset points')
     ax.scatter(sdp, rp, marker='*', color='r', s=500, label='Maximum Sharpe ratio')
     ax.scatter(sdp_min, rp_min, marker='*', color='g', s=500, label='Minimum volatility')
 
     target = np.linspace(rp_min, 0.34, 50)
     efficient_portfolios = efficient_frontier(mean_returns, cov_matrix, target)
     ax.plot([p['fun'] for p in efficient_portfolios], target, linestyle='-.', color='black', label='efficient frontier')
     ax.set_title('Portfolio Optimization with Individual Stocks')
     ax.set_xlabel('annualised volatility')
     ax.set_ylabel('annualised returns')
     ax.legend(labelspacing=0.8)
 
display_calculated_ef_with_random(mean_returns, cov_matrix, num_portfolios, risk_free_rate)

plt.show()
