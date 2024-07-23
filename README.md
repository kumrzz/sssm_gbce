# Super Simple Stock Market : Global Beverage Corporation Exchange#

Description:
The Global Beverage Corporation Exchange is a new stock market trading in drinks companies.
Your company is building the object-oriented system to run that trading. 
You have been assigned to build part of the core object model for a limited phase 1.

This source code will -
- For a given stock:
    - calculate the dividend yield given any price as input
    - calculate the P/E Ratio given any price as input
    - record a trade, with timestamp, quantity of shares, buy or sell indicator and price
    - Calculate Volume Weighted Stock Price based on trades in past  5 minutes
- Calculate the GBCE All Share Index using the geometric mean of prices for all stocks

Constraints & Notes:
1.	No database or GUI, all data is held in memory.
2.	Formulas and data provided are simplified representations for the purpose of this exercise.

Global Beverage Corporation Exchange
Stock Symbol  | Type      |  Last Dividend| Fixed Dividend| Par Value
------------- | ----      | ------------: | :------------: | --------:
TEA           | Common    | 0             |                | 100
POP           | Common    | 8             |                | 100
ALE           | Common    | 23            |                | 60
GIN           | Preferred | 8             |         2%     | 100
JOE           | Common    | 13            |                | 250


Requirements:
- Python 3.10, Python 3.7 or higher should also work
- Tested on Windows11

Run:
Please ensure:
1. gbce_sample_data.csv file contains data as specified in current gbce_sample_data.csv file,
    it is read and populates in-memory database/model for further operations.
2. StocksDBFile.txt contains trade records, we operate on this while recording trade, calculating
    volume weighted stock price and GBCE all share index. If this file is not present,
    the code automatically handles it by creating one. The file is therefore OPTIONAL, NOT NECESSARY !!
3. Ensure main.py is present and then run as:
```
python main.py
```

Output on Console Window:

```
Select a number for corresponding operation:
                                1 for Calculating DIVIDEND yield.
                                2 for Calculating P/E ratio.
                                3 for Recording Trade.
                                4 for Calculating Volume Weighted Stock Price.
                                5 for Calculating the GBCE All Share Index.
                                0 to exit, if you are done with all the operations.
                                ===============================================
                                Enter number:
```

Tests:
To test the assignment using unittest, please execute test.py file as:
```
python test.py
```

Developer:
Kumar Ghosh
