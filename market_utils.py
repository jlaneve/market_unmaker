from optibook.common_types import PriceVolume

class Market:
    def __init__(self, exchange):
        self.exchange = exchange
        
        self.delta = 0.5
        self.volume = 50
        
        self.books = OrderBooks(exchange)
        self.orders = OrderManager(exchange)
        self.positions = Positions(exchange)
        self.market_maker = MarketMaker(exchange)
        self.update()
        
    def print_market(self):
        print("==============CURRENT VOLUMES==============")
        print(
            "TECH_BASKET BID / ASK: {} {}".format(
            self.books.basket.get_total_volume("bid"),
            self.books.basket.get_total_volume("ask")
        ))
        
        print("==============CURRENT BIDS==============")
        print(
            "TECH_BASKET: {} ({})".format(
            self.books.basket.best_bid.price,
            self.books.basket.best_bid.volume
        ))
        
        print("==============CURRENT ASKS==============")
        print(
            "TECH_BASKET: {} ({})".format(
            self.books.basket.best_ask.price,
            self.books.basket.best_ask.volume
        ))
        
        print("==============CURRENT POSITIONS==============")
        print(
            "AMAZON: {}, GOOGLE: {}, TECH_BASKET: {}".format(
            self.positions.amazon,
            self.positions.google,
            self.positions.basket,
        ))
        
        print("==============CURRENT ORDERS==============")
        self.orders.print_orders()
        
        
        print("\n")
        
    def update(self):
        self.update_books()
        self.update_positions()
        self.update_orders()
        
    def update_positions(self):
        self.positions.update_positions()
        
    def update_books(self):
        self.books.update_books()
        
    def update_orders(self):
        self.orders.update_orders()
        
    def get_theoretical_diff(self):
        amazon = self.books.amazon
        google = self.books.google
        basket = self.books.basket
        
        diff, volume = 0, 0
        
        if google.best_ask.price + amazon.best_ask.price < basket.best_bid.price:
            diff = round(google.best_ask.price + amazon.best_ask.price - basket.best_bid.price, 1)
            volume = min(google.best_ask.volume, amazon.best_ask.volume, basket.best_bid.volume)
            
        elif google.best_bid.price + amazon.best_bid.price > basket.best_ask.price:
            diff = round(google.best_bid.price + amazon.best_bid.price - basket.best_ask.price, 1)
            volume = min(google.best_bid.volume, amazon.best_bid.volume, basket.best_ask.volume)
            
            
        return diff
        
    def buy(self, instrument_id, price, volume, trade_type = None):
        if price == "market":
            price = self.books.get_book_by_name(instrument_id).best_ask.price
            print(price)
            return self.orders.trade(instrument_id, price, volume, "bid", trade_type if trade_type else "ioc")
        else:
            return self.orders.trade(instrument_id, price, volume, "bid", trade_type if trade_type else "limit")
            
    def sell(self, instrument_id, price, volume, trade_type = None):
        print(price, volume)
        if price == "market":
            price = self.books.get_book_by_name(instrument_id).best_bid.price
            return self.orders.trade(instrument_id, price, volume, "ask", trade_type if trade_type else "ioc")
        else:
            return self.orders.trade(instrument_id, price, volume, "ask", trade_type if trade_type else "limit")
            
    def get_theoretical_ask(self):
        return self.books.amazon.best_ask.price + self.books.google.best_ask.price
        
    def get_theoretical_bid(self):
        return self.books.amazon.best_bid.price + self.books.google.best_bid.price
        
    def get_undercut_ask(self):
        return round(self.books.basket.best_ask.price - self.delta, 1)
    
    def get_undercut_bid(self):
        return round(self.books.basket.best_bid.price + self.delta, 1)
        
    def create_market_making_orders(self):
        ask = self.get_undercut_ask()
        bid = self.get_undercut_bid()
        
        print(ask, bid)
        
        if self.market_maker.update_orders_required(ask, bid):
            # self.clear_orders()
            
            self.buy("TECH_BASKET", bid, self.volume, trade_type = "limit")
            
            self.sell("TECH_BASKET", ask, self.volume, trade_type = "limit")
        
    def clear_orders(self):
        self.orders.clear_orders()
        
    def get_trade_history(self, instrument_id):
        tradeticks = self.exchange.get_trade_history(instrument_id)
        for trade in tradeticks:
            print(f"[{trade.instrument_id}] price({trade.price}), volume({trade.volume}), aggressor_side({trade.side})")
            
    def get_total_delta(self):
        return self.orders.get_unrealized_delta() + self.positions.get_delta()

class MarketMaker:
    def __init__(self, exchange):
        self.exchange = exchange
        
        self.last_ask = None
        self.last_bid = None
        
    def update_prices(self, new_ask, new_bid):
        self.last_ask = new_ask
        self.last_bid = new_bid
        
    def update_orders_required(self, new_ask, new_bid):
        res = (new_ask != self.last_ask) or (new_bid != self.last_bid)
        self.update_prices(new_ask, new_bid)
        
        return res
        
    def buy_middle(self, orders):
        for order in orders:
            print("\t{}: {} {} @ {}".format(order.order_id, order.side, order.volume, order.price))

class OrderBooks:
    def __init__(self, exchange, amazon_book = None, google_book = None, basket_book = None):
        self.exchange = exchange
        self.amazon = amazon_book
        self.google = google_book
        self.basket = basket_book
        
    def update_books(self):
        self.google = Book("GOOGLE", self.exchange.get_last_price_book("GOOGLE"))
        self.amazon = Book("AMAZON", self.exchange.get_last_price_book("AMAZON"))
        self.basket = Book("TECH_BASKET", self.exchange.get_last_price_book("TECH_BASKET"))
        
    def get_book_by_name(self, instrument_id):
        if instrument_id == "GOOGLE":
            return self.google
        elif instrument_id == "AMAZON":
            return self.amazon
        else:
            return self.basket

class Book:
    def __init__(self, instrument_id, order_book):
        self.instrument_id = instrument_id
        self.bids = order_book.bids
        self.asks = order_book.asks
        
        self.best_bid = PriceVolume(0, 0)
        self.best_ask = PriceVolume(0, 0)
        
        self.update_attributes()
        
        
    def update_attributes(self):
        if self.bids:
            self.best_bid = self.bids[0]
            self.best_bid.price = round(self.best_bid.price, 1)
            
        if self.asks:
            self.best_ask = self.asks[0]
            self.best_ask.price = round(self.best_ask.price, 1)
    
    def get_total_volume(self, side):
        if side == "ask":
            return sum([ask.volume for ask in self.asks])
        else:
            return sum([bid.volume for bid in self.bids])

class Positions:
    def __init__(self, exchange):
        self.exchange = exchange
        self.amazon = None
        self.google = None
        self.basket = None
        
    def update_positions(self):
        positions = self.exchange.get_positions()
        self.amazon = positions["AMAZON"]
        self.google = positions["GOOGLE"]
        self.basket = positions["TECH_BASKET"]
        
    def get_delta(self):
        return -1 * (self.amazon + self.google - self.basket)

class OrderManager:
    def __init__(self, exchange):
        self.exchange = exchange
        
        self.amazon_order_ids = []
        self.google_order_ids = []
        self.basket_order_ids = []
        
        self.amazon = None
        self.google = None
        self.basket = None
        
    def trade(self, instrument_id, price, volume, side, order_type):
        order_id = self.exchange.insert_order(
            instrument_id,
            price = price,
            volume = volume,
            side = side,
            order_type = order_type
        )
        
        if instrument_id == "AMAZON":
            self.amazon_order_ids.append(order_id)
            
        if instrument_id == "GOOGLE":
            self.google_order_ids.append(order_id)
            
        if instrument_id == "TECH_BASKET":
            self.basket_order_ids.append(order_id)
            
        return order_id
    
    def update_orders(self):
        self.amazon = self.exchange.get_outstanding_orders("AMAZON")
        self.google = self.exchange.get_outstanding_orders("GOOGLE")
        self.basket = self.exchange.get_outstanding_orders("TECH_BASKET")
        
    def print_orders(self):
        print("AMAZON:")
        if self.amazon:
            for order in self.amazon.values():
                print("\t{}: {} {} @ {}".format(order.order_id, order.side, order.volume, order.price))
            
        print("GOOGLE:")
        if self.google:
            for order in self.google.values():
                print("\t{}: {} {} @ {}".format(order.order_id, order.side, order.volume, order.price))

        print("BASKET:")
        if self.basket:
            for order in self.basket.values():
                print("\t{}: {} {} @ {}".format(order.order_id, order.side, order.volume, order.price))
            
    def clear_orders(self):
        self.exchange.delete_orders("TECH_BASKET")
        
        
    def get_unrealized_delta(self):
        amazon_delta = sum([order.volume for order in self.amazon.values()])
        google_delta = sum([order.volume for order in self.google.values()])
        basket_delta = sum([order.volume for order in self.basket.values()])
        
        return amazon_delta + google_delta + basket_delta
        
    def get_unrealized_volume(self, instrument_id):
        if instrument_id == "TECH_BASKET":
            return sum([
                order.volume for order in self.basket.values()
            ])
        elif instrument_id == "AMAZON":
            return sum([
                order.volume for order in self.amazon.values()
            ])
        elif instrument_id == "GOOGLE":
            return sum([
                order.volume for order in self.google.values()
            ])
