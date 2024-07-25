import os, csv, pickle, sqlite3
from datetime import datetime, timedelta
from models import StockModel, TradeModel, GBCEIndexModel
import logging
from typing import List


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.basicConfig(filename='log_filename.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
stock_config_file = "gbce_sample_data.csv"

db_conn = sqlite3.connect(':memory:')
with db_conn:
    cur = db_conn.cursor()
    try:
        cur.execute("DROP TABLE IF EXISTS data")  # cleaning up
        cur.execute("CREATE TABLE data(i)")
    except Exception as why:
        logging.debug(why)


class FileDatabase:
    """
    memory(in-mem sqlite) and necessary file operations: i/o 
    """    
    trading_details = {}

    @staticmethod
    def load_stock_metadata_from_file(filename: str = stock_config_file) -> List[str | float]:
        """
        loads metadata such as symbol, type, last dividend from a predefined path
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(script_dir, filename)
        if not os.path.isfile(config_file):
            logging.warning("file not found, config will contain zero stocks")
            return []
        if os.stat(config_file).st_size == 0:
            logging.warning("file empty, config will contain zero stocks")
            return []        
        stock_details_list = list(csv.reader(open(config_file)))
        if stock_details_list[0][-1] == 'par_value':  # The first row contains headers
            stock_details_list = stock_details_list[1:]
        stock_details_list = [[row[0],row[1],float(row[2]),float(row[3]),float(row[4])] for row in stock_details_list]
        return stock_details_list

    @classmethod
    def write_activity_to_localmem(cls, trade_details={}):
        cls.trading_details = trade_details
        try:
            with db_conn:
                cur = db_conn.cursor()
                cur.execute("DELETE FROM data",)  # not necessary but prevents db from balooning into a monster
                cur.execute("INSERT INTO data VALUES(?)", (sqlite3.Binary(pickle.dumps(cls.trading_details)),))
                logging.info('trade activity now written to temp memory !')
                return True
        except Exception as why:
            logging.error(why)
            return False

    @classmethod
    def read_activity_from_localmem(cls):
        try:
            with db_conn:
                cur = db_conn.cursor()
                cur.execute("select i from data")
                db_content = [pickle.loads(row[0]) for row in cur]
                cls.trading_details = db_content[-1]  # final record contains the latest data
                return cls.trading_details
        except Exception as why:
            logging.warning("No record present in local memory: Please add trade records!")
            return cls.trading_details


class StockService:
    """
    settings calculations and operations on stocks
    """
    config_stocks_list = {}

    @classmethod
    def stock_config_operations(cls, stock_symbol, stock_type, last_dividend, fixed_dividend=0, par_value=0):
        stock_model_obj = StockModel()
        gbce_index_model_obj = GBCEIndexModel()
        stock_model_obj.set_stock_symbol(stock_symbol)
        gbce_index_model_obj.index_constituents.add(stock_symbol)
        stock_model_obj.set_stock_type(stock_type)
        stock_model_obj.set_last_dividend(last_dividend)
        stock_model_obj.set_fixed_dividend(fixed_dividend)
        stock_model_obj.set_par_value(par_value)
        cls.config_stocks_list[stock_symbol] = stock_model_obj

    @staticmethod
    def volume_weighted_stock_price(symbol: str, interval_in_mins = 5) -> tuple[str, float]:
        try:
            # reading file data to collect all the trade records until now
            trading_details = FileDatabase().read_activity_from_localmem()
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
            # No trades yet for provided stock symbol
            logging.warning(f"Trades for given stock symbol: {KE} have never been recorded! Please add records ... ")
            return "Failure", 0.0
        except ZeroDivisionError:
            # Either no trade is done in last 5 mins or calculation makes it 0.0.
            logging.warning(f"Either no trades located for {symbol} , or calculation results in 0.0 !!")
            vol_wt_price = 0
            return "Success", vol_wt_price

    @classmethod
    def calculate_dividend_yield(cls, stock_symbol: str, price: float) -> tuple[str, int]:
        if price < 0:
            logging.warning("Re-enter price, price can not be less or equal to zero!")
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
                logging.warning(ZDE)
                return "Failure", 0
        else:
            logging.warning("Stock not located for Dividend calc, please enter stock that's already in activity/memory !")
            return "Failure", 0
    
    @classmethod
    def calculate_pe_ratio(cls, stock_symbol: str, price: float):
        # calculate dividend for given price and stock
        try:
            stock_detail = cls.config_stocks_list[stock_symbol]
        except KeyError as KE:
            logging.warning(KE)
            return "Failure", 0
        last_dividend = stock_detail.get_last_dividend()
        try:
            # can't use dividend yield here as that is already a fraction of the price !
            pe_ratio = price / last_dividend
        except ZeroDivisionError as ZDE:
            # dividend can be zero, resulting in pe_ratio of zero
            pe_ratio = 0
        return "Success", pe_ratio


class TradeService:
    """
    Records trades (activity) on stocks
    """

    @staticmethod
    def record_trade(symbol, quantity, buy_or_sell, trade_price, timestamp=datetime.now()) -> str:
        """
        Writes trade activity to local memory
        """
        if symbol not in StockService.config_stocks_list:
            logging.warning(f"Stock symbol {symbol} not present in index config file({stock_config_file}) provided!")
            return "Failure"
        try:
            # read from file/db
            file_obj = FileDatabase()
            trading_details = file_obj.read_activity_from_localmem()

            trade_model_obj = TradeModel()
            trade_model_obj.set_quantity_shares(quantity)
            trade_model_obj.set_trade_type(buy_or_sell)
            trade_model_obj.set_trade_price(trade_price)
            trade_model_obj.set_timestamp(timestamp)
            if not trading_details or symbol not in trading_details:
                trading_details[symbol] = {}
            trading_details[symbol][timestamp] = trade_model_obj

            # write to file/db
            file_obj.write_activity_to_localmem(trading_details)
            return "Success"

        except Exception as Except:
            logging.warning(Except)
            return "Failure"

class GBCEIndex:
    """
    Calculations on the Global Beverage Corporation Exchange Index
    """
    trading_details = {}

    @classmethod
    def all_share_index(cls) -> float:
        """
        calculates a geometric mean of the Volume Weighted Stock Price for all stocks in the GBCE
        note this V-W price is NOT for 5mins only, it's for the whole population!
        """
        cls.trading_details = FileDatabase().read_activity_from_localmem()
        if not cls.trading_details:
            logging.warning("Empty records, no trade done!")
            return None
        total_stock_count = 0
        total_price = 0

        for stock in cls.trading_details:
            for time, traded_share in cls.trading_details[stock].items():
                total_stock_count += traded_share.get_quantity_shares()
                total_price += (traded_share.get_quantity_shares() * traded_share.get_trade_price())

        gbce_all_share_index = pow(total_price, 1/total_stock_count) 

        return gbce_all_share_index
