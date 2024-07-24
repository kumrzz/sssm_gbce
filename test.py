import random
import unittest
from services import StockService, TradeService, GBCEIndex, FileDatabase


class TestBaseCases(unittest.TestCase):
    symbols = ["TEA", "POP", "ALE", "GIN", "JOE"]
    buy_or_sell = ["BUY", "SELL"]
    quantities = range(0, 1000, 5)
    prices = [5, 827, 47, 29.6, 1, 932, 10000]

    @classmethod
    def setUpClass(cls):        
        stock_details_list = FileDatabase.load_stock_config_from_file()
        for stock in stock_details_list:
            StockService().stock_config_operations(*stock)
        print("local pickled DB file populated!!")
    
    def test_record_trade(self):
        print('\n')
        for _ in range(4):
            temp_trade = random.choice(self.symbols), random.choice(self.quantities), random.choice(self.buy_or_sell), random.choice(self.prices)
            print("trade: ", temp_trade)
            status = TradeService.record_trade(*temp_trade)            
            self.assertEqual(status, "Success", "error in TradeService.record_trade")            

    def test_volume_weighted_stock_price(self):
        print('\n')
        trading_details = FileDatabase.read_activity_from_file()
        for symbol in self.symbols:
            if symbol in trading_details:
                status, vwsp = StockService.volume_weighted_stock_price(symbol)
                print(f"(5min)Volume-weighted Stock price for {symbol}: {vwsp}")
                self.assertEqual(status, "Success", "error in StockService.volume_weighted_stock_price calc")
    
    def test_dividend_yield_calc(self):
        print('\n')
        for symbol in self.symbols:
            status, divi_yield = StockService.calculate_dividend_yield(symbol, random.choice(self.prices))
            print(f"Dividend yield for {symbol}: {divi_yield}")
            self.assertEqual(status, "Success", "error in StockService.calculate_dividend_yield")

    def test_pe_ratio_calc(self):
        print('\n')
        for symbol in self.symbols:
            input_price = random.choice(self.prices)
            status, pe_ratio = StockService.calculate_pe_ratio(symbol, input_price)
            print(f"P/E Ratio for {symbol} @ {input_price} : {pe_ratio}")
            self.assertEqual(status, "Success", "P/E Ratio calc error in StockService.calculate_pe_ratio")

    @classmethod
    def test_gbce_index(cls):
        print('\n')
        print("GBCE All Share index valuation:", GBCEIndex.all_share_index())


if __name__ == '__main__':    
    def suite():
        """
            Gather all the tests from this module in a test suite and run in specific order.
        """
        suite = unittest.TestSuite()
        suite.addTest(TestBaseCases('test_record_trade'))
        suite.addTest(TestBaseCases('test_volume_weighted_stock_price'))
        suite.addTest(TestBaseCases('test_dividend_yield_calc'))
        suite.addTest(TestBaseCases('test_pe_ratio_calc'))
        suite.addTest(TestBaseCases('test_gbce_index'))
        return suite

    custom_suite = suite()
    runner = unittest.TextTestRunner()
    runner.run(custom_suite)