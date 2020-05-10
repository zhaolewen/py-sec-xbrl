import settings
import EdgarScrape
import XMLExtract
import os
import time
import requests
import sys
import pickle
import pandas as pd


def extract_xml(symbol):
	q_path = "{0}/{1}/xml/{2}".format(settings.RAW_DATA_PATH, symbol, '10-Q')
	k_path = "{0}/{1}/xml/{2}".format(settings.RAW_DATA_PATH, symbol, '10-K')
	q_list = os.listdir(q_path)
	k_list = os.listdir(k_path)

	#Create directories if they do not exist
	if not os.path.exists("{0}/{1}/".format(settings.EXTRACTED_DATA_PATH, symbol)):
		os.makedirs("{0}/{1}/".format(settings.EXTRACTED_DATA_PATH, symbol))

	if not os.path.exists("{0}/{1}/10-Q/".format(settings.EXTRACTED_DATA_PATH, symbol)):
		os.makedirs("{0}/{1}/10-Q/".format(settings.EXTRACTED_DATA_PATH, symbol))

	if not os.path.exists("{0}/{1}/10-Q/xml/".format(settings.EXTRACTED_DATA_PATH, symbol)):
		os.makedirs("{0}/{1}/10-Q/xml/".format(settings.EXTRACTED_DATA_PATH, symbol))

	if not os.path.exists("{0}/{1}/10-K/".format(settings.EXTRACTED_DATA_PATH, symbol)):
		os.makedirs("{0}/{1}/10-K/".format(settings.EXTRACTED_DATA_PATH, symbol))

	if not os.path.exists("{0}/{1}/10-K/".format(settings.EXTRACTED_DATA_PATH, symbol)):
		os.makedirs("{0}/{1}/10-K/xml/".format(settings.EXTRACTED_DATA_PATH, symbol))

	xml_10q_path = "{0}/{1}/10-Q/xml/".format(settings.EXTRACTED_DATA_PATH, symbol)
	xml_10k_path = "{0}/{1}/10-K/xml/".format(settings.EXTRACTED_DATA_PATH, symbol)

	#10-Q Extract
	for ql in q_list:
		if logs.check_if_extracted(symbol, ql):
			continue

		if not os.path.exists("{0}/{1}".format(xml_10q_path, ql)):
			os.makedirs("{0}/{1}".format(xml_10q_path, ql))

		ql_path = "{0}/{1}".format(xml_10q_path, ql)


		try:
			tmp_xe = XMLExtract.ExtractFilingData(symbol, ql, '10-Q')
		except:
			logs.add_extract_data(symbol, ql, False)
			continue

		if settings.OUTPUT_PICKLE:
			if tmp_xe.data['error'] == False:
				pickle.dump(tmp_xe.data, open("{0}/{1}.p".format(ql_path, tmp_xe.format_str), "wb"))
				logs.add_extract_data(symbol, ql, True)
				pass
			elif tmp_xe.data['error'] == True:
				print('Error Extracting: {0}|{1}|{2}'.format(symbol, ql, '10-K'))
				logs.add_extract_data(symbol, ql, False)
				pass
		if settings.OUTPUT_JSON:
			pass


	for kl in k_list:
		if logs.check_if_extracted(symbol, kl):
			continue

		if not os.path.exists("{0}/{1}".format(xml_10k_path, kl)):
			os.makedirs("{0}/{1}".format(xml_10k_path, kl))

		kl_path = "{0}/{1}".format(xml_10k_path, kl)

		try:
			tmp_xe = XMLExtract.ExtractFilingData(symbol, kl, '10-K')
		except:
			logs.add_extract_data(symbol, ql, False)
			continue

		if settings.OUTPUT_PICKLE:
			if tmp_xe.data['error'] == False:
				pickle.dump(tmp_xe.data, open("{0}/{1}.p".format(kl_path, tmp_xe.format_str), "wb"))
				logs.add_extract_data(symbol, kl, True)
				pass
			elif tmp_xe.data['error'] == True:
				print('Error Extracting: {0}|{1}|{2}'.format(symbol, kl, '10-K'))
				logs.add_extract_data(symbol, kl, False)
				pass
		if settings.OUTPUT_JSON:
			pass


def run_main():
	scrape_thread = ScrapeThread(name='Scrape Thread')
	scrape_thread.daemon = True
	extract_thread = ExtractThread(name='Extract Thread')
	extract_thread.daemon = True
	scrape_thread.start()
	extract_thread.start()
	scrape_thread.join()
	extract_thread.join()

if __name__ == '__main__':
	run_main()
