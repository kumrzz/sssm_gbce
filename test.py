import random
import unittest
from services import StockService, TradeService, GBCEIndex, FileDatabase


class TestHardcodedCases(unittest.TestCase):
    symbols = ["TEA", "POP", "ALE", "GIN", "JOE"]
    buy_or_sell = ["BUY", "SELL"]
    quantities = range(0, 1000, 5)
    prices = [5, 827, 47, 29.6, 1, 932, 10000]

    def setUpClass():
        StockService().stock_config_operations('RUM','Common',5)
    
    def test_record_trade_manualinputs(self):
        status = TradeService.record_trade(symbol="RUM", quantity=100, buy_or_sell="BUY", trade_price=499)            
        self.assertEqual(status, "Success", "error in TradeService.record_trade")
        status = TradeService.record_trade(symbol="RUM", quantity=100000, buy_or_sell="BUY", trade_price=500)            
        self.assertEqual(status, "Success", "error in TradeService.record_trade")           

    def test_volume_weighted_stock_price_manualinputs(self):
        print('\n')
        status, vwsp = StockService.volume_weighted_stock_price("RUM")
        print(f"(5min)Volume-weighted Stock price for {"RUM"}: {vwsp}")
        self.assertEqual(vwsp, 500, "error in StockService.volume_weighted_stock_price calc")
    
    def test_dividend_yield_calc_manualinputs(self):
        print('\n')
        status, divi_yield = StockService.calculate_dividend_yield("RUM", 50)
        print(f"Dividend yield for RUM @ 50 : {divi_yield}")
        self.assertEqual(divi_yield, 0.1, "error in StockService.calculate_dividend_yield")

    def test_pe_ratio_calc_manualinputs(self):
        print('\n')
        status, pe_ratio = StockService.calculate_pe_ratio("RUM", 50)
        print(f"P/E Ratio for {"RUM"} @50 : {pe_ratio}")
        self.assertEqual(pe_ratio, 10, "P/E Ratio calc error in StockService.calculate_pe_ratio")


class TestBaseCases(unittest.TestCase):
    symbols = ["TEA", "POP", "ALE", "GIN", "JOE"]
    buy_or_sell = ["BUY", "SELL"]
    quantities = range(0, 1000, 5)
    prices = [5, 827, 47, 29.6, 1, 932, 10000]
    
    def test_record_trade(self):
        for _ in range(4):
            temp_trade = random.choice(self.symbols), random.choice(self.quantities), random.choice(self.buy_or_sell), random.choice(self.prices)
            print("trade: ", temp_trade)
            status = TradeService.record_trade(*temp_trade)            
            self.assertEqual(status, "Success", "error in TradeService.record_trade")           

    def test_volume_weighted_stock_price(self):
        print('\n')
        trading_details = FileDatabase.read_activity_from_localmem()
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


class TestExpectedFailCases(unittest.TestCase):
    bad_ticker = 'IMPOSSIBLERANDOMSTOCK'
    buy_or_sell = ["BUY", "SELL"]
    quantities = range(0, 1000, 5)
    prices = [5, 827, 47, 29.6, 1, 932, 10000]

    def test_record_trade_failure(self):
        temp_trade = self.bad_ticker, random.choice(self.quantities), random.choice(self.buy_or_sell), random.choice(self.prices)
        print("trade: ", temp_trade)
        status = TradeService.record_trade(*temp_trade)
        self.assertEqual(status, "Failure", f"Trade in {self.bad_ticker} should have failed, it did not!")
    
    def test_volume_weighted_stock_price_failure(self):
        print('\n')
        status, vwsp = StockService.volume_weighted_stock_price(self.bad_ticker)
        self.assertEqual(status, "Failure", "StockService.volume_weighted_stock_price calc did not fail for {self.bad_ticker}")
    
    def test_dividend_yield_calc_failure(self):
        print('\n')
        status, divi_yield = StockService.calculate_dividend_yield(self.bad_ticker, random.choice(self.prices))
        self.assertEqual(status, "Failure", "StockService.calculate_dividend_yield didn't fail for {self.bad_ticker}")

    def test_pe_ratio_calc_failure(self):
        print('\n')
        status, pe_ratio = StockService.calculate_pe_ratio(self.bad_ticker, random.choice(self.prices))
        self.assertEqual(status, "Failure", "StockService.calculate_pe_ratio didn't fail for {self.bad_ticker}")


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
        suite.addTest(TestExpectedFailCases('test_record_trade_failure'))
        suite.addTest(TestExpectedFailCases('test_volume_weighted_stock_price_failure'))
        suite.addTest(TestExpectedFailCases('test_dividend_yield_calc_failure'))
        suite.addTest(TestExpectedFailCases('test_pe_ratio_calc_failure'))
        suite.addTest(TestHardcodedCases('test_record_trade_manualinputs'))
        suite.addTest(TestHardcodedCases('test_volume_weighted_stock_price_manualinputs'))
        suite.addTest(TestHardcodedCases('test_dividend_yield_calc_manualinputs'))
        suite.addTest(TestHardcodedCases('test_pe_ratio_calc_manualinputs'))
        return suite

    stock_details_list = FileDatabase.load_stock_metadata_from_file()
    for stock in stock_details_list:
        StockService().stock_config_operations(*stock)
    print("\nStock config/metadata populated from file for testing!")
    
    custom_suite = suite()
    runner = unittest.TextTestRunner()
    runner.run(custom_suite)