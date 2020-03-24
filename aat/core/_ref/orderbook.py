# https://github.com/kmanley/orderbook/blob/master/orderbook.py
# TODO: epytext is @type, @param, @rtype, @return
import cStringIO as StringIO
from collections import deque, namedtuple
# TODO: get rid of dec_places stuff, make all prices ints which represent ticks

class Order:
    def __init__(self, side, size, price, trader, order_id):
        """
        Class representing a single order
        @param side: 0=buy, 1=sell
        @param size: order quantity
        @param price: price in ticks
        @param trader: owner of order
        @param order_id: order ID        
        """
        self.side = side
        self.size = size
        self.price = price
        self.trader = trader
        self.order_id = order_id

class OrderBook(object):
    def __init__(self, name, max_price=10000, start_order_id=0, cb=None):
        """
        Creates a new order book. 
        
        @param name: name of asset being traded (e.g "BTCUSD")
        @param start_order_id: first number to use for next order
        @param max_price: maximum price in ticks
        @param cb: trade execution callback. Should have same signature as self.execute
        
        Note: a deque instance is created for each price point.
        The number of price points is max_price. For assets with high 
        max_prices this can potentially use a considerable amount of memory. 
        
        TODO: as a future optimization, could establish min_price and only create 
        (max_price-min_price) deques. The tradeoff is that during a
        market crash the order book might not be able to represent prices as low
        as the market.
        """
        self.name = name
        self.order_id = start_order_id
        self.max_price = max_price
        #self.dec_places = dec_places
        self.cb = cb or self.execute
        self.price_points = [deque() for i in range(self.max_price)] # TODO: should be > max_price so max_price is representable
        self.bid_max = 0
        self.ask_min = max_price + 1
        self.orders = {} # orderid -> Order
        
    def execute(self, trader_buy, trader_sell, price, size):
        """
        Execution callback
        @param trader_buy: the trader on the buy side
        @param trader_sell: the trader on the sell side
        @param price: trade price
        @param size: trade size
        """
        print "EXECUTE: %s BUY %s SELL %s %s @ %d" % (trader_buy, trader_sell, size, self.name, price)
        
    def limit_order(self, side, size, price, trader):
        """
        Inserts a new limit order into the order book. If the order 
        can be matched, one or more calls to the execution callback will
        be made synchronously (one for each fill). If the order can't
        be completely filled, it will be queued in the order book. In either
        case this function returns an order ID that can be used to cancel 
        the order.
        
        @param side: 0=buy, 1=sell
        @param size: order quantity
        @param price: limit price as float
        @param trader: owner of the order
        """
        self.order_id += 1
        if type(price) != int:
            raise ValueError("expected price as int (ticks)")
        #if type(price) == float:
        #    price = int(price * (10**self.dec_places))
        if side == 0: # buy order
            # look for outstanding sell orders that cross with the incoming order
            while price >= self.ask_min:
                entries = self.price_points[self.ask_min]
                while entries:
                    entry = entries[0]
                    if entry.size < size:
                        self.cb(trader, entry.trader, price, entry.size)
                        size -= entry.size
                        entries.popleft()
                    else:
                        self.cb(trader, entry.trader, price, size)
                        if entry.size > size:
                            entry.size -= size
                        else:
                            entries.popleft()
                        self.order_id += 1
                        return self.order_id
                        
                # we have exhausted all orders at the ask_min price point. Move on
                # to the next price level
                self.ask_min += 1

            # if we get here then there is some qty we can't fill, so enqueue the order
            self.order_id += 1
            #order.id = self.order_id
            self.price_points[price].append(Order(side, size, price, trader, self.order_id))
            if self.bid_max < price:
                self.bid_max = price
            return self.order_id

        else: # sell order
            # look for outstanding buy orders that cross with the incoming order
            while price <= self.bid_max:
                entries = self.price_points[self.bid_max]
                while entries:
                    entry = entries[0]
                    if entry.size < size:
                        self.cb(entry.trader, trader, price, entry.size)
                        size -= entry.size
                        entries.popleft()
                    else:
                        self.cb(entry.trader, trader, price, size)
                        if entry.size > size:
                            entry.size -= size
                        else:
                            # entry.size == size
                            entries.popleft()
                        self.order_id += 1
                        #id = self.order_id
                        return self.order_id
                        
                # we have exhausted all orders at the ask_min price point. Move on
                # to the next price level
                self.bid_max -= 1

            # if we get here then there is some qty we can't fill, so enqueue the order
            self.order_id += 1
            #order.id = self.order_id
            self.price_points[price].append(Order(side, size, price, trader, self.order_id))
            if self.ask_min > price:
                self.ask_min = price
            return self.order_id	    
            
    def _render_level(self, level, maxlen=40):
        """
        Renders a single price point level of the order book.
        """
        ret = ",".join(("%s:%s(%s)" % (order.size, order.trader, order.order_id) for order in level))
        if len(ret) > maxlen:
            ret = ",".join((str(order.size) for order in level))
        if len(ret) > maxlen:
            ret = "%d orders (total size %d)" % (len(level), sum((order.size for order in level)))
            assert len(ret) <= maxlen
        return ret
        
    def render(self):
        """
        Renders a visual representation of the order book as a string.
        This is mainly useful for debugging and learning about 
        how order books work.
        """
        output = StringIO.StringIO()
        output.write(("-"*110)+"\r\n")
        output.write("Buyers".center(55) + " | " + "Sellers".center(55) + "\r\n")
        output.write(("-"*110)+"\r\n")
        for price in range(self.max_price-1, 0, -1):
            level = self.price_points[price]
            if level:
                if price >= self.ask_min:
                    left_price = ""
                    left_orders = ""
                    right_price = str(price) #str(float(price)/10**self.dec_places)
                    right_orders = self._render_level(level)
                else:
                    left_price = str(price) #str(float(price)/10**self.dec_places)
                    left_orders = self._render_level(level)
                    right_price = ""
                    right_orders = ""
                output.write(left_orders.rjust(43))
                output.write(" |")
                output.write(left_price.rjust(10))
                output.write(" | ")
                output.write(right_price.rjust(10))
                output.write("| ")
                output.write(right_orders.ljust(43))
                output.write("\r\n"+("-"*110)+"\r\n")
        return output.getvalue()
# TODO: cancels                    
# TODO: different order types, what are they?
#  fill or kill, partial order allowed, etc...
# TODO: support market order
# TODO: performance testing
# TODO: get rid of Order object for input? just store them internally?    
def _unittest2():
    book = OrderBook("BTCUSD")
    orders = [(0, 3, 200, "Bea"),
              (1, 2, 201, "Sam"),
              (0, 2, 200, "Ben"),
              (1, 1, 198, "Sol"),
              (1, 5, 202, "Stu"),
              (0, 2, 201, "Bif"),
	      (0, 2, 202, "Bif"),
              (0, 2, 201, "Bob"),
              (1, 6, 200, "Sue"),
              (0, 7, 198, "Bud"),]
    for i, order in enumerate(orders):
      #print "STEP %d" % i
      #print book.render()
      book.limit_order(*order)
      #print
    print
    print book.render()
     
def _unittest1():
    ob = OrderBook("BTCUSD")
    
    #o1 = Order(0, 50, 100, 'trader 1')
    #ob.limit_order(o1)
    #o2   = Order(1, 50, 100, 'trader 2')
    #ob.limit_order(o2)

    # side, size, price, trader
    ob.limit_order(0, 50, 1.00, 'trader 1')
    ob.limit_order(1, 80, 1.01, 'trader 2')
    ob.limit_order(0, 20, 1.00, 'trader 3')
    ob.limit_order(1, 5, 1.05, 'trader 4')
    ob.limit_order(1, 5, 1.25, 'trader 5')
    #ob.limit_order(0, 100, 1.50, 'trader 6')    
    print ob.render()

def _perftest():
    import os
    print "pid: %s" % os.getpid()
    class MyOrderBook(OrderBook):
        trades = 0
        def execute(self, trader_buy, trader_sell, price, size):
            MyOrderBook.trades += 1
    
    import time, random
    ITERS = 100000
    max_price = 10
    ob = OrderBook("FOOBAR", max_price=max_price)
    start = time.clock()
    for i in range(ITERS):
        os.system("clear")
        buysell, qty, price, trader = random.choice([0,1]), random.randrange(1,150), \
                random.randrange(1,max_price), 'trader %s' % random.randrange(1000)
        print "NEW ORDER: %s %s %s @ %s" % (trader, "BUY" if buysell==0 else "SELL", qty, price)
        ob.limit_order(buysell, qty, price, trader)
        print ob.render()
        raw_input()
    elapsed = (time.clock() - start) * 1000.
    print "# orders: %d" % ITERS
    print "elapsed: %.2f msecs" % elapsed
    print "# trades: %d" % MyOrderBook.trades
    print "%.2f orders/sec" % (ITERS/elapsed*1000.)
    #print ob.render()
    raw_input()
        
if __name__ == "__main__":
    _unittest2()
    import sys
    sys.exit(0)
    #_unittest1()
    #_perftest(
    import time
    ob = OrderBook("GBPUSD")
    start = time.time()
    ob.limit_order(0, 100, 593, "Kevin")
    ob.limit_order(1, 100, 200, "Tom")
    elapsed = time.time() - start
    print "elapsed: %s" % (elapsed * 1e6)