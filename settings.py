################################
## Data Files and Directories ##
################################

#Data Locations
MAIN_DATA_DIR = 'data'
RAW_DATA_DIR = 'raw_data'
EXTRACTED_DATA_DIR = 'extracted_data'

#Path Names
RAW_DATA_PATH = "{0}/{1}".format(MAIN_DATA_DIR, RAW_DATA_DIR)
EXTRACTED_DATA_PATH = "{0}/{1}".format(MAIN_DATA_DIR, EXTRACTED_DATA_DIR)


###############################
## Log Files and Directories ##
###############################

#Log Locations
MAIN_LOG_DIR = 'logs'

#Log Master File
LOG_EXT = "p"
SCRAPE_LOG_FILE = "scrape_log"
EXTRACT_LOG_FILE = "extract_log"

#Log Master File Path
SCRAPE_LOG_FILE_PATH = "{0}/{1}.{2}".format(MAIN_LOG_DIR, SCRAPE_LOG_FILE, LOG_EXT)
EXTRACT_LOG_FILE_PATH = "{0}/{1}.{2}".format(MAIN_LOG_DIR, EXTRACT_LOG_FILE, LOG_EXT)


######################################################
## Scrape Lists and Reference Files and Directories ##
######################################################

#Scrape List Locations
MAIN_SCRAPE_LIST_DIR = 'scrape_lists'
STOCK_EXCHANGE_LIST_DIR = 'stock_exchanges'

#Xbrl
XBRL_TAXONOMY_LIST_DIR = 'xbrl_taxonomy'
XBRL_TAXONOMY_ELEMENTS_DIR = 'xbrl_elements'
XBRL_TAXONOMY_CALCS_DIR = 'xbrl_calculations'


OTHER_SCRAPE_LIST_DIR = 'other_scrapes'

#If XBRL already extracted
XBRL_DICT_DIR = 'xbrl_dict'
XBRL_DICT_FILENAME = 'xbrl_dict.p'

#Path Names
STOCK_EXCHANGE_LIST_PATH = "{0}/{1}".format(MAIN_SCRAPE_LIST_DIR,
											STOCK_EXCHANGE_LIST_DIR)
											 
XBRL_TAXONOMY_LIST_PATH = "{0}/{1}".format(MAIN_SCRAPE_LIST_DIR,
										   XBRL_TAXONOMY_LIST_DIR)
											
XBRL_ELEMENTS_PATH = "{0}/{1}/{2}".format(MAIN_SCRAPE_LIST_DIR,
									      XBRL_TAXONOMY_LIST_DIR,
									      XBRL_TAXONOMY_ELEMENTS_DIR)
									  
XBRL_CALCS_PATH = "{0}/{1}/{2}".format(MAIN_SCRAPE_LIST_DIR,
									   XBRL_TAXONOMY_LIST_DIR,
									   XBRL_TAXONOMY_CALCS_DIR)
											

											
XBRL_DICT_PATH = "{0}/{1}/{2}/{3}".format(MAIN_SCRAPE_LIST_DIR,
										  XBRL_TAXONOMY_LIST_DIR,
										  XBRL_DICT_DIR,
										  XBRL_DICT_FILENAME)

#####################
## Scraper Options ##
#####################
GET_XML = True
GET_TXT = False
GET_HTML = False
GET_XL = False

#####################
## Extract Options ##
#####################
OUTPUT_PICKLE = True
OUTPUT_JSON = False

###########
## URLs ###
###########

LINK_URL = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={0}&type={1}&dateb=&owner=exclude&count=100"









