from perspective import Table
from ..config import EventType
from .models import Event, Data
from .handler import EventHandler


class TableHandler(EventHandler):
    onData = None
    onHalt = None
    onContinue = None
    onError = None
    onStart = None
    onExit = None

    def __init__(self):
        self._trades = Table(Data.schema(), index="timestamp")
        self._orders = Table(Data.schema(), index="id")

    def installTables(self, manager):
        manager.host_table("trades", self._trades)
        manager.host_table("orders", self._orders)

    def tables(self):
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
