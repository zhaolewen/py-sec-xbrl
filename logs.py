import settings
import os
import pickle
from collections import OrderedDict

if not os.path.exists(settings.SCRAPE_LOG_FILE_PATH):
	data_log = OrderedDict()
	pickle.dump(data_log, open(settings.SCRAPE_LOG_FILE_PATH, "wb"))
if not os.path.exists(settings.EXTRACT_LOG_FILE_PATH):
	data_log = OrderedDict()
	pickle.dump(data_log, open(settings.EXTRACT_LOG_FILE_PATH, "wb"))

def add_scrape_data(symbol, scrape_data, complete):
	"""Add data regarding scrape to scrape log."""
	
	if complete:
		complete_key = 'complete'
	else:
		complete_key = 'incomplete'
	data_log = pickle.load(open(settings.SCRAPE_LOG_FILE_PATH, "rb"))
	try:
		data_log[symbol]
		data_log[symbol][complete_key] = scrape_data
	except KeyError:
		data_log[symbol] = {}
		data_log[symbol]['complete'] = None
		data_log[symbol]['incomplete'] = None
		data_log[symbol][complete_key] = scrape_data
	pickle.dump(data_log, open(settings.SCRAPE_LOG_FILE_PATH, "wb"))

def add_extract_data(symbol, extract_data, complete):
	"""Add data regarding scrape or extract to master log."""
	
	if complete:
		complete_key = 'complete'
	else:
		complete_key = 'incomplete'
	data_log = pickle.load(open(settings.EXTRACT_LOG_FILE_PATH, "rb"))
	try:
		data_log[symbol]
		data_log[symbol][complete_key].append(extract_data)
	except KeyError:
		data_log[symbol] = {}
		data_log[symbol]['complete'] = []
		data_log[symbol]['incomplete'] = []
		data_log[symbol][complete_key].append(extract_data)
	pickle.dump(data_log, open(settings.EXTRACT_LOG_FILE_PATH, "wb"))

def check_if_extracted(symbol, date):
	"""Check if symbol's date was previously extracted."""
	
	data_log = pickle.load(open(settings.EXTRACT_LOG_FILE_PATH, "rb"))
	try:
		extracted = data_log[symbol]['complete']
		not_extracted = data_log[symbol]['incomplete']
	except KeyError:
		return False
	if date in extracted:
		return True
	if date in not_extracted:
		return True
	return False

