import settings
import requests
import LinkURL
import re
import os
import urllib
from bs4 import BeautifulSoup as BS

class GetFilings:

	def __init__(self, ticker_symbol):
		self.ticker_symbol = ticker_symbol
		self.filings = {'10q_list': [],
				'10q_xl_list': [],
				'10q_xml': [], 
				'10q_html': [],
				'10q_txt': [],
				'10q_xl': [],
				
				'10k_list': [],
				'10k_xl_list': [],
				'10k_xml': [],
				'10k_html': [],
				'10k_txt': [],
				'10k_xl': [],
				
				'success': {
						'count': 0,
						'10-Q': None,
						'10-K': None
					   },
				'errors': {
						'count': 0,
						'10-Q': None,
						'10-K': None
					  }
				}
		print('Scraping {0}'.format(self.ticker_symbol))
		print('Getting 10-Q list...')
		self.get_10q_list()
		print('Getting 10-K list...')
		self.get_10k_list()
		print('Getting 10-Q files...')
		self.get_all_10q()
		print('Getting 10-K files...')
		self.get_all_10k()
		print('Downloading all files...')
		self.download_all()

	def create_folders(self):
		if not os.path.exists('{0}/{1}/'.format(settings.RAW_DATA_PATH, self.ticker_symbol)):
			os.makedirs('{0}/{1}/'.format(settings.RAW_DATA_PATH, self.ticker_symbol))
		if settings.GET_XML:
			if not os.path.exists('{0}/{1}/xml/10-Q/'.format(settings.RAW_DATA_PATH, self.ticker_symbol)):
				os.makedirs('{0}/{1}/xml/10-Q/'.format(settings.RAW_DATA_PATH, self.ticker_symbol))

			if not os.path.exists('{0}/{1}/xml/10-K/'.format(settings.RAW_DATA_PATH, self.ticker_symbol)):
				os.makedirs('{0}/{1}/xml/10-K/'.format(settings.RAW_DATA_PATH, self.ticker_symbol))

		if settings.GET_HTML:
			if not os.path.exists('{0}/{1}/html/10-Q/'.format(settings.RAW_DATA_PATH, self.ticker_symbol)):
				os.makedirs('{0}/{1}/html/10-Q/'.format(settings.RAW_DATA_PATH, self.ticker_symbol))

			if not os.path.exists('{0}/{1}/html/10-K/'.format(settings.RAW_DATA_PATH, self.ticker_symbol)):
				os.makedirs('{0}/{1}/html/10-K/'.format(settings.RAW_DATA_PATH, self.ticker_symbol))

		if settings.GET_TXT:
			if not os.path.exists('{0}/{1}/txt/10-K/'.format(settings.RAW_DATA_PATH, self.ticker_symbol)):
				os.makedirs('{0}/{1}/txt/10-K/'.format(settings.RAW_DATA_PATH, self.ticker_symbol))

			if not os.path.exists('{0}/{1}/txt/10-Q/'.format(settings.RAW_DATA_PATH, self.ticker_symbol)):
				os.makedirs('{0}/{1}/txt/10-Q/'.format(settings.RAW_DATA_PATH, self.ticker_symbol))

		if settings.GET_XL:
			if not os.path.exists('{0}/{1}/xl/10-K/'.format(settings.RAW_DATA_PATH, self.ticker_symbol)):
				os.makedirs('{0}/{1}/xl/10-K/'.format(settings.RAW_DATA_PATH, self.ticker_symbol))

			if not os.path.exists('{0}/{1}/xl/10-Q/'.format(settings.RAW_DATA_PATH, self.ticker_symbol)):
				os.makedirs('{0}/{1}/xl/10-Q/'.format(settings.RAW_DATA_PATH, self.ticker_symbol))

	def validate_page(self, html):
		try:
			check = html.find_all('center')[0].text
		except IndexError:
			self.create_folders()
			return True 
		return False

	def get_main_html(self, q_or_k):
		link = settings.LINK_URL.format(self.ticker_symbol, q_or_k)
		r = requests.get(link)
		s = BS(r.text)
		if self.validate_page(s):
			return s
		else:
			return False

	def get_10q_list(self):
		html = self.get_main_html('10-Q')
		if html:
			for link in html.find_all('a', {'id': 'documentsbutton'}):
				doc_url = 'https://www.sec.gov' + link['href']
				self.filings['10q_list'].append(doc_url)
			for link in html.find_all('a', {'id': 'interactiveDataBtn'}):
				doc_url = 'https://www.sec.gov' + link['href']
				self.filings['10q_xl_list'].append(doc_url)
		else:
			return False


	def get_10k_list(self):
		html = self.get_main_html('10-K')
		if html:
			for link in html.find_all('a', {'id': 'documentsbutton'}):
				doc_url = 'https://www.sec.gov' + link['href']
				self.filings['10k_list'].append(doc_url)
			for link in html.find_all('a', {'id': 'interactiveDataBtn'}):
				doc_url = 'https://www.sec.gov' + link['href']
				self.filings['10k_xl_list'].append(doc_url)

	def get_xml_file(self, html, i):
		s = BS(html)
		try:
			xml_link = s.find_all('table', {'class': 'tableFile', 'summary': 'Data Files'})[0].find_all('tr')[i].find_all('td')[2].find('a')['href']
			xtname = ['.xml', '.xsd']
			if os.path.splitext(xml_link)[1] in xtname:
				xml_link = 'https://www.sec.gov' + xml_link
				return xml_link
			else:
				return False
		except IndexError:
			return False

	def get_html(self, html):
		s = BS(html)
		try:
			html_link = s.find_all('table', {'class': 'tableFile', 'summary': 'Document Format Files'})[0].find_all('tr')[1].find('a')['href']
			xtname = ['.html', '.htm']
			if os.path.splitext(html_link)[1] in xtname:
				html_link = 'https://www.sec.gov' + html_link
				return html_link
			else:
				return False
		except IndexError:
			return False

	def get_txt(self, html):
		s = BS(html)
		try:
			txt_link = s.find_all('table', {'class': 'tableFile', 'summary': 'Document Format Files'})[0].find_all('td')
			link_idx = None
			for idx, val in enumerate(txt_link):
				if 'Complete submission' in val.text:
					link_idx = idx + 1
			txt_link = txt_link[link_idx].find('a')['href']
			xtname = ['.txt']
			if os.path.splitext(txt_link)[1] in xtname:
				txt_link = 'https://www.sec.gov' + txt_link
				return txt_link
			else:
				return False
		except IndexError:
			return False

	def get_xl(self, html):
		s = BS(html)
		try:
			xl_link = s.find_all('td', {'colspan': '2'})[0].find_all('a')[1]['href']
			link = 'https://www.sec.gov' + xl_link
			return link
		except IndexError:
			return False
			
	def get_date(self, html):
		s = BS(html)
		try:
			date = s.find_all('div', {'class': 'formGrouping'})[1].find_all('div')[1].text
			return date
		except (IndexError, AttributeError):
			return False


	def get_all_10q(self):
		if len(self.filings['10q_list']) == 0:
			try:
				self.filings['errors']['10-Q'].append('all')
			except (KeyError, AttributeError):
				self.filings['errors']['10-Q'] = []
				self.filings['errors']['10-Q'].append('all')
			return False
		dates = []
		errors = {}
		success = {}
		for link_val in self.filings['10q_list']:
			r = requests.get(link_val)
			html_txt = r.text
			date = self.get_date(html_txt)
			dates.append(date)
			success[date] = []
			if settings.GET_XML:
				for i in range(1, 7):
					link_xml = self.get_xml_file(html_txt, i)
					if link_xml:
						self.filings['10q_xml'].append((link_xml, date))
						try:
							success[date].append((link_xml, date))
						except (KeyError, AttributeError):
							success[date] = []
							success[date].append('xml')
					elif not link_xml:
						try:
							errors[date].append('xml')
						except (KeyError, AttributeError):
							errors[date] = []
							errors[date].append('xml')
			if settings.GET_HTML:
				link_html = self.get_html(html_txt)
				if link_html:
					self.filings['10q_html'].append((link_html, date, 'html'))
					try:
						success[date].append('html')
					except (KeyError, AttributeError):
						success[date] = []
						success[date].append('html')
				elif not link_html:
					try:
						errors[date].append('html')
					except (KeyError, AttributeError):
						errors[date] = []
						errors[date].append('html')
			if settings.GET_TXT:
				link_txt = self.get_txt(html_txt)
				if link_txt:
					self.filings['10q_txt'].append((link_txt, date, 'txt'))
					try:
						success[date].append('txt')
					except (KeyError, AttributeError):
						success[date] = []
						success[date].append('txt')
				elif not link_txt:
					try:
						errors[date].append('txt')
					except (KeyError, AttributeError):
						errors[date] = []
						errors[date].append('txt')
		if settings.GET_XL:
			count = 0
			for link_val in self.filings['10q_xl_list']:
				r = requests.get(link_val)
				html_txt = r.text
				link_xl = self.get_xl(html_txt)
				if link_xl:
					self.filings['10q_xl'].append((link_xl, dates[count], 'xl'))
					try:
						success[dates[count]].append('xl')
					except (KeyError, AttributeError):
						success[dates[count]] = []
						success[dates[count]].append('xl')
				elif not link_xl:
					try:
						errors[dates[count]].append('xl')
					except (KeyError, AttributeError):
						errors[dates[count]] = []
						errors[dates[count]].append('xl')
				count += 1
		if len(errors) > 0:
			self.filings['errors']['count'] += 1
			self.filings['errors']['10-Q'] = errors
		if len(success) > 0:
			self.filings['success']['count'] += 1
			self.filings['success']['10-Q'] = success

	def get_all_10k(self):
		if len(self.filings['10k_list']) == 0:
			try:
				self.filings['errors']['10-K'].append('all')
			except (KeyError, AttributeError):
				self.filings['errors']['10-K'] = []
				self.filings['errors']['10-K'].append('all')
			return False
		dates = []
		errors = {}
		success = {}
		for link_val in self.filings['10k_list']:
			r = requests.get(link_val)
			html_txt = r.text
			date = self.get_date(html_txt)
			dates.append(date)
			success[date] = []
			if settings.GET_XML:
				for i in range(1, 7):
					link_xml = self.get_xml_file(html_txt, i)
					if link_xml:
						self.filings['10k_xml'].append((link_xml, date))
						try:
							success[date].append((link_xml, date))
						except (KeyError, AttributeError):
							success[date] = []
							success[date].append('xml')
					elif not link_xml:
						try:
							errors[date].append('xml')
						except (KeyError, AttributeError):
							errors[date] = []
							errors[date].append('xml')
			if settings.GET_HTML:
				link_html = self.get_html(html_txt)
				if link_html:
					self.filings['10k_html'].append((link_html, date, 'html'))
					try:
						success[date].append('html')
					except (KeyError, AttributeError):
						success[date] = []
						success[date].append('html')
				elif not link_html:
					try:
						errors[date].append('html')
					except (KeyError, AttributeError):
						errors[date] = []
						errors[date].append('html')
			if settings.GET_TXT:
				link_txt = self.get_txt(html_txt)
				if link_txt:
					self.filings['10k_txt'].append((link_txt, date, 'txt'))
					try:
						success[date].append('txt')
					except (KeyError, AttributeError):
						success[date] = []
						success[date].append('txt')
				elif not link_txt:
					try:
						errors[date].append('txt')
					except (KeyError, AttributeError):
						errors[date] = []
						errors[date].append('txt')
		if settings.GET_XL:
			count = 0
			for link_val in self.filings['10k_xl_list']:
				r = requests.get(link_val)
				html_txt = r.text
				link_xl = self.get_xl(html_txt)
				if link_xl:
					self.filings['10k_xl'].append((link_xl, dates[count], 'xl'))
					try:
						success[dates[count]].append('xl')
					except (KeyError, AttributeError):
						success[dates[count]] = []
						success[dates[count]].append('xl')
				elif not link_xl:
					try:
						errors[dates[count]].append('xl')
					except (KeyError, AttributeError):
						errors[dates[count]] = []
						errors[dates[count]].append('xl')
				count += 1
		if len(errors) > 0:
			self.filings['errors']['count'] += 1
			self.filings['errors']['10-K'] = errors
		if len(success) > 0:
			self.filings['success']['count'] += 1
			self.filings['success']['10-K'] = success

	def check_duplicate(self, directory, filename):
		if filename in os.listdir(directory):
			return True
		return False

	def download_all(self):
		#Download XML files
		if settings.GET_XML:
			for link in self.filings['10q_xml']:
				fname = os.path.split(link[0])[1]
				ext = os.path.splitext(link[0])[1]
				fname = "{0}_{1}{2}".format(self.ticker_symbol, fname, ext)
				diry = '{0}/{1}/xml/10-Q/{2}/'.format(settings.RAW_DATA_PATH, self.ticker_symbol, link[1])
				if not os.path.exists(diry):
					os.makedirs(diry)
				if not self.check_duplicate(diry, fname):
					urllib.urlretrieve(link[0], '{0}{1}'.format(diry, fname))
					
			for link in self.filings['10k_xml']:
				fname = os.path.split(link[0])[1]
				ext = os.path.splitext(link[0])[1]
				fname = "{0}_{1}{2}".format(self.ticker_symbol, fname, ext)
				diry = '{0}/{1}/xml/10-K/{2}/'.format(settings.RAW_DATA_PATH, self.ticker_symbol, link[1])
				if not os.path.exists(diry):
					os.makedirs(diry)
				if not self.check_duplicate(diry, fname):
					urllib.urlretrieve(link[0], '{0}{1}'.format(diry, fname))
		
		#Download HTML files
		if settings.GET_HTML:
			for link in self.filings['10q_html']:
				fname = "{0}_{1}_{2}.html".format(self.ticker_symbol, link[1], link[2])
				diry = '{0}/{1}/html/10-Q/{2}/'.format(settings.RAW_DATA_PATH, self.ticker_symbol, link[1])
				if not os.path.exists(diry):
					os.makedirs(diry)
				if not self.check_duplicate(diry, fname):
					urllib.urlretrieve(link[0], '{0}{1}'.format(diry, fname))
					
			for link in self.filings['10k_html']:
				fname = "{0}_{1}_{2}.html".format(self.ticker_symbol, link[1], link[2])
				diry = '{0}/{1}/html/10-K/{2}/'.format(settings.RAW_DATA_PATH, self.ticker_symbol, link[1])
				if not os.path.exists(diry):
					os.makedirs(diry)
				if not self.check_duplicate(diry, fname):
					urllib.urlretrieve(link[0], '{0}{1}'.format(diry, fname))

		#Download TXT files
		if settings.GET_TXT:
			for link in self.filings['10q_txt']:
				fname = "{0}_{1}_{2}.txt".format(self.ticker_symbol, link[1], link[2])
				diry = '{0}/{1}/txt/10-Q/{2}/'.format(settings.RAW_DATA_PATH, self.ticker_symbol, link[1])
				if not os.path.exists(diry):
					os.makedirs(diry)
				if not self.check_duplicate(diry, fname):
					urllib.urlretrieve(link[0], '{0}{1}'.format(diry, fname))

			for link in self.filings['10k_txt']:
				fname = "{0}_{1}_{2}.txt".format(self.ticker_symbol, link[1], link[2])
				diry = '{0}/{1}/txt/10-K/{2}/'.format(settings.RAW_DATA_PATH, self.ticker_symbol, link[1])
				if not os.path.exists(diry):
					os.makedirs(diry)
				if not self.check_duplicate(diry, fname):
					urllib.urlretrieve(link[0], '{0}{1}'.format(diry, fname))

		#Download XL files
		if settings.GET_XL:
			for link in self.filings['10q_xl']:
				fname = "{0}_{1}_{2}.xlsx".format(self.ticker_symbol, link[1], link[2])
				fname = self.ticker_symbol + fname
				diry = '{0}/{1}/xl/10-Q/{2}/'.format(settings.RAW_DATA_PATH, self.ticker_symbol, link[1])
				if not os.path.exists(diry):
					os.makedirs(diry)
				if not self.check_duplicate(diry, fname):
					urllib.urlretrieve(link[0], '{0}{1}'.format(diry, fname))
					
			for link in self.filings['10k_xl']:
				fname = "{0}_{1}_{2}.xlsx".format(self.ticker_symbol, link[1], link[2])
				fname = self.ticker_symbol + fname
				diry = '{0}/{1}/xl/10-K/{2}/'.format(settings.RAW_DATA_PATH, self.ticker_symbol, link[1])
				if not os.path.exists(diry):
					os.makedirs(diry)
				if not self.check_duplicate(diry, fname):
					urllib.urlretrieve(link[0], '{0}{1}'.format(diry, fname))
