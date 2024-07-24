from datetime import datetime

class StockModel:
    def __init__(self):
        self.stock_symbol = None
        self.stock_type = None
        self.last_dividend = 0
        self.fixed_dividend = 0
        self.par_value = 0

    def set_stock_symbol(self, symbol_of_stock: str) -> None:
        self.stock_symbol = symbol_of_stock

    def get_stock_symbol(self):
        return self.stock_symbol

    def set_stock_type(self, type_of_stock):
        self.stock_type = type_of_stock

    def get_stock_type(self):
        return self.stock_type

    def set_last_dividend(self, dividend):
        self.last_dividend = dividend

    def get_last_dividend(self):
        return self.last_dividend

    def set_fixed_dividend(self, dividend_fix):
        self.fixed_dividend = dividend_fix

    def get_fixed_dividend(self):
        return self.fixed_dividend

    def set_par_value(self, new_par_value):
        self.par_value = new_par_value

    def get_par_value(self):
        return self.par_value


class TradeModel:
    def __init__(self):
        self.type = None
        self.trade_price = 0
        self.quantity_of_shares = 0
        self.timestamp = datetime.now()

    def __str__(self):
        return f"type:{self.type}, price:{self.trade_price}, quantity:{self.quantity_of_shares}, time:{self.timestamp}"

    def set_trade_type(self, trade_type: str) -> None:
        self.type = trade_type  # trade type can be BUY or SELL

    def get_trade_type(self) -> str:
        return self.type

    def set_trade_price(self, trade_price: float) -> None:
        self.trade_price = trade_price

    def get_trade_price(self) -> float:
        return self.trade_price

    def set_quantity_shares(self, quantity: int) -> None:
        self.quantity_of_shares = quantity

    def get_quantity_shares(self) -> int:
        return self.quantity_of_shares

    def set_timestamp(self, timestamp: datetime):
        self.timestamp = timestamp

    def get_timestamp(self) -> datetime:
        return self.timestamp

class GBCEIndexModel:
    """
    Not in use quite yet
    """
    def __init__(self):
        self.index_constituents = set()