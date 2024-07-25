from services import GBCEIndex, StockService, TradeService, FileDatabase

def input_operations():
    """Input/Output Interaction
    Interacts with user for input and provides appropriate output.
    1. Enter a stock symbol
    2. Select the operation to be performed
    3. View/Check the output
    """
    # Populate DB
    stock_details_list = FileDatabase.load_stock_metadata_from_file()
    for stock in stock_details_list:
        StockService().stock_config_operations(*stock)
    config_stocks_list = [row[0] for row in stock_details_list]
    for stock in stock_details_list:
            StockService().stock_config_operations(*stock)
    print("Stock config/metadata populated from file")

    operations = """Select a number for corresponding operation:
                    1 for Calculating DIVIDEND yield.
                    2 for Calculating P/E ratio.
                    3 for Recording Trade.
                    4 for Calculating Volume Weighted Stock Price.
                    5 for Calculating the GBCE All Share Index.
                    0 to exit, if you are done with all the operations.
                    ===============================================
                    Enter number:"""
    list_of_stocks = f"""Select one stock symbol from:
                            {config_stocks_list}
                            ===================
                            Enter one of the above strings:"""
    enter_stock_price = "Enter stock price:"
    enter_stock_quantity = "Enter stock quantity:"
    re_enter = "Please enter correct data!"
    success = "Success"

    while True:
        try:
            # operation_num tells us the operation we wish to perform
            operation_num = int(input(operations))
            # exit
            if operation_num == 0:
                print("bye!")
                break
            elif operation_num == 1:
                print("You have selected to calculate Dividend yield!")
                stock_symbol = input(list_of_stocks).upper()
                stock_price = float(input(enter_stock_price))
                status, dividend_yield = StockService.calculate_dividend_yield(stock_symbol, stock_price)
                if status == success:
                    print(f"Dividend yield for {stock_symbol} at {stock_price} is:  {dividend_yield}")
                else:
                    print(status)
                    print(re_enter)

            elif operation_num == 2:
                print("You have selected to calculate P/E ratio!")
                stock_symbol = input(list_of_stocks).upper()
                stock_price = float(input(enter_stock_price))
                status, pe_ratio = StockService.calculate_pe_ratio(stock_symbol, stock_price)
                if status == success:
                    print(f"P/E ratio for {stock_symbol} at {stock_price} is:{pe_ratio}")
                else:
                    print(status)
                    print(re_enter)

            elif operation_num == 3:
                print("You have selected to Record Trade!")
                stock_symbol = input(list_of_stocks).upper()
                stock_quantity = int(input(enter_stock_quantity))
                buy_or_sell = input("Enter BUY, if you wish to buy stock else SELL:")
                buy_or_sell = buy_or_sell.upper()
                stock_price = float(input(enter_stock_price))
                # record traded stock
                if buy_or_sell not in {"BUY", "SELL"}:
                    print(re_enter)
                    continue
                status = TradeService.record_trade(stock_symbol, stock_quantity, buy_or_sell, stock_price)
                if status == success:
                    print(f"The trade for {buy_or_sell} of {stock_symbol} has now been recorded.")
                else:
                    print(re_enter)

            elif operation_num == 4:
                print("You have selected to calculate Volume Weighted Stock Price of last 5 mins!")
                stock_symbol = input(list_of_stocks).upper()
                status, vol_wt_stock_price = StockService.volume_weighted_stock_price(stock_symbol)
                if status == success:
                    print(f"Volume Weighted Stock Price for {stock_symbol} is:{vol_wt_stock_price}")
                else:
                    print(re_enter)

            elif operation_num == 5:
                print("You have selected to calculate GBCE All Share Index!")
                gbce = GBCEIndex.all_share_index()
                if gbce:
                    print("GBCE All Share Index:", gbce)

            else:
                print("Please try again, your selection of numbers may not be one of those expected!!!")
        except ValueError as VE:
            print(VE)
            print(re_enter)
        except UnboundLocalError as ULE:
            print(ULE)
            print(re_enter)
        except Exception as EXCEPT:
            print(EXCEPT)
            print(re_enter)

if __name__ == '__main__':
    input_operations()