import utils
from optibook.synchronous_client import Exchange
import threading
import time
import logging
logger = logging.getLogger('client')
logger.setLevel('ERROR')

from market_utils import Market

print("Setup was successful.")


e = Exchange()
a = e.connect()

market = Market(e)

def clear_positions():
    positions = e.get_positions()
    while sum(positions.values()) != 0:
        positions = e.get_positions()
        for s, p in positions.items():
            if p > 0:
                e.insert_order(s, price=150, volume=p, side='ask', order_type='limit')
            elif p < 0:
                e.insert_order(s, price=250, volume=-p, side='bid', order_type='limit')  
        print(e.get_positions())
        
        time.sleep(1)
        
        
clear_positions()

UPPER_BOUND = 700
UPPER_PRICE_BOUND = 49000
LOWER_BOUND = 160
LOWER_PRICE_BOUND = 160
VOL = 300


buy_id = market.buy("TECH_BASKET", LOWER_PRICE_BOUND, VOL)
sell_id = market.sell("TECH_BASKET", UPPER_PRICE_BOUND, VOL)


while True:
    try:
        market.update()
        size = market.positions.basket
        
        basket_bid_vol = market.books.basket.get_total_volume("bid") - VOL
        for order in market.books.basket.bids:
            if order.price > LOWER_BOUND:
                market.sell("TECH_BASKET", order.price, order.volume)
            
        basket_ask_vol = market.books.basket.get_total_volume("ask") - VOL
        for order in market.books.basket.asks:
            if order.price < UPPER_BOUND:
                market.buy("TECH_BASKET", order.price, order.volume)
            
    except Exception as err:
        if not e.is_connected():
            e.connect()
            
            time.sleep(1)
            
            positions = e.get_positions()

            while sum(positions.values()) != 0:
                positions = e.get_positions()
                for s, p in positions.items():
                    if p > 0:
                        e.insert_order(s, price=150, volume=p, side='ask', order_type='limit')
                    elif p < 0:
                        e.insert_order(s, price=250, volume=-p, side='bid', order_type='limit')  
                print(e.get_positions())
                
                time.sleep(1)
                
            
            buy_id = market.buy("TECH_BASKET", LOWER_PRICE_BOUND, VOL)
            sell_id = market.sell("TECH_BASKET", UPPER_PRICE_BOUND, VOL)
            
        print(err)
        time.sleep(5)


def update_orders_loop():
    while True:
        e.amend_order("TECH_BASKET", order_id = buy_id, volume = VOL)
        e.amend_order("TECH_BASKET", order_id = sell_id, volume = VOL)
        time.sleep(5)
        
        
if __name__ == '__main__':
    threading.Thread(target=purchase_middle_loop).start()
    threading.Thread(target=update_orders_loop).start()