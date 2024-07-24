import os, csv, pickle
from datetime import datetime, timedelta
from models import StockModel, TradeModel


class FileDatabase:
    """
    File operations: i/o
    """
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "StocksDBFile.txt")
    print("'database' filepath:", file_path)
    trading_details = {}

    @classmethod
    def write_activity_to_file(cls, trade_details={}):
        cls.trading_details = trade_details
        with open(cls.file_path, 'wb') as db:
            db.write(pickle.dumps(cls.trading_details))
            print("trade activity now written to File!")

    @classmethod
    def read_activity_from_file(cls):
        try:
            with open(cls.file_path, 'rb') as db:
                read_db = db.read()
                cls.trading_details = pickle.loads(read_db)
                # print("Trade records read as:", cls.trading_details)
            return cls.trading_details
        except FileNotFoundError:
            FileDatabase().write_activity_to_file()
            print("No record present in file: Please add trade records!")
            return cls.trading_details
    
    def load_stock_config_from_file(filename= "gbce_sample_data.csv"):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(script_dir, filename)
        if not os.path.isfile(config_file):
            print("file not found, config will contain zero stocks")
            return []
        if os.stat(config_file).st_size == 0:
            print("file empty, config will contain zero stocks")
            return []        
        stock_details_list = list(csv.reader(open(config_file)))
        if stock_details_list[0][-1] == 'par_value':  # The first row contains headers
            stock_details_list = stock_details_list[1:]
        stock_details_list = [[row[0],row[1],float(row[2]),float(row[3]),float(row[4])] for row in stock_details_list]
        return stock_details_list


class StockService:
    """
    settings calculations and operations on individual stocks
    """
    config_stocks_list = {}

    @classmethod
    def stock_config_operations(cls, stock_symbol, stock_type, last_dividend, fixed_dividend=0, par_value=0):
        stock_model_obj = StockModel()
        stock_model_obj.set_stock_symbol(stock_symbol)
        stock_model_obj.set_stock_type(stock_type)
        stock_model_obj.set_last_dividend(last_dividend)
        stock_model_obj.set_fixed_dividend(fixed_dividend)
        stock_model_obj.set_par_value(par_value)
        cls.config_stocks_list[stock_symbol] = stock_model_obj
    
    @staticmethod
    def volume_weighted_stock_price(symbol: str, interval_in_mins = 5) -> tuple[str, float]:
        try:
            # reading file's data to collect all the trade records until now
            trading_details = FileDatabase().read_activity_from_file()
            # filtering out the data, gives data for the stock symbol we need
            symbol_trade_details = trading_details[symbol]

            difference_datetime = datetime.now() - timedelta(minutes=interval_in_mins)
            total_quantity_shares = 0
            share_quantity_trade_sum = 0
            # calculates volume weighted trade for given stock symbol and returns it
            for time, trade_obj in symbol_trade_details.items():
                if time >= difference_datetime:
                    total_quantity_shares += trade_obj.get_quantity_shares()
                    share_quantity_trade_sum += (trade_obj.get_quantity_shares() * trade_obj.get_trade_price())
            vol_wt_price = share_quantity_trade_sum / total_quantity_shares
            return "Success", vol_wt_price
        except KeyError as KE:
            # No trade is done for provided stock symbol
            print(KE)
            print("Trade record for given stock symbol has never been recorded! Please add records ... ")
            return "Failure", 0.0
        except ZeroDivisionError:
            # Either no trade is done in last 5 mins or calculation makes it 0.0.
            print(f"Either no trades located for {symbol} , or calculation results in 0.0 !!")
            vol_wt_price = 0
            return "Success", vol_wt_price

    @classmethod
    def calculate_dividend_yield(cls, stock_symbol: str, price: float) -> tuple[str, int]:
        if price < 0:
            print("Re-enter price, price can not be less or equal to zero!")
            return "Failure", 0

        # check if stock_symbol is present in list of stocks
        stock_present = False
        if stock_symbol in cls.config_stocks_list:
            stock_present = True

        if stock_present:
            stock_detail = cls.config_stocks_list[stock_symbol]
            try:
                if stock_detail.get_stock_type() == "Common":
                    last_dividend = stock_detail.get_last_dividend()
                    dividend_yield = last_dividend / price
                else:
                    fixed_dividend = stock_detail.get_fixed_dividend()
                    par_value = stock_detail.get_par_value()
                    dividend_yield = (fixed_dividend * par_value) / price
                return "Success", dividend_yield
            except ZeroDivisionError as ZDE:
                print(ZDE)
                return "Failure", 0
        else:
            print("Stock is not present in Memory, please enter stock that's already in memory!")
            return "Failure", 0
    
    @classmethod
    def calculate_pe_ratio(cls, stock_symbol: str, price: float):

        # calculate dividend for given price and stock
        status, dividend = cls.calculate_dividend_yield(stock_symbol, price)
        if status == "Failure":
            return "Failure", 0
        else:
            try:
                pe_ratio = price / dividend
            except ZeroDivisionError as ZDE:
                # considering dividend can be zero resulting in pe_ratio as zero
                pe_ratio = 0
            return "Success", pe_ratio


class TradeService:
    """
    Records trades (activity) on stocks
    """

    @staticmethod
    def record_trade(symbol, quantity, buy_or_sell, trade_price, timestamp=datetime.now()) -> str:
        if symbol not in StockService.config_stocks_list:
            print("Stock symbol is not present in the excel file provided!")
            return "Failure"
        try:
            # read from file/db
            file_obj = FileDatabase()
            trading_details = file_obj.read_activity_from_file()

            trade_model_obj = TradeModel()
            trade_model_obj.set_quantity_shares(quantity)
            trade_model_obj.set_trade_type(buy_or_sell)
            trade_model_obj.set_trade_price(trade_price)
            trade_model_obj.set_timestamp(timestamp)
            if not trading_details or symbol not in trading_details:
                trading_details[symbol] = {}
            trading_details[symbol][timestamp] = trade_model_obj

            # write to file/db
            file_obj.write_activity_to_file(trading_details)
            return "Success"

        except Exception as Except:
            print(Except)
            return "Failure"

class GBCEIndex:
    """
    Calculations on the Global Beverage Corporation Exchange Index
    """
    trading_details = {}

    @classmethod
    def all_share_index(cls):
        cls.trading_details = FileDatabase().read_activity_from_file()
        if not cls.trading_details:
            print("Empty records, no trade done!")
            return None
        total_stock_count = 0
        total_price = 0
        for stock in cls.trading_details:
            for time, traded_share in cls.trading_details[stock].items():
                total_stock_count += traded_share.get_quantity_shares()
                total_price += (traded_share.get_quantity_shares() * traded_share.get_trade_price())

        #note this WV price is NOT for 5mins only, it's for the whole population!
        gbce_all_share_index = pow(total_price, 1/total_stock_count) 

        return gbce_all_share_index
