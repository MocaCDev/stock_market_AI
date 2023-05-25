from robin_stocks.robinhood import (
    login, get_top_100, get_all_stock_orders, get_all_open_stock_orders, get_quotes, get_stock_order_info, find_stock_orders, get_latest_price, get_ratings, get_earnings,
    get_historical_portfolio, build_holdings, order_buy_market, order, order_sell_market, order_buy_fractional_by_price,
    get_option_order_info, get_stock_quote_by_id, get_stock_quote_by_symbol, get_symbol_by_url,
    get_name_by_url, helper, find_stock_orders
)
from time import sleep
import sys, json, threading, requests

def print_json(data):
    sys.stdout.write(json.dumps(data, indent=2))
    sys.stdout.flush()

# TODO: Some of the data is referencing sells
#       Figure out how to handle this.
def load(data_arr, backup = None, _type = 'q', index = None):
    if index == None:
        if len(data_arr) >= 1:
            ret_array = []

            for i in range(len(data_arr)):
                if _type == 'q': ret_array.append(data_arr[i]['quantity']) if not data_arr[i]['quantity'] in ret_array else print('', end = '')
                if _type == 'rn': ret_array.append(data_arr[i]['rounded_notation']) if not data_arr[i]['rounded_notation'] in ret_array else print('', end = '')
                if _type == 'sd': ret_array.append(data_arr[i]['settlement_date']) if not data_arr[i]['settlement_date'] in ret_array else print('', end = '')
            return ret_array
    else:
        if len(data_arr) >= 1:
            if _type == 'rn': return data_arr[0]['rounded_notional']
            
            # If it doesn't work it's sell data
            return data_arr['quantity']
        else:
            #print(json.dumps(backup, indent=2))
            return 1
        #if index <= len(data_arr) - 1 and not index < 0 and len(data_arr) >= 1:
        #    try:
        #        if _type == 'rn':return data_arr[index]['rounded_notional']
        #    except:
        #        print(json.dumps(data_arr, indent=2), index)
        #        if _type == 'rn': return data_arr[0]['rounded_notional']

    try:    
        if _type == 'ap': 
            return data_arr['average_price']
    except: pass

    return None

class App:

    def __init__(self, email, password, stocks = None, stock_orders_year = ['2023', '2022']):
        if not type(stocks) == list:
            sys.stdout.write('The argument `stocks` needs to be an array of stocks.')
            sys.stdout.flush()
            sys.exit(1)
        
        if stock_orders_year == None:
            sys.stdout.write('`stock_orders_years` cannot be None')
            sys.stdout.flush()
            sys.exit(1)
        
        # Login!
        self.login = login(email, password)
        self.access_token = self.login['access_token']
        self.refresh_token = self.login['refresh_token']

        # General Stock Data!
        self.stocks = stocks
        self.general_stock_info = {}
        self.stocks_latest_price = []
        self.orders_info = []

        # Get the earnings!
        for i in self.stocks:
            quotes_data = get_quotes(i)
            self.general_stock_info[i] = {
                'Ask Price': quotes_data[0]['ask_price'],
                'Bid Price': quotes_data[0]['bid_price'],
                'Last Trade Price': quotes_data[0]['last_trade_price'],
                'Previous Close': quotes_data[0]['previous_close']
            }

            self.stocks_latest_price.append(get_latest_price(i)[0])

        all_orders = None
        for i in self.stocks:
            for x in find_stock_orders(symbol=i):
                #print(json.dumps(x, indent=2))
                for y in stock_orders_year:
                    if y in x['created_at']:
                        self.orders_info.append({
                            'Symbol': i,
                            f'{i} Data': {
                                'Order ID': x['id'],
                                'Ref Order ID': x['ref_id'],
                                'Date Initiated': x['created_at'],
                                'Date Updated': x['updated_at'],
                                'Average Price': x['average_price'],
                                'Action': x['side'],
                                'Shares Bought': load(x['executions']),
                                'Equation': f'{float(load(data_arr = x["executions"], backup = x, _type = "rn", index = 0)) / float(load(x, _type = "ap", index=-1))}',
                                #'Settlement Date': x['executions'][0]['settlement_date']
                            }
                        })
                        #print(json.dumps(i, indent=2))

            with open('order_history.json', 'w') as file:
                file.write(json.dumps(self.orders_info, indent=2))
                file.flush()
                file.close()

        #print(self.general_stock_info, '\n', self.stocks_latest_price, '\n', self.orders_info)
