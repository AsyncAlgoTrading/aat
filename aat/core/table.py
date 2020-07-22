from typing import Tuple
from .models import Event, Order, Trade
from .handler import EventHandler

try:
    from perspective import Table  # type: ignore
except ImportError:
    class Table(object):  # type: ignore
        def __init__(*args, **kwargs):
            pass

        def update(self, *args):
            pass

        def remove(self, *args):
            pass


class TableHandler(EventHandler):
    onData = None  # type: ignore
    onHalt = None  # type: ignore
    onContinue = None  # type: ignore
    onError = None  # type: ignore
    onStart = None  # type: ignore
    onExit = None  # type: ignore

    def __init__(self):
        self._trades = Table(Trade.perspectiveSchema(), index="timestamp")
        self._orders = Table(Order.perspectiveSchema(), index="id")

    def installTables(self, manager) -> None:
        manager.host_table("trades", self._trades)
        manager.host_table("orders", self._orders)

    def tables(self) -> Tuple[Table, Table]:
        return self._trades, self._orders

    def onTrade(self, event: Event):
        '''onTrade'''
        self._trades.update([event.target.to_json()])

    def onOpen(self, event: Event):
        '''onOpen'''
        self._orders.update([event.target.to_json()])

    def onCancel(self, event: Event):
        '''onCancel'''
        self._orders.remove([event.target.id])

    def onChange(self, event: Event):
        '''onChange'''
        self._orders.update([event.target.to_json()])

    def onFill(self, event: Event):
        '''onFill'''
        self._orders.remove([event.target.id])
