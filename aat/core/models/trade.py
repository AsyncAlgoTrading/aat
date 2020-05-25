from collections import deque
from pydantic import validator
from typing import Mapping, Type, Union
from .data import Data
from .order import Order
from ...config import DataType, Side


class Trade(Data):
    # for convenience
    Types = DataType

    type: DataType = DataType.TRADE
    maker_orders: deque
    taker_order: Order

    _slippage: float = 0.0
    _transaction_cost: float = 0.0

    def addSlippage(self, slippage: float):
        '''add slippage to an trade'''
        if self.side == Side.BUY:
            # price moves against (up)
            self._slippage = slippage
            self.price += slippage
        else:
            # price moves against (down)
            self._slippage = -slippage
            self.price -= slippage

    def addTransactionCost(self, txncost: float):
        '''add transaction cost to a trade'''
        if self.side == Side.BUY:
            # price moves against (up)
            self.transaction_cost = txncost
            self.price += txncost
        else:
            # price moves against (down)
            self.transaction_cost = -txncost
            self.price -= txncost

    def slippage(self):
        '''the amount of slippage of the order'''
        return 0.0

    def transactionCost(self):
        '''any transaction costs incurred on the order'''
        return 0.0

    @validator("type")
    def _assert_type_is_order(cls, v):
        assert v == DataType.TRADE
        return v

    @validator("maker_orders")
    def _assert_maker_orders(cls, v):
        assert len(v) > 0
        return v

    def __str__(self):
        return f'<{self.instrument}-{self.volume:.2f}@{self.price:.2f}-{self.exchange}>'

    def to_json(self) -> Mapping[str, Union[str, int, float]]:
        return \
            {'id': self.id,
             'timestamp': self.timestamp,
             'volume': self.volume,
             'price': self.price,
             'side': self.side.value,
             'instrument': str(self.instrument),
             'exchange': str(self.exchange)}

    @staticmethod
    def perspectiveSchema() -> Mapping[str, Type]:
        return {
            "id": int,
            "timestamp": int,
            "volume": float,
            "price": float,
            "side": str,
            "instrument": str,
            "exchange": str,
        }
