import utils
from optibook.synchronous_client import Exchange
import time
import math

import logging
logger = logging.getLogger('client')
logger.setLevel('ERROR')

from ticker_utils import Ticker
from market_utils import Market

print("Setup was successful.")


e = Exchange()
a = e.connect()

market = Market(e)

DELTA = 0.5
threshold = 50
num_trades = 20

trades = []



# Bringing delta to 0:
# 1. Buy/sell A+G
# 2. Buy/sell B


# Flow:
# 1. Delta hedge if needed
# 2. Get rid of old trades
# 3. Find new target price
# 4. Trade around new target price


while True:
    try:
        market.update()
        market.print_market()
        
        delta = market.positions.get_delta()
        
        if abs(delta) >= threshold:
            print("NEED TO HEDGE {}".format(delta))
            size = abs(math.floor(delta / 2))
            amazon_size = market.positions.amazon
            google_size = market.positions.google
            
            # if delta > 0, we need to sell A+G
            if delta > 0:
                max_amazon_allowed = 500 + amazon_size if amazon_size > 0 else min(amazon_size + 500, 800)
                max_google_allowed = 500 + google_size if google_size > 0 else min(google_size + 500, 800)
                
                amazon_size = min(size, max_amazon_allowed)
                google_size = min(size, max_google_allowed)
                
                market.sell("AMAZON", "market", amazon_size)
                market.sell("GOOGLE", "market", google_size)
            # if delta < 0, we need to buy A+G
            elif delta < 0:
                max_amazon_allowed = 500 - amazon_size if amazon_size > 0 else min(-1 * amazon_size + 500, 800)
                max_google_allowed = 500 - google_size if google_size > 0 else min(-1 * google_size + 500, 800)
                
                amazon_size = min(size, max_amazon_allowed)
                google_size = min(size, max_google_allowed)
                
                
                print(market.buy("AMAZON", "market", amazon_size))
                print(market.buy("GOOGLE", "market", google_size))
        
        
        if len(trades) > num_trades:
            e.delete_order("TECH_BASKET", order_id = trades[0])
            e.delete_order("TECH_BASKET", order_id = trades[1])
            trades = trades[2:]
        
        ask = market.get_theoretical_ask()
        bid = market.get_theoretical_bid()
        avg = (ask + bid)/2
        
        
        if not avg == 0:
            # Buy at avg - dt, sell at avg + dt
            trades.append(market.buy("TECH_BASKET", avg - DELTA, 10))
            trades.append(market.sell("TECH_BASKET", avg + DELTA, 10))
            
        # market.orders.print_orders()
            
        time.sleep(0.2)
            
    except Exception as err:
        if not e.is_connected():
            e.connect()
        print(err)
        time.sleep(5)
    