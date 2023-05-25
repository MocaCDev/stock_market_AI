import json, os, sys
from datetime import datetime, timezone
import requests, finnhub
import yfinance as yf

r = requests.get('https://api.polygon.io/v2/aggs/ticker/NVDA/range/1/day/2023-01-09/2023-01-09?apiKey=L3Z9OD0EVE1bmTmWDAO3llfwD1uMugpM')
print(r.json())
sys.exit(0)

date = str(datetime.now().date()).split('-')
date = [int(i) for i in date]
date[2] += 2
date = [str(i) for i in date]
date = '-'.join(date)

adirnames = []
afilenames = []
filename = None
for (_, dirnames, _) in os.walk('data'):
    adirnames.append(dirnames)
    for i in dirnames:
        for (_, _, filename) in os.walk(f'data/{i}'):
            afilenames.append(filename[0])

adirnames = adirnames[0]

strat_data = {
    'Stock Name': None,
    'Average Price Per Stock': None,
    'Date': date,
    'Opened At': None,
    'Last Closed': None,
    'Open Difference To Last Closed': None,
    'Todays High': None,
    'Todays Low': None,
    'Predicted % Change': None,
    'Status': 'Before Open' if sys.argv[1] == 'before' else 'During Open' if sys.argv[1] == 'during' else 'After Close',
    'Possibilities': {
        'Possible Gain Today': None,#msft.info['dayHigh'] - msft.info['open'] if msft.info['open'] < msft.info['dayHigh'] else 0,
        'Possible Gain %': None,#msft.info['open'] / msft.info['dayHigh'] if msft.info['open'] < msft.info['dayHigh'] else 0,
        'Possible Loss Today': None,#msft.info['open'] - msft.info['dayLow'] if msft.info['open'] > msft.info['dayLow'] else 0,
        'Possible Loss %': None,#msft.info['open'] / msft.info['dayLow'] if msft.info['open'] > msft.info['dayLow'] else 0,
    },
    'Profit': {
        'Obtain Profit At Price': None,
        'Profit Total': None,
        'Shares Before Profit Obtained': None,
        'Shares After Profit Obtained': None,
        'Shares Sold': None,
        'Start Price Before Profit Withdraw': None,
        'End Price After Profit Withdraw': None,
    },
    'Loss': {
        'Loss Total': None,
        'Start Price Before Loss': None,
        'End Price After Loss': None,
        'Initial Price In Stock': None,
        'Prior Gains': None,
        'Shares': None,
    },
    'Periodic Data': {
        'Day % Change': None,
        'Week % Change': None,
        'Month % Change': None,
        '3 Months % Change': None,
        '6 Months % Change': None,
        'YTD % Change': None,
        '1 Year % Change': None,
        '3 Years % Change': None,
        '5 Years % Change': None,
        '10 Years % Change': None,
        'Max % Change Overall(10+ Years)': None
    }
}

# Some stocks, such as C3.AI, are represented by just AI
change_to = {'C3.AI': 'AI'}

# All of the stocks we are keeping track of during this run of the program
stocks = sys.argv[3].split(',')
original_stocks = sys.argv[3].split(',') # Needed just in case a stock, such as C3.AI, is being kept track of

# Prices
prices = [float(i) for i in sys.argv[4].split(',')]

# Average Costs
avg_costs = [float(i) for i in sys.argv[5].split(',')]

# Number of shares
num_shares = [float(i) for i in sys.argv[6].split(',')]

# Todays Return
returns = [float(i) for i in sys.argv[7].split(',')]

# Beginning Price
beg_prices = []

# Create new directories, if they don't already exist, for each stocks data to reside in
for i in original_stocks:
    if not os.path.isdir(f'data/{i}'):
        os.mkdir(f'data/{i}')

for i in range(len(prices)):
    if returns[i] < 0: beg_prices.append(prices[i] + (returns[i] * -1))
    else: beg_prices.append(prices[i] - returns[i])

print(prices, returns, beg_prices)

# Information we don't need
not_needed = [
    'address1', 'address2', 'city', 'state', 'zip',
    'country', 'phone', 'website', 'industry', 'industryDisp',
    'sector', 'longBusinessSummary', 'fullTimeEmployees',
    'companyOfficers'    
]

# Update if the name is not as required
for i in range(len(stocks)):
    if stocks[i] in change_to:
        stocks[i] = change_to[stocks[i]]

# Obtain all info over all the stocks
msft = None
for i in range(len(stocks)):
    msft = yf.Ticker(stocks[i])

    #r = requests.get(f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={stocks[i]}&interval=5min&apikey=3O1AWMMI7B18DBJF')
    
    strat_data['Stock Name'] = original_stocks[i]
    strat_data['Average Price Per Stock'] = avg_costs[i]
    strat_data['Opened At'] = msft.info['open']
    strat_data['Todays High'] = msft.info['dayHigh']
    strat_data['Todays Low'] = msft.info['dayLow']
    strat_data['Last Closed'] = msft.info['previousClose']
    strat_data['Open Difference To Last Closed'] = msft.info['open'] - msft.info['previousClose']
    strat_data['Predicted % Change'] = round(((prices[i] - beg_prices[i]) / prices[i]) * 100, 2)
    strat_data['Possibilities']['Possible Gain Today'] = msft.info['dayHigh'] - msft.info['open'] if msft.info['open'] < msft.info['dayHigh'] else 0
    strat_data['Possibilities']['Possible Gain %'] = msft.info['open'] / msft.info['dayHigh'] if msft.info['open'] < msft.info['dayHigh'] else 0
    strat_data['Possibilities']['Possible Loss Today'] = msft.info['open'] - msft.info['dayLow'] if msft.info['open'] > msft.info['dayLow'] else 0
    strat_data['Possibilities']['Possible Loss %'] = msft.info['open'] / msft.info['dayLow'] if msft.info['open'] > msft.info['dayLow'] else 0

    if returns[i] < 0:
        strat_data['Loss']['Loss Total'] = returns[i]
        strat_data['Loss']['Start Price Before Loss'] = beg_prices[i]
        strat_data['Loss']['End Price After Loss'] = prices[i]
        strat_data['Loss']['Initial Price In Stock'] = num_shares[i] * avg_costs[i]
        strat_data['Loss']['Shares'] = round(strat_data['Loss']['Initial Price In Stock'] / avg_costs[i], 2)

        # Delete `Profit`. We don't need to have it
        strat_data['Profit'].clear()
    if returns[i] > 0:
        strat_data['Profit']['Obtain Profit At Price'] = prices[i]
        strat_data['Profit']['Profit Total'] = prices[i] - beg_prices[i]
        strat_data['Profit']['Shares Before Profit Obtained'] = round(beg_prices[i] / avg_costs[i], 2)
        strat_data['Profit']['Shares After Profit Obtained'] = round(strat_data['Profit']['Shares Before Profit Obtained'] - (strat_data['Profit']['Profit Total'] / avg_costs[i]), 2)
        strat_data['Profit']['Shares Sold'] = round(strat_data['Profit']['Profit Total'] / avg_costs[i], 6)
        strat_data['Profit']['Start Price Before Profit Withdraw'] = prices[i]
        strat_data['Profit']['End Price After Profit Withdraw'] = prices[i] - strat_data['Profit']['Profit Total']

        # Delete `Loss`. We don't need to have it
        strat_data['Loss'].clear()

    resp = requests.get(f'https://financialmodelingprep.com/api/v3/stock-price-change/{stocks[i]}?apikey=b96a973d765d9a17847537211467142a')
    resp = resp.json()
    strat_data['Periodic Data']['Day % Change'] = resp[0]['1D']
    strat_data['Periodic Data']['Week % Change'] = resp[0]['5D']
    strat_data['Periodic Data']['Month % Change'] = resp[0]['1M']
    strat_data['Periodic Data']['3 Months % Change'] = resp[0]['3M']
    strat_data['Periodic Data']['6 Months % Change'] = resp[0]['6M']
    strat_data['Periodic Data']['YTD % Change'] = resp[0]['ytd']
    strat_data['Periodic Data']['1 Year % Change'] = resp[0]['1Y']
    strat_data['Periodic Data']['3 Years % Change'] = resp[0]['3Y']
    strat_data['Periodic Data']['5 Years % Change'] = resp[0]['5Y']
    strat_data['Periodic Data']['10 Years % Change'] = resp[0]['10Y']
    strat_data['Periodic Data']['Max % Change Overall(10+ Years)'] = resp[0]['max']

    number = 0
    for x in afilenames:
        if original_stocks[i] in x:
            number += 1

    type_ = None
    if sys.argv[2] == 'roth':
        type_ = 'roth'
    else: type_ = 'normal'

    with open(f'data/{original_stocks[i]}/{date} - {original_stocks[i]} {type_} {number}.json', 'w') as file:
        file.write(json.dumps(strat_data, indent=2))
        file.flush()
        file.close()

for i in range(len(prices)):
    print(f'% Change of {original_stocks[i]}: ', round(((prices[i] - beg_prices[i]) / prices[i]) * 100, 2))
