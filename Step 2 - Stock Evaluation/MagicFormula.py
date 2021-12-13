import yfinance as yf
import pandas as pd
import csv
import concurrent.futures 

class Stock():
    '''Creates data type with earnings yield and return on capital for a stock'''
    def __init__(self, ticker, earningsYield, returnOnCapital): 
        self.ticker = ticker
        self.earningsYield = earningsYield
        self.returnOnCapital = returnOnCapital
        self.earningsRanking = 100000 # p/e "trailingPE" (inverse of P/E for yearnings yield)
        self.capitalRanking = 100000 # return on assests "returnOnAssets"
        self.combinedRanking = 10000
    
    def __repr__(self):
        return (f"RANKING: {self.combinedRanking}, Ticker: {self.ticker}, Earnings Yield: {self.earningsYield}, Return on Capital: {self.returnOnCapital}, EarnRank: {self.earningsRanking}, CapRank: {self.capitalRanking},\n\n")
    
    '''
    def __lt__
    def __gt__
    can use these to define how to sort stock object if needed (instead of using a key= in sort function)
    '''
    
    def getTicker(self):
        return self.ticker
    
    def getEarningsYield(self):
        return self.earningsYield
    
    def getReturnOnCapital(self):
        return self.returnOnCapital
    
    def setEarningsRanking(self, ranking):
        self.earningsRanking = ranking
    
    def setCapitalRanking(self, ranking):
        self.capitalRanking = ranking
    
    def getCombinedRanking(self):
        self.combinedRanking = self.earningsRanking + self.capitalRanking
        return self.earningsRanking + self.capitalRanking

class StockDataAssigner():
    def __init__(self, tickers):
        self.tickers = tickers
        self.stockObjectList = []
    
    def assignTickerDataToObject(self, i): # use list of tickers from function above as input
        error = False
        try:
            # create list of stock objects with earnings yield and return on assets data 
            print(f"Began calculating and assigning financial data for ticker #{i+1} out of {len(self.tickers)} tickers")
            stockTicker = self.tickers[i]
            tickerObject = yf.Ticker(stockTicker)
            stockPE = tickerObject.info['trailingPE'] ** -1 # inverse of PE = earnings yield
            stockCapital = tickerObject.info['returnOnAssets']
            
        except KeyError:
            error = True
            print("KeyError")
        except TypeError:
            error = True
            print("TypeError")
        finally:
            if not error and stockPE != None and stockCapital != None:
                StockObject = Stock(stockTicker, stockPE, stockCapital)
                self.stockObjectList.append(StockObject)
        error = False
        
    def threadingDataAssignment(self):
        #! Try asyncio instead (see youtube video in python saved videos )
        with concurrent.futures.ThreadPoolExecutor(max_workers=400) as executor: # 400 max workers likely not ideal... 1000 sometimes works faster but can get stuck
                executor.map(self.assignTickerDataToObject, range(len(self.tickers)-1))
    
    def getStockObjectList(self):
        return self.stockObjectList


def makeListOfListsIntoList(list):
    return [item for sublist in list for item in sublist]


def rankStocks(stockObjectList): 
    '''Ranks stocks based off return on capital and earnings yield and then adds this data to the stock objects'''
    capitalRankedList = sorted(stockObjectList, key=rankReturnOnCapital, reverse=True)
    earningsRankedList = sorted(stockObjectList, key=rankEarningsYield, reverse=True)
    
    for i in range(len(stockObjectList)-1):
        capitalRankedList[i].setCapitalRanking(i)
        earningsRankedList[i].setEarningsRanking(i)
    
    magicFormulaRankedList = sorted(stockObjectList, key=magicFormula)
    
    return magicFormulaRankedList

def rankReturnOnCapital(stockObject):
    return stockObject.getReturnOnCapital()

def rankEarningsYield(stockObject):
    return stockObject.getEarningsYield()

def magicFormula(stockObject):
    return stockObject.getCombinedRanking()

def main():
    # microsoft = yf.Ticker('MSFT')
    # dict =  microsoft.info
    # df = pd.DataFrame.from_dict(dict,orient='index')
    # # df = df.reset_index()
    # pd.set_option("display.max_rows", None, "display.max_columns", None)
    # print(df)
    
    tickers = []
    CSVtickers = "Step 1 - Market Cap/FilteredTickers.csv"
    # creates list of lists with tickers
    with open(CSVtickers, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            tickers.append(row)
            
    # turns into regular list
    tickers = makeListOfListsIntoList(tickers)
    
    # create data assigner that goes through and gets financial data from yahoo and assigns to stock object
    DataAssignment = StockDataAssigner(tickers)
    DataAssignment.threadingDataAssignment()
    
    
    # print(DataAssignment.getStockObjectList())
    print("Calculations Done\n-----------------------------------")
    
    magicFormulaRankedStocks = rankStocks(DataAssignment.getStockObjectList())
    
    # create new list with top 30 magic formula ranked stocks
    top35 = []
    for i in range(35):
        top35.append(magicFormulaRankedStocks[i])
    
    print(top35)
     

if __name__ == '__main__':
    main()
    