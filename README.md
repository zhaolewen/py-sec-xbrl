# py-sec-xbrl
SEC Edgar Parser based on Python 3

The repository is forked from https://github.com/tooksoi/ScraXBRL but I've decided to focus on the parsing part in this repository to simplify stuff, as it varies a lot as to how you want to do the scrapping and it's relatively easier.

Thus 2 priorities for the moment:
1. Simplify scripts to parse SEC XBRL xml files
2. Make the scripts ready as a library that can be installed

To use:<br>
1. Install requirements from requirements.txt<br>
2. Change settings.py to fit your needs. Raw scraped data will be stored in data/raw_data and<br>
   extracted data will be stored in data/extracted_data by default.<br>
3. Run python main.py. This will begin the scrape and extract process.<br>
4. To view data in terminal (data must have already been scraped from the SEC EDGAR website):
![alt tag](https://raw.githubusercontent.com/computerpencils/ScraXBRL/master/aapl20130629.png)
Data is stored in a pickle file. To use DataViewer, create instance of DataView class and enter<br>
the necessary parameters (ticker_symbol, filing_date, filing_type). The data will then be stored in<br>
[instance name].data, and it is an OrderedDict.
