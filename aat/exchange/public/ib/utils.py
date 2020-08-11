from ibapi.contract import Contract, ComboLeg  # type: ignore
from ibapi.order import Order  # type: ignore

from aat.config import InstrumentType, OrderType
from aat.core import Instrument


def _constructContract(instrument):
    '''Construct an IB contract and order from an Order object'''
    contract = Contract()

    if instrument.type == InstrumentType.EQUITY:
        contract.symbol = instrument.name
        contract.secType = "STK"
        contract.currency = (instrument.currency.name if instrument.currency else '') or "USD"
        contract.exchange = instrument.brokerExchange or "SMART"

    elif instrument.type == InstrumentType.BOND:
        # enter CUSIP as symbol
        contract.symbol = instrument.name  # cusip e.g. 912828C57
        contract.secType = "BOND"
        contract.exchange = instrument.brokerExchange or "SMART"
        contract.currency = instrument.currency.name or "USD"

    elif instrument.type == InstrumentType.OPTION:
        # contract.symbol = "GOOG"
        contract.secType = "OPT"
        contract.exchange = instrument.brokerExchange or "SMART"
        contract.currency = (instrument.currency.name if instrument.currency else '') or "USD"
        # contract.lastTradeDateOrContractMonth = "20170120"
        # contract.strike = 615
        # contract.right = "C"
        # contract.multiplier = "100"
        contract.localSymbol = instrument.name  # e.g. "P BMW  JUL 20  4650"
        #                                        can swap name for the above
        #                                        commented out stuff

    elif instrument.type == InstrumentType.FUTURE:
        # contract.symbol = "ES";
        contract.secType = "FUT"
        contract.exchange = instrument.brokerExchange or "SMART"
        contract.currency = (instrument.currency.name if instrument.currency else '') or "USD"
        # contract.lastTradeDateOrContractMonth = "201803";
        # contract.Multiplier = "5";

        contract.localSymbol = instrument.name  # e.g. "ESU6"
        #                                        swap for commented

    elif instrument.type == InstrumentType.PAIR:
        contract.symbol = instrument.leg1  # "EUR"
        contract.secType = "CASH"
        contract.currency = instrument.leg2  # "GBP"
        contract.exchange = instrument.brokerExchange or "IDEALPRO"

    elif instrument.type == InstrumentType.FUTURESOPTION:
        # contract.symbol = instrument.symbol
        contract.secType = "FOP"
        contract.exchange = instrument.brokerExchange
        contract.currency = (instrument.currency.name if instrument.currency else '') or "USD"
        # contract.lastTradeDateOrContractMonth = instrument.contractDate.strftime('%Y%m%d')
        # contract.strike = instrument.strike
        # contract.right = instrument.callOrPut
        # contract.multiplier = instrument.multiplier or "100"
        contract.localSymbol = instrument.name  # e.g. "ESU6"

    elif instrument.type == InstrumentType.MUTUALFUND:
        contract.symbol = instrument.name  # "VINIX"
        contract.secType = "FUND"
        contract.exchange = instrument.brokerExchange or "FUNDSERV"
        contract.currency = (instrument.currency.name if instrument.currency else '') or "USD"

    elif instrument.type == InstrumentType.COMMODITIES:
        contract.symbol = instrument.name  # "XAUUSD"
        contract.secType = "CMDTY"
        contract.exchange = instrument.brokerExchange or "SMART"
        contract.currency = (instrument.currency.name if instrument.currency else '') or "USD"

    elif instrument.type == InstrumentType.SPREAD:
        if instrument.leg1 and \
           instrument.leg1.type == InstrumentType.FUTURE and \
           instrument.leg1.underlying and \
           instrument.leg1.underlying.type == InstrumentType.COMMODITIES and \
           instrument.leg2 and \
           instrument.leg2.type == InstrumentType.FUTURE and \
           instrument.leg2.underlying and \
           instrument.leg2.underlying.type == InstrumentType.COMMODITIES and \
           instrument.leg1 != instrument.leg2:
            # Intercommodity futures use A.B
            contract.symbol = '{}.{}'.format(instrument.leg1.underlying.name,
                                             instrument.leg2.underlying.name)

        elif instrument.leg1 and instrument.leg1.underlying and \
                instrument.leg2 and instrument.leg2.underlying and \
                (instrument.leg1.underlying == instrument.leg2.underlying):
            # most other spreads just use the underlying
            contract.symbol = instrument.leg1.underlying.name

        elif instrument.leg1 and instrument.leg2 and \
            (instrument.leg1.type == InstrumentType.EQUITY and
             instrument.leg2.type == InstrumentType.EQUITY):
            # Stock spreads use A,B
            contract.symbol = '{},{}'.format(instrument.leg1.name, instrument.leg2.name)

        else:
            contract.symbol = instrument.name

        contract.secType = "BAG"
        contract.currency = (instrument.currency.name if instrument.currency else '') or "USD"
        contract.exchange = instrument.brokerExchange or "SMART"

        leg1 = ComboLeg()
        leg1.conId = instrument.brokerId
        leg1.ratio = 1  # TODO
        leg1.action = instrument.leg1_side
        leg1.exchange = instrument.brokerExchange or "SMART"

        leg2 = ComboLeg()
        leg2.conId = instrument.brokerId  # MCD STK
        leg2.ratio = 1  # TODO
        leg2.action = instrument.leg2_side
        leg2.exchange = instrument.brokerExchange or "SMART"

        contract.comboLegs = [leg1, leg2]

    elif instrument.type == InstrumentType.CURRENCY:
        raise NotImplementedError()

    elif instrument.type == InstrumentType.INDEX:
        raise NotImplementedError()

    else:
        raise NotImplementedError()
    return contract


def _constructContractAndOrder(aat_order):
    contract = _constructContract(aat_order.instrument)
    order = Order()
    order.action = aat_order.side.value

    if aat_order.order_type == OrderType.MARKET:
        order.orderType = "MKT"
        order.totalQuantity = aat_order.volume

    elif aat_order.order_type == OrderType.LIMIT:
        order.orderType = "LMT"
        order.totalQuantity = aat_order.volume
        order.lmtPrice = aat_order.price

    elif aat_order.order_type == OrderType.STOP:
        if aat_order.stop_target.order_type == OrderType.MARKET:
            order.orderType = "STP"
            order.auxPrice = aat_order.price
            order.totalQuantity = aat_order.stop_target.volume

        elif aat_order.stop_target.order_type == OrderType.LIMIT:
            order.orderType = "STP LMT"
            order.totalQuantity = aat_order.stop_target.volume
            order.lmtPrice = aat_order.stop_target.price
            order.auxPrice = aat_order.price

        else:
            raise NotImplementedError()

    else:
        raise NotImplementedError()

    return contract, order


def _constructInstrument(contract):
    name = contract.localSymbol if contract.localSymbol else contract.symbol
    brokerId = str(contract.conId)
    brokerExchange = contract.exchange
    currency = Instrument(name=contract.currency, type=InstrumentType.CURRENCY)

    if contract.secType == "STK":
        type = InstrumentType.EQUITY
    elif contract.secType == "BOND":
        type = InstrumentType.BOND
    elif contract.secType == "OPT":
        type = InstrumentType.OPTION

    elif contract.secType == "FUT":
        type = InstrumentType.FUTURE
    elif contract.secType == "CASH":
        type = InstrumentType.PAIR
    elif contract.secType == "FOP":
        type = InstrumentType.FUTURESOPTION
    elif contract.secType == "FUND":
        type = InstrumentType.MUTUALFUND
    elif contract.secType == "CMDTY":
        type = InstrumentType.COMMODITIES
    elif contract.secType == "BAG":
        type = InstrumentType.SPREAD
    else:
        raise NotImplementedError()

    return Instrument(
        name=name,
        type=type,
        exchanges=[],
        brokerExchange=brokerExchange,
        brokerId=brokerId,
        currency=currency
    )
