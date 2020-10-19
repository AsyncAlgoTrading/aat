from aat.config import Side, OrderType, OrderFlag


def _new_order(client, order):
    jsn = {}

    if order.type == OrderType.LIMIT:
        jsn['type'] = 'limit'
        jsn['side'] = order.side.value.lower()
        jsn['price'] = order.price
        jsn['size'] = order.size

        if order.flag == OrderFlag.FILL_OR_KILL:
            jsn['time_in_force'] = 'FOK'
        elif order.flag == OrderFlag.IMMEDIATE_OR_CANCEL:
            jsn['time_in_force'] = 'IOC'
        else:
            jsn['time_in_force'] = 'GTC'

    elif order.type == OrderType.MARKET:
        jsn['type'] = 'market'
        jsn['side'] = order.side.value.lower()
        jsn['size'] = order.size

    else:
        jsn['type'] = order.stop_target.side.value.lower()
        jsn['price'] = order.stop_target.price
        jsn['size'] = order.stop_target.size

        if order.stop_target.side == Side.BUY:
            jsn['stop'] = 'entry'
        else:
            jsn['stop'] = 'loss'

        jsn['stop_price'] = order.price

        if order.stop_target.type == OrderType.LIMIT:
            jsn['type'] = 'limit'
            if order.flag == OrderFlag.FILL_OR_KILL:
                jsn['time_in_force'] = 'FOK'
            elif order.flag == OrderFlag.IMMEDIATE_OR_CANCEL:
                jsn['time_in_force'] = 'IOC'
            else:
                jsn['time_in_force'] = 'GTC'

        elif order.stop_target.type == OrderType.MARKET:
            jsn['type'] = 'market'

    id = client.newOrder(jsn)
    if id > 0:
        order.id = id
        return True
    return False


def _cancel_order(client, order):
    jsn = {}
    jsn['client_oid'] = order.id
    jsn['product_id'] = order.instrument.brokerId
    return client.cancelOrder(jsn)


def _order_book(client, instrument):
    ob = client.orderBook(instrument.brokerId)
    print(ob)
    import pdb
    pdb.set_trace()
