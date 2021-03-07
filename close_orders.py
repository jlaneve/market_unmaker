from optibook.synchronous_client import Exchange
import time

e = Exchange()
a = e.connect()


# Get out of all positions you are currently holding, regarless of the loss involved. That means selling whatever
# you are long, and buying-back whatever you are short. Be sure you know what you are doing when you use this logic.
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