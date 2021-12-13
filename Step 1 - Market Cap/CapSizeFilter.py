import yfinance as yf
import csv 
import concurrent.futures

#! Put non functions into main function so that this file can be imported later 

# to update this csv list, go to https://www.nasdaq.com/market-activity/stocks/screener?exchange=NASDAQ&render=download
# download the list, go to numbers, delete all the columns other than symbol
# doing this is necessary to get tickers that go in and out of market cap range but not really that important
nasdaqTickers = "Step 1 - Market Cap/NASDAQ 50M to 200B as of NOV 19 2021.CSV"
nyseTickers = "Step 1 - Market Cap/NYSE Market Cap between 50M and 200B.CSV"

#! If you wanted to not have to go and download and manually edit data everytime,
#! you could just download every ticker on nasdaq and nyse and let the program parse 
#! every ticker every time you want to run again. Would be slower but easier

tickers = []

# open data on nasdaq and nyse tickers and add both to tickers list 
with open(nasdaqTickers, 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        ticker = row[-2]
        tickers.append(ticker)

with open(nyseTickers, 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        ticker = row[-2]
        tickers.append(ticker)


print(f"Number of tickers before: {len(tickers)}")

class TickerFilterer():
    '''Concurrently filters tickers by market cap into a new list '''
    def __init__(self, tickers, filteredTickers=[]):
        self.tickers = tickers 
        self.filteredTickers = []
    
    def calculation(self, i):
        try:
            print(f"Began calculating ticker #{i+1} out of {len(self.tickers)-1} tickers")
            ticker = yf.Ticker(self.tickers[i])
            marketCap = ticker.info['marketCap']
            if marketCap > 100_000_000 and marketCap < 100_000_000_000:
                self.filteredTickers.append(self.tickers[i])
            
        except TypeError:
            print(f"[TypeError]: Ticker #{i+1} did not have data on market cap and was not included in filtered list")
            
        except KeyError:
            print(f"[KeyError]: Ticker #{i+1} did not have data on market cap and was not included in filtered list")

    def filterTickersByMarketCap(self): 
        """     
        Runs the market cap calculation concurrently using threads
        """
        tickersLength = len(self.tickers) - 1
        with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor: # 100 max workers likely not ideal... 1000 sometimes works faster but can get stuck
            executor.map(self.calculation, range(tickersLength))
        
        print("FINISHED CALCULATING TICKERS (OR AT LEAST CREATING THE THREADS FOR THEM)")


    def getFilteredTickers(self):
        return self.filteredTickers  


# create filter object to filter the data
FilterObject = TickerFilterer(tickers)
FilterObject.filterTickersByMarketCap()

print(f"Number of tickers after: {len(FilterObject.getFilteredTickers())}")
tickersCapSizeFiltered = FilterObject.getFilteredTickers()
tickersCapSizeFiltered.sort()
print(f"Repeated tickers in filtered list: {len(tickersCapSizeFiltered) != len(set(tickersCapSizeFiltered))}")
print(tickersCapSizeFiltered)
print("Done calculating, writing csvFile")

# this makes each ticker into its own list to make writing a csv easier
def makeListOfLists(list):
    return [[element] for element in list]

tickersCapSizeFiltered = makeListOfLists(tickersCapSizeFiltered)

# writes list into a csv file
with open("FilteredTickers.csv", 'w') as csvfile: 
    csvwriter = csv.writer(csvfile) 
    csvwriter.writerows(tickersCapSizeFiltered) 

print("finished")
