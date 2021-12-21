import yfinance as yf
import pandas as pd
import csv
import concurrent.futures 
import asyncio

'''
Replace concurrent futures' threading with asyncio asynchronous code - should increase speed

'''


#! NOT POSSIBLE

'''
I have checked documentation of yfinance and see requests library in requirements, the library ins not async. 
It means that you should not use it with asyncio module, 
you should use theading.Thread or concurrent.futures.ThreadPoolExecutor instead.
'''



















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
    
    #TODO look up how to use asyncio with an api i think the problem is not being able to say await on the api calls cause of the library
    async def assignTickerDataToObject(self, i): # use list of tickers from function above as input
        error = False
        #! creates a TypeError for every stock, might be because the variables get all mixed up in the event loop because it doesn't wait for stockPe and stockCapital ??
        try:
            # create list of stock objects with earnings yield and return on assets data 
            print(f"Began calculating and assigning financial data for ticker #{i+1} out of {len(self.tickers)} tickers")
            stockTicker = self.tickers[i]
            tickerObject = yf.Ticker(stockTicker)
            stockPE = tickerObject.info['trailingPE'] ** -1 # inverse of PE = earnings yield
            stockCapital = tickerObject.info['returnOnAssets']
            '''Making these two three lines await makes program really fast but raises type error
            Also, i don't think you can do await on object calls and dictionary calls so maybe that's why'''

        except KeyError:
            error = True
            print(f"KeyError #{i+1}")
        except TypeError:
            error = True
            print(f"TypeError #{i+1}")
            # raise TypeError
        finally:
            if not error and stockPE != None and stockCapital != None:
                StockObject = Stock(stockTicker, stockPE, stockCapital)
                self.stockObjectList.append(StockObject)
                print(f"SUCCESS #{i+1}")
        error = False
        '''
        maybe run this whole block in sequence for each iteration and then run all the iterations in parallel
        see ArjanCodes asynchronous tutorial on youtube 
        '''
    
    async def assignTickerDataToObjectTEST(self, i):
        await asyncio.sleep(2)
        print(i)
        
    async def asyncDataAssignment(self):
        await asyncio.gather(*[self.assignTickerDataToObject(i) for i in range(len(self.tickers))])
        

    
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
    asyncio.run(DataAssignment.asyncDataAssignment())
    
    
    # print(DataAssignment.getStockObjectList())
    print("Calculations Done\n-----------------------------------")
    
    magicFormulaRankedStocks = rankStocks(DataAssignment.getStockObjectList())
    
    # create new list with top 35 magic formula ranked stocks
    top35 = []
    for i in range(35):
        top35.append(magicFormulaRankedStocks[i])
    
    print(top35)
     

if __name__ == '__main__':
    main()
    