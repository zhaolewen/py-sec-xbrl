import settings
import os
import pickle
import json
import re
import string
import math
import pandas as pd
from collections import OrderedDict
from bs4 import BeautifulSoup as BS


class ExtractFilingData:

	def __init__(self, symbol, date, ftype):
		self.ticker = symbol
		self.date = date
		self.ftype = ftype
		self.symbol = None
		self.data = OrderedDict()
		
		self.ins_sp = None
		self.schema_sp = None
		self.cal_sp = None
		self.def_sp = None
		self.lab_sp = None
		self.pre_sp = None
		self.xl_pd = None
		
		self.xbrl_year = None
		
		self.format_data = {
							'quarter': None,
							'year': None,
							'date': None,
							'symbol': None,
							'ftype': None,
							}
		
		print("Extract contents from: {0}|{1}|{2}".format(self.ticker, self.date, self.ftype))
		self.create_data_segments()
		self.load_files()
		if self.data['error'] == False:
			self.get_total_ins_t()
			self.build_ins()
			self.get_year()
			self.get_format_data()
			self.symbol = self.format_data['symbol']
			self.get_all_labels()
			self.extract_all_pre()
			self.extract_all_calc()
			del self.data['ins_t']
			self.format_data['symbol'] = self.ticker
			self.format_str = "{0}_{1}_{2}_{3}_{4}".format(self.format_data['symbol'],
													   self.format_data['date'],
													   self.format_data['year'],
													   self.format_data['quarter'],
													   self.format_data['ftype'])
		elif self.data['error'] == True:
			pass
		
	def create_data_segments(self):
		"""Create the data segment dictionaries."""
		
		self.data['ins_t'] = OrderedDict()
		self.data['ins'] = OrderedDict()
		self.data['cal'] = OrderedDict()
		self.data['lab'] = OrderedDict()
		self.data['pre'] = OrderedDict()
		self.data['error'] = False
		self.data['no_lineage'] = []

	def validate_file(self, fname):
		"""Returns file category type."""
		
		with open(fname, 'r') as f:
			tmp = BS(f)
		
		pre_found = tmp.find(re.compile('presentation[lL]ink'))
		def_found = tmp.find(re.compile('definition[lL]ink'))
		cal_found = tmp.find(re.compile('calculation[lL]ink'))
		lab_found = tmp.find(re.compile('label[lL]ink'))
		sch_found = tmp.find(re.compile('roletype'))
		ins_found = tmp.find(re.compile('context'))
		tmp_found_list = [pre_found, def_found, cal_found, sch_found, ins_found, lab_found]
		found_list = []
		for fl in tmp_found_list:
			if fl:
				found_list.append(fl)
				
		if len(found_list) == 1:
			tmp_fl = found_list[0]
			if tmp_fl == pre_found:
				return 'pre'
			if tmp_fl == def_found:
				return 'def'
			if tmp_fl == lab_found:
				return 'lab'
			if tmp_fl == cal_found:
				return 'cal'
			if tmp_fl == sch_found:
				return 'schema'
			if tmp_fl == ins_found:
				return 'ins'
		else:
			return found_list

	def load_files(self):
		"""Load all data files and store in variables."""
		
		fpath = '{0}/{1}/xml/{2}/{3}'.format(settings.RAW_DATA_PATH,
										  self.ticker,
										  self.ftype,
										  self.date)

		files = os.listdir(fpath)
		sym_len = len(self.ticker) + 1
		date_len = len(self.date) + 1
		tot_len = sym_len + date_len
		required = ['pre', 'lab', 'cal', 'ins']
		found = []
		not_found = []
		for x in files:
			spli_t = os.path.splitext(x)[0]
			ext = spli_t[tot_len:]
			
			fname = '{0}/{1}'.format(fpath, x)
			ftype = self.validate_file(fname)
			
			if isinstance(ftype, list):
				continue

			if ftype == 'ins': #Load instance file
				with open(fname, 'r') as f:
					self.ins_sp = BS(f)
				found.append('ins')

			if ftype == 'schema':
				continue

			if ftype == 'cal': #Load calculations file
				with open(fname, 'r') as f:
					self.cal_sp = BS(f)
				found.append('cal')

			if ftype == 'def':
				continue

			if ftype == 'lab': #Load labels file
				with open(fname, 'r') as f:
					self.lab_sp = BS(f)
				found.append('lab')

			if ftype == 'pre': #Load presentation file
				with open(fname, 'r') as f:
					self.pre_sp = BS(f)
				found.append('pre')

		for i in required:
			if i not in found:
				not_found.append(i)
		if len(not_found) > 0:
			self.data['error'] = True
			return False
		
	def get_year(self):
		try:
			yre = '(dei:DocumentFiscalYearFocus$)'
			year = self.ins_sp.find(name=re.compile(yre, re.IGNORECASE | re.MULTILINE)).get_text()
		except AttributeError:
			try:
				yre = '(dei:DocumentPeriodEndDate$)'
				year = self.ins_sp.find(name=re.compile(yre, re.IGNORECASE | re.MULTILINE)).get_text()
				year = year[:4]
			except AttributeError:
				return False
		try:
			year = int(year)
			sure_years = [2001, 2002, 2003, 2004, 2005, 
						  2006, 2007, 2008, 2009, 2011,
						  2012, 2013, 2014, 2016]
			if year in sure_years:
				self.xbrl_year = str(year)
			if year == 2010:
				self.xbrl_year = '2009'
			if year == 2015:
				self.xbrl_year = '2014'
			return True
		except:
			return False
			
	def get_format_data(self):
		names = ['documentfiscalperiodfocus', 'documentfiscalyearfocus', 
				'documentperiodenddate', 'tradingsymbol', 'documenttype']
		#Get Quarter
		try:
			val_q = self.data['ins']['facts']['dei'][names[0]]['val_by_date'].keys()[0]
			self.format_data['quarter'] = self.data['ins']['facts']['dei'][names[0]]['val_by_date'][val_q][0][0].upper()
		except KeyError:
			self.format_data['quarter'] = 'NA'
		#Get Year
		try:
			val_y = self.data['ins']['facts']['dei'][names[1]]['val_by_date'].keys()[0]
			self.format_data['year'] = self.data['ins']['facts']['dei'][names[1]]['val_by_date'][val_y][0][0]
		except KeyError:
			self.format_data['year'] = self.xbrl_year
		#Get Date
		try:
			val_d = self.data['ins']['facts']['dei'][names[2]]['val_by_date'].keys()[0]
			self.format_data['date'] = self.data['ins']['facts']['dei'][names[2]]['val_by_date'][val_d][0][0]
		except KeyError:
			self.format_data['date'] = 'NA'
		#Get Symbol
		try:
			val_s = self.data['ins']['facts']['dei'][names[3]]['val_by_date'].keys()[0]
			self.format_data['symbol'] = self.data['ins']['facts']['dei'][names[3]]['val_by_date'][val_s][0][0].upper()
		except (KeyError, IndexError):
			self.format_data['symbol'] = self.ticker
		#Get Filing Type
		try:
			val_f = self.data['ins']['facts']['dei'][names[4]]['val_by_date'].keys()[0]
			self.format_data['ftype'] = self.data['ins']['facts']['dei'][names[4]]['val_by_date'][val_f][0][0].replace('/', '-')
			self.format_data['ftype'] = self.format_data['ftype'].upper()
		except KeyError:
			self.format_data['ftype'] = self.ftype
		
	
	######################
	## Generic Portions ##
	######################
	
	def find_closest_ins(self, lab):
		"""From an entered label, find the closest instance fact."""
		
		if lab[1] == '':
			return False
		try:
			self.data['ins']['facts'][lab[0].lower()][lab[1].lower()]
			return lab
		except KeyError:
			lab0 = lab[0]
			lab1 = lab[1][:-1]
			lab = (lab0, lab1)
			return self.find_closest_ins(lab)

	def check_if_in_pre(self, title):
		"""Check if title exists in presentation dictionary."""
		
		try:
			self.data['pre']['roles'][title]
			return True
		except KeyError:
			return False
	
	def format_to_xbrl(self, try_str):
		"""Remove spaces and non-alphanumeric characters 
		   from a string."""
		
		cleaned_str = re.sub('[^0-9a-zA-Z]+', '', try_str)
		return cleaned_str
	
	def find_label(self, try_str, get_full=92):
		"""Find label from a string as exists in the populated
		   labels dictionary."""

		if try_str == float('nan'):
			return False
		key_ref = self.data['lab'].keys()
		key_lists = []
		for kr in key_ref:
			kl_cp = self.data['lab'][kr].keys()
			key_lists.append(kl_cp)
		label_list = []
		for key_num in range(len(key_ref)):
			for i in key_lists[key_num]:
				val_keys = self.data['lab'][key_ref[key_num]][i].keys()
				for num in val_keys:
					if self.data['lab'][key_ref[key_num]][i][num] == try_str:
						if get_full:
							label_list.append((key_ref[key_num], i))
						else:
							label_list.append((key_ref[key_num], i[:get_full]))
		label_list = list(set(label_list))
		if len(label_list) == 0:
			try:
				label_list = self.find_label(try_str[:-1])
			except RuntimeError:
				return label_list
		return label_list
		
	def find_label_str(self, label):
		"""Find string from a label as exists in the populated
		   labels dictionary."""

		pfx = label[0]
		label = label[1]
		try:
			base_ref = self.data['lab'][pfx][label]
		except KeyError:
			try:
				base_ref = self.data['lab']['us-gaap'][label]
			except KeyError:
				try:
					base_ref = self.data['lab'][self.symbol.lower()][label]
				except KeyError:
					base_ref = label
		return base_ref
	
	def get_pfx_gen(self, html_string, ins):
		"""Generic prefix extractor utilizing the instance dictionary."""
		
		ins_keys = self.data[ins]['facts'].keys()
		html_string = str(html_string).lower()
		pfx = None
		for i in ins_keys:
			if i in html_string:
				pfx = i
		if not '_' in html_string and not ':' in html_string and not '-' in html_string:
			if pfx == None:
				return None
		return pfx

	def get_name_gen(self, html_string, ins):
		"""Generic name extractor utilizing the instance dictionary."""
		
		html_string = str(html_string)
		ins_keys = self.data[ins]['facts'].keys()
		tmp_str = html_string
		while True:
			pfx = re.search('([^\W_]|[-])*', tmp_str).group(0)
			if len(tmp_str) == 0:
				return False
			if pfx in ins_keys:
				tmp_str = tmp_str[len(pfx)+1:]
				break
			else:
				tmp_str = tmp_str[len(pfx)+1:]	
		to_use = re.search('[^\W_]*', tmp_str)
		return to_use.group(0)
		
	def get_lineage(self, roots, from_to_list, ele, lineage_list=None):
		"""Get the lookup location on the tree for a specific element."""
		
		if lineage_list:
			lineage = lineage_list
		else:
			lineage = [ele]
		cur_ele = ele
		for i in roots:
			if cur_ele == i[1]:
				return lineage 
		else:
			for i in from_to_list:
				if i[1] == cur_ele:
					lineage.insert(0, i[0])
					cur_ele = i[0]
			return self.get_lineage(roots, from_to_list, cur_ele, lineage)
			
	def check_path_exist(self, path):
		"""Check if a certain path exists."""
		
		try:
			exec(path)
			return True
		except KeyError:
			return False
		
	def gen_dict_path(self, cat, link_eles, role_name, pfx, ctx=None, ref_self='self'):
		"""Generate dictionary path and execute code to create or assign
		   values to dictionary."""
		
		if cat == 'pre' or cat == 'cal':
			base_str = '{0}.data["{1}"]["roles"]["{2}"]["tree"]'.format(ref_self, cat, role_name)
		elif cat == 'xl':
			base_str = '{0}.data["{1}"]["{2}"]["tree"]'.format(ref_self, cat, role_name)
		for i in link_eles:
			if i == link_eles[0]:
				next_ele = "['{0}']".format(i)
				base_str += next_ele
				if not self.check_path_exist(base_str):
					exec(base_str + ' = OrderedDict()')
					next_ele = '["sub"]'
					base_str += next_ele
					if not self.check_path_exist(base_str):
						exec(base_str + ' = OrderedDict()')
				else:
					base_str += '["sub"]'
			elif i == link_eles[-1]:
				next_ele = '["{0}"]'.format(i)
				base_str += next_ele
				if not self.check_path_exist(base_str):
					exec(base_str + " = OrderedDict()")
				pfx_str = base_str + '["pfx"] = "{0}"'.format(pfx)
				if not self.check_path_exist(pfx_str):
					exec(pfx_str)
				if not self.check_path_exist(base_str + "['sub']"):
					exec(base_str + '["sub"] = OrderedDict()')
				if cat == 'pre' and ctx:
					if isinstance(ctx, (unicode, str)):
						try:
							try:
								assign_str = base_str + '["label"] = "{0}"'.format(ctx.encode('utf-8'))
								exec(assign_str)
							except SyntaxError:
								ctx_2 = ctx[2][:79]
								ctx_2 = ctx_2.replace('"', "'")
								ctx_2 = ctx_2.replace('\n', '')
								assign_str = base_str + '["label"] = "{0}"'.format(ctx_2.encode('utf-8'))
								exec(assign_str)
						except KeyError:
							pass
					if isinstance(ctx, tuple):
						try:
							assign_str = base_str + "['order'] = {0}".format(ctx[0])
							exec(assign_str)
						except KeyError:
							pass
						try:
							assign_str = base_str + "['val'] = {0}".format(ctx[1])
							exec(assign_str)
						except KeyError:
							pass
						try:
							try:
								assign_str = base_str + '["label"] = "{0}"'.format(ctx[2].encode('utf-8'))
								exec(assign_str)
							except SyntaxError:
								ctx_2 = ctx[2][:79]
								ctx_2 = ctx_2.replace('"', "'")
								ctx_2 = ctx_2.replace('\n', '')
								assign_str = base_str + '["label"] = "{0}"'.format(ctx_2.encode('utf-8'))
								exec(assign_str)
						except KeyError:
							pass
				elif cat == 'cal' and ctx:
					try:
						assign_str = base_str + "['order'] = {0}".format(ctx[0])
						exec(assign_str)
					except KeyError:
						pass
					try:
						assign_str = base_str + "['weight'] = {0}".format(ctx[1])
						exec(assign_str)
					except KeyError:
						pass
					try:
						assign_str = base_str + "['val'] = {0}".format(ctx[2])
						exec(assign_str)
					except KeyError:
						pass
			else:
				next_ele = '["{0}"]'.format(i)
				base_str += next_ele
				if not self.check_path_exist(base_str):
					exec(base_str + ' = OrderedDict()')
					base_str += "['sub']"
					if not self.check_path_exist(base_str):
						exec(base_str + ' = OrderedDict()')
				else:
					base_str += "['sub']"

	def traverse_print_tree(self, base, role_keys, tabs=0):
		"""Traverse cal tree and print."""

		for rk in role_keys:
			if rk == 'sub':
				continue
			tab_str = '   ' * tabs
			try:
				lab_str = tab_str + str(base[rk]['label'])
			except KeyError:
				lab_str = rk
			try:
				base_keys = base[rk]['val'].keys()
				if len(base_keys) == 0:
					if len(base[rk]['sub']) == 0:
						continue
					else:
						print('\033[1m' + lab_str + '\033[0m')
				else:
					date_str = ''
					val_str = ''
					for i in base_keys:
						date_str += str(i)
						date_str += '\t\t'
					for bk in base_keys:
						if base[rk]['val'][bk] == None:
							continue
						if isinstance(base[rk]['val'][bk], float):
							val_str += str(base[rk]['val'][bk])
						else:
							val_str += base[rk]['val'][bk].encode('utf-8')
						val_str += '\t\t'
					print(lab_str)
					print(tab_str + '\t' + date_str)
					print(tab_str + '\t' + val_str)
			except KeyError:
				pass
			if len(base[rk]['sub']) > 0:
				rk_base = base[rk]['sub']
				rk_base_keys = rk_base.keys()
				self.traverse_print_tree(rk_base, rk_base_keys, tabs=tabs+1)
				
	def traverse_tree(self, base):
		base_tree = base['tree']
		role_keys = base_tree.keys()
		self.traverse_print_tree(base_tree, role_keys)
	
	def traverse_all_trees(self):
		base = self.data['pre']['roles']
		base_keys = base.keys()
		for bk in base_keys:
			self.traverse_tree(base[bk])
				
	def find_fact_in_role(self, cat, fact):
		"""Returns list of roles with fact in them."""
		
		all_role_keys = self.data[cat]['roles'].keys()
		roles_with_fact = []
		for i in all_role_keys:
			base = self.data[cat]['roles'][i]['unique']
			for b in base:
				if fact == b[1]:
					roles_with_fact.append(i)
		roles_with_fact = list(set(roles_with_fact))
		return roles_with_fact
		
	def find_pfx_in_ins(self, fact):
		"""Returns pfx of fact in ins given no prefix."""
		
		ins_keys = self.data['ins']['facts'].keys()
		for ik in ins_keys:
			base = self.data['ins']['facts'][ik].keys()
			for b in base:
				if b == fact.lower():
					return ik
				
	######################
	## Instance Section ##
	######################
		
	def get_context_id(self, tag):
		"""Get context ID."""
		
		return tag.get('id')
		
	def get_period_type(self, tag):
		"""Get period type."""
		
		period = tag.find(name=re.compile('period'))
		if period.find(name=re.compile('instant')):
			return 'instant'
		else:
			return 'duration'
		
	def get_period(self, tag, p_type):
		"""Get period time."""
		
		period = tag.find(name=re.compile('period'))
		if p_type == 'instant':
			p_content = period.find(name=re.compile('instant')).text
			return p_content
		else:
			p_start = period.find(name=re.compile('start[dD]ate')).text
			p_end = period.find(name=re.compile('end[dD]ate')).text
			p_content = (p_start, p_end)
			return p_content
		
	def build_context_ref_list(self):
		"""Build the context reference list. Each context has a period 
		   that is either an instance and duration type, and the 
		   specific period is also stored under 'when'."""
		
		self.data['ins']['contexts'] = OrderedDict()
		ctx_raw = self.ins_sp.find_all(name=re.compile('context'))
		for ctx in ctx_raw:
			ctx_id = self.get_context_id(ctx)
			exmem = ctx.find(name=re.compile('explicitmember'))
			if exmem:
				exmem_txt = exmem.text
			else:
				exmem_txt = None
			period_type = self.get_period_type(ctx)
			period = self.get_period(ctx, period_type)
			self.data['ins']['contexts'][ctx_id] = OrderedDict()
			self.data['ins']['contexts'][ctx_id]['period'] = OrderedDict()
			self.data['ins']['contexts'][ctx_id]['period']['type'] = period_type
			self.data['ins']['contexts'][ctx_id]['period']['when'] = OrderedDict()
			if period_type == 'instant':
				self.data['ins']['contexts'][ctx_id]['period']['when'] = period
			else:
				self.data['ins']['contexts'][ctx_id]['period']['when']['startdate'] = period[0]
				self.data['ins']['contexts'][ctx_id]['period']['when']['enddate'] = period[1]
			if exmem_txt:
				try:
					self.data['ins']['contexts'][ctx_id]['exmem'].append(exmem_txt)
				except KeyError:
					self.data['ins']['contexts'][ctx_id]['exmem'] = []
					self.data['ins']['contexts'][ctx_id]['exmem'].append(exmem_txt)
				
	def get_pfx(self, html_string):
		"""Extract prefix from HTML string."""
		
		html_string = str(html_string)
		pfx = re.search('[A-zA-Z0-9]+[^:_]*', html_string)
		try:
			return pfx.group(0)
		except AttributeError:
			return None

	def get_name(self, html_string):
		"""Extract name from HTML string."""
		
		html_string = str(html_string)
		name = re.search('(?<=[:_])[A-zA-Z0-9][^\s_]*', html_string)
		try:
			return name.group(0)
		except AttributeError:
			return None

	def make_pfx(self, prfx, ins):
		"""Make the prefix subcategories."""
		
		if prfx not in self.data[ins]['facts'].keys():
			self.data[ins]['facts'][prfx] = OrderedDict()
			
	def pop_ins_t(self, ctx_ref, pfx, name, dates, val, decimals):
		"""Populate ins_t with parameters."""
		
		self.data['ins_t']['facts'][pfx][name][ctx_ref]['date'] = dates
		self.data['ins_t']['facts'][pfx][name][ctx_ref]['val'] = val
		self.data['ins_t']['facts'][pfx][name][ctx_ref]['decimals'] = decimals
		
	def get_facts(self):
		"""Get fact names, store them under prefix, and subcategorize
		   according to context reference."""
		
		self.data['ins_t']['facts'] = OrderedDict()
		tmp_tags = self.ins_sp.find_all(name=re.compile('([A-zA-Z]+:[A-zA-Z]+)'))
		self.make_pfx(self.ticker.lower(), 'ins_t')
		for tmp in tmp_tags:
			pfx = self.get_pfx(tmp)
			name = self.get_name(tmp)
			long_name = None
			for i in tmp.attrs.keys():
				if tmp[i] == '':
					long_name = i
			if long_name:
				name += long_name
			self.make_pfx(pfx, 'ins_t')
			try:
				self.data['ins_t']['facts'][pfx][name]
			except KeyError:
				self.data['ins_t']['facts'][pfx][name] = OrderedDict()
			if len(tmp.get_text()) < 35 and len(tmp.get_text()) >= 1:
					ctx_ref = tmp.get('contextref')
					decimals = tmp.get('decimals')
					if ctx_ref:
						try:
							self.data['ins_t']['facts'][pfx][name][ctx_ref]
						except KeyError:
							self.data['ins_t']['facts'][pfx][name][ctx_ref] = OrderedDict()
						dates = self.data['ins']['contexts'][ctx_ref]['period']['when']
						try:
							exmem = self.data['ins']['contexts'][ctx_ref]['exmem']
							self.data['ins_t']['facts'][pfx][name][ctx_ref]['exmem'] = exmem
							for em in exmem:
								ex_pfx = self.get_pfx(em)
								ex_name = self.get_name(em)
								ex_name = ex_name.lower()
								try:
									self.data['ins_t']['facts'][ex_pfx][ex_name]
								except KeyError:
									self.data['ins_t']['facts'][ex_pfx][ex_name] = OrderedDict()
								try:
									self.data['ins_t']['facts'][ex_pfx][ex_name][ctx_ref]
								except KeyError:
									self.data['ins_t']['facts'][ex_pfx][ex_name][ctx_ref] = OrderedDict()
								try:
									con_fl = float(tmp.text)
									self.pop_ins_t(ctx_ref, ex_pfx, ex_name, dates, con_fl, decimals)
								except ValueError:
									self.pop_ins_t(ctx_ref, ex_pfx, ex_name, dates, tmp.text, decimals)
						except KeyError:
							pass
						try:
							con_fl = float(tmp.text)
							self.pop_ins_t(ctx_ref, pfx, name, dates, con_fl, decimals)
						except ValueError:
							self.pop_ins_t(ctx_ref, pfx, name, dates, tmp.text, decimals)
						
	def get_total_ins_t(self):
		"""Populate the instance dictionary."""
		
		self.build_context_ref_list()
		self.get_facts()
		
	def conv_date_to_int(self, date):
		"""Convert date str to int."""
		
		year = int(date[0:4])
		month = int(date[5:7])
		day = int(date[8:])
		return (year, month, day)
		
	def sort_by_date(self, date_list):
		"""Sort dates in descending order."""
		
		master = OrderedDict()
		s = date_list
		s.sort(key=lambda tup: tup[0], reverse=True)
		master['val_list'] = []
		master['val_by_date'] = OrderedDict()
		for i in s:
			master['val_list'].append((i[1], i[4]))
			try:
				master['val_by_date'][i[0]]
			except KeyError:
				master['val_by_date'][i[0]] = []
			master['val_by_date'][i[0]].append((i[1], i[2], i[3], i[4]))
		tmp_master = []
		tmp_dates = []
		for i in master['val_by_date'].keys():
			if master['val_by_date'][i] not in tmp_master:
				tmp_master.append(master['val_by_date'][i])
				tmp_dates.append(i)
		master['val_by_date'] = OrderedDict()
		for i in range(len(tmp_dates)):
			master['val_by_date'][tmp_dates[i]] = tmp_master[i]
		master['val_list'] = list(set(master['val_list']))
		return master
		
	def val_to_pre_conv(self, val, decimal):
		"""Convert value to pre form using decimal attribute."""
		
		if decimal in ['INF', None, 0]:
			return val
		base_str = '1'
		decimal = int(decimal)
		if decimal < 0:
			base_zero = '0' * (abs(decimal))
			base_str += base_zero
			conv_num = float(base_str)
			val_conv = val / conv_num
			return val_conv
		elif decimal > 0:
			base_zero = '0' * (abs(decimal))
			base_str += base_zero
			conv_num = float(base_str)
			val_conv = val * conv_num
			return val_conv
		
	
	def build_ins(self):
		"""Build instance reference with dates in descending order."""
		
		self.data['ins']['facts'] = OrderedDict()
		pfx_keys = self.data['ins_t']['facts'].keys()
		for pfx in pfx_keys:
			self.make_pfx(pfx, 'ins')
			name_keys = self.data['ins_t']['facts'][pfx].keys()
			for name in name_keys:
				self.data['ins']['facts'][pfx][name] = OrderedDict()
				ctx_keys = self.data['ins_t']['facts'][pfx][name].keys()
				unsorted_ctx = []
				ctx_exmem = []
				for ctx in ctx_keys:
					ctx_val = self.data['ins_t']['facts'][pfx][name][ctx]
					ctx_dec = self.data['ins_t']['facts'][pfx][name][ctx]['decimals']
					ctx_conv_val = self.val_to_pre_conv(ctx_val['val'], ctx_dec)
					ctx_date = ctx_val['date']
					if len(ctx_date) == 2:
						ctx_date_begin = ctx_date['startdate']
						ctx_date_end = ctx_date['enddate']
						unsorted_ctx.append(((ctx_date_begin, ctx_date_end), ctx_val['val'], ctx, ctx_dec, ctx_conv_val))
					else:
						unsorted_ctx.append(((ctx_date), ctx_val['val'], ctx, ctx_dec, ctx_conv_val))
				name_val = self.sort_by_date(unsorted_ctx)
				self.data['ins']['facts'][pfx][name] = name_val
				
	####################
	## Labels Section ##
	####################

	def get_all_labels(self):
		"""Populate the labels dictionary."""
		
		labels = self.lab_sp.find_all(name=re.compile('labellink'))
		tmp_labels = labels[0].find_all(name=re.compile('link:[lL]abel$'))
		if len(tmp_labels) == 0:
			labels = labels[0].find_all(name=re.compile('label'))
		else:
			use_label_nd = False
			for tl in tmp_labels:
				tmp_str = str(tl)
				if '<link:labelarc' in tmp_str or '<link:labelArc' in tmp_str or '<labelarc' in tmp_str:
					use_label_nd = True
					break
			if use_label_nd:
				tmp_labels = labels[0].find_all(name=re.compile('label'))
			labels = tmp_labels
		locs = self.lab_sp.find_all(name=re.compile('x?link:loc'))
		locs_pairs = []
		for i in locs:
			loc_href = i.get('xlink:href')
			lnxt_names = []
			loc_next = i.find_next()
			if loc_next == None:
				break
			keep_going = True
			while loc_next.name not in ['xlink:loc', 'link:loc']:
				if loc_next == None:
					keep_going = False
				elif loc_next.name in ['xlink:labelArc', 'xlink:labelarc']:
					loc_next = loc_next.find_next()
					continue
				elif loc_next.name in ['xlink:label', 'link:label']:
					lnxt_name = self.get_name(loc_next.get('xlink:label'))
					if lnxt_name not in lnxt_names:
						lnxt_names.append(lnxt_name)
				loc_next = loc_next.find_next()
				if loc_next == None:
					break
			loc_href = os.path.splitext(loc_href)[1]
			if '#' not in loc_href:
				continue
			pnd_idx = loc_href.index('#')
			loc_href = loc_href[pnd_idx+1:]
			loc_pfx = self.get_pfx_gen(loc_href, 'ins_t')
			loc_name = self.get_name_gen(loc_href, 'ins_t')
			if not loc_pfx:
				loc_pfx = self.symbol
			if loc_pfx and loc_name:
				tmp_lp = [loc_pfx, loc_name]
				for i in lnxt_names:
					if i not in tmp_lp:
						tmp_lp.append(i)
				tmp_lp = tuple(tmp_lp)
				locs_pairs.append(tmp_lp)
		for i in labels:
			if i.name in ['labelarc', 'labelArc', 'xlink:labelarc', 'xlink:labelArc']:
				continue
			lab_pfx = self.get_pfx_gen(i.get('xlink:label'), 'ins_t')
			lab_name = self.get_name_gen(i.get('xlink:label'), 'ins_t')
			if not lab_name:
				lab_name = self.get_name(i.get('xlink:label'))
				if lab_name and not lab_pfx:
					for lp in locs_pairs:
						for l in lp[1:]:
							if lab_name == l:
								lab_name = l
								lab_pfx = lp[0]
			if not lab_pfx and not lab_name:
				lab_name = self.get_name(i.get('xlink:label'))
				if lab_name:
					lab_pfx = self.find_pfx_in_ins(lab_name)
				if lab_name and not lab_pfx:
					for lp in locs_pairs:
						for l in lp[1:]:
							if lab_name == l:
								lab_name = l
								lab_pfx = lp[0]
			if lab_name and not lab_pfx:
				for lp in locs_pairs:
					for lp in locs_pairs:
						for l in lp[1:]:
							if lab_name == l:
								lab_name = l
								lab_pfx = lp[0]
			if not lab_pfx and not lab_name:
				continue
			if lab_pfx and not lab_name:
				tmp_lab_store = i.get('xlink:label')
				lab_pfx = self.get_pfx_gen(tmp_lab_store, 'ins_t')
				try:
					reg_xt = '(?<={0}[_])[^\W_]*'.format(lab_pfx)
					reg_xt_ex = re.search(reg_xt, tmp_lab_store)
					lab_name = reg_xt_ex.group(0)
				except AttributeError:
					try:
						reg_xt = '(?<={0})[^\W_]*'.format(lab_pfx.upper())
						reg_xt_ex = re.search(reg_xt, tmp_lab_store)
						name_to = reg_xt_ex.group(0)
					except AttributeError:
						pass
			if not lab_name:
				pass
			try:
				self.data['lab'][lab_pfx]
			except KeyError:
				self.data['lab'][lab_pfx] = OrderedDict()
			label_type = i.get('xlink:role')
			label_type = os.path.split(label_type)[1]
			try:
				self.data['lab'][lab_pfx][lab_name][label_type] = i.text
			except KeyError:
				self.data['lab'][lab_pfx][lab_name] = OrderedDict()
				self.data['lab'][lab_pfx][lab_name][label_type] = i.text
		for l in locs_pairs:
			if len(l[1:]) > 1:
				try:
					l2 = self.data['lab'][l[0]][l[2]]
					self.data['lab'][l[0]][l[1]] = l2
				except KeyError:
					pass

	##########################
	## Calculations Section ##
	##########################
	
	def make_calc_tree(self, calc_arcs, calc_locs, role_name, title):
		"""Generate a calculation tree for a specific role 
		   and create the ordered priority and weight."""
		
		root = []
		to_list = []
		from_list = []
		from_to_pair = [] #(parent, child)
		locs_pairs = []
		for cl in calc_locs:
			tmp_cl_raw = cl.get('xlink:href')
			tmp_cl = os.path.splitext(tmp_cl_raw)[1]
			if '#' in tmp_cl:
				tmp_cl_idx = tmp_cl.index('#')
				tmp_cl = tmp_cl[tmp_cl_idx+1:]
				pfx_loc = self.get_pfx_gen(tmp_cl, 'ins_t')
				name_loc = self.get_name_gen(tmp_cl, 'ins_t')
				locs_pairs.append((pfx_loc, name_loc))
		for i in calc_arcs:
			#Start to list
			xlink_to = i.get('xlink:to')
			pfx_to = self.get_pfx_gen(xlink_to, 'ins_t')
			name_to = self.get_name_gen(xlink_to, 'ins_t')
			if not pfx_to and not name_to:
				name_to = xlink_to
				for lp in locs_pairs:
					if name_to == lp[1]:
						pfx_to = lp[0]
						break
			if not pfx_to:
				continue
			if pfx_to and not name_to:
				tmp_to_store = xlink_to
				tmp_to = xlink_to.lower()
				idx_name_s = tmp_to.index(pfx_to)
				xlink_to = xlink_to[idx_name_s:]
				try:
					reg_xt = '(?<={0})[^\W_]*'.format(pfx_to)
					reg_xt_ex = re.search(reg_xt, xlink_to)
					name_to = reg_xt_ex.group(0)
				except AttributeError:
					try:
						reg_xt = '(?<={0})[^\W_]*'.format(pfx_to.upper())
						reg_xt_ex = re.search(reg_xt, xlink_to)
						name_to = reg_xt_ex.group(0)
					except AttributeError:
						pass
			if not name_to:
				tmp_pfx = self.get_name_gen(xlink_to, 'ins')
				if tmp_pfx:
					tmp_nt = xlink_to.lower()
					end_pfx = tmp_nt.index(tmp_pfx) + len(tmp_pfx)
					name_to = xlink_to[end_pfx:]
					if '_' in name_to:
						xt_idx = name_to.index('_')
						name_to = name_to[:xt_idx]
				if not name_to:
					if '_' not in xlink_to and ':' not in xlink_to and '-' not in xlink_to:
						if isinstance(xlink_to, str):
							if tmp_pfx == None:
								name_to = xlink_to
					if not name_to:
						if pfx_to:
							if '_' not in xlink_to and ':' not in xlink_to and '-' not in xlink_to:
								if isinstance(xlink_to, str):
									name_to = xlink_to
						if not name_to:
							continue
			#Get order and weight
			order = i.get('order')
			order = float(order)
			weight = i.get('weight')
			weight = float(weight)
			if name_to not in to_list:
				to_list.append((pfx_to, name_to, order, weight))
			#Start From List
			xlink_from = i.get('xlink:from')
			pfx_from = self.get_pfx_gen(xlink_from, 'ins_t')
			name_from = self.get_name_gen(xlink_from, 'ins_t')
			if not pfx_from and not name_from:
				name_from = xlink_from
				for lp in locs_pairs:
					if name_from == lp[1]:
						pfx_from = lp[0]
						break
			if not pfx_from:
				continue
			if pfx_from and not name_from:
				tmp_from_store = xlink_from
				pfx_from = self.get_pfx_gen(xlink_from, 'ins_t')
				tmp_from = xlink_from.lower()
				idx_name_s = tmp_from.index(pfx_from)
				xlink_from = xlink_from[idx_name_s:]
				try:
					reg_xt = '(?<={0})[^\W_]*'.format(pfx_from)
					reg_xt_ex = re.search(reg_xt, xlink_from)
					name_from = reg_xt_ex.group(0)
				except:
					try:
						reg_xt = '(?<={0})[^\W_]*'.format(pfx_to.upper())
						reg_xt_ex = re.search(reg_xt, xlink_from)
						name_from = reg_xt_ex.group(0)
					except AttributeError:
						pass
			if not name_from:
				tmp_pfx = self.get_name_gen(xlink_from, 'ins')
				if tmp_pfx:
					tmp_nt = xlink_from.lower()
					end_pfx = tmp_nt.index(tmp_pfx) + len(tmp_pfx)
					name_from = xlink_from[end_pfx:]
					if '_' in name_from:
						xt_idx = name_from.index('_')
						name_from = name_from[:xt_idx]
				if not name_from:
					if '_' not in xlink_from and ':' not in xlink_from and '-' not in xlink_from:
						if isinstance(xlink_from, str):
							if tmp_pfx == None:
								name_from = xlink_from
					if not name_from:
						if pfx_from:
							if '_' not in xlink_from and ':' not in xlink_from and '-' not in xlink_from:
								if isinstance(xlink_from, str):
									name_from = xlink_from
						if not name_from:
							continue
			if name_from not in from_list:
				from_list.append((pfx_from, name_from, order, weight))
			from_to_pair.append((name_from, name_to, order, weight))
		for i in from_list:
			in_to_list = False
			for x in to_list:
				if i[:2] == x[:2]:
					in_to_list = True
			if not in_to_list:	
				root.append(i)
		root = list(set(root))
		root.sort(key=lambda tup: tup[2])
		to_list.sort(key=lambda tup: tup[2])
		from_list.sort(key=lambda tup: tup[2])
		if len(root) == 0:
			if len(to_list) > 0 or len(from_list) > 0:
				if len(to_list) == 1 and len(from_list) == 0:
					root = to_list
					root = list(set(root))
				elif len(from_list) == 1 and len(to_list) == 0:
					root = from_list
					root = list(set(root))
				elif len(from_list) == 0:
					root = to_list
					root = list(set(root))
				elif len(to_list) == 0:
					root = from_list
					root = list(set(root))
				elif len(from_list) == 1 and len(to_list) > 1:
					root = from_list
					root = list(set(root))
				elif len(from_list) < len(to_list):
					root = from_list
					root = list(set(root))
				elif to_list == from_list:
					root = from_list
					root = list(set(root))
				else:
					pass
		self.data['cal']['roles'][role_name] = OrderedDict()
		self.data['cal']['roles'][role_name]['title_name'] = title
		self.data['cal']['roles'][role_name]['tree'] = OrderedDict()
		self.data['cal']['roles'][role_name]['from_to'] = from_to_pair
		self.data['cal']['roles'][role_name]['root'] = root
		unique_tmp = from_list + to_list
		unique = list(set(unique_tmp))
		self.data['cal']['roles'][role_name]['unique'] = unique
		key_ctx_list = []
		for i in root:
			self.data['cal']['roles'][role_name]['tree'][i[1]] = OrderedDict()
			self.data['cal']['roles'][role_name]['tree'][i[1]]['pfx'] = i[0]
			self.data['cal']['roles'][role_name]['tree'][i[1]]['sub'] = OrderedDict()
			try:
				tmp_root = self.data['ins']['facts'][i[0]][i[1].lower()]['val_by_date']
			except KeyError:
				try:
					tmp_root = self.data['ins']['facts'][self.symbol.lower()][i[1].lower()]['val_by_date']
				except KeyError:
					try:
						tmp_root = self.data['ins']['facts']['us-gaap'][i[1].lower()]['val_by_date']
					except KeyError:
						continue
			root_val = OrderedDict()
			tr_keys = tmp_root.keys()
			tmp_ctx_list = []
			for trk in tr_keys:
				tmps_val = tmp_root[trk]
				root_val[trk] = tmps_val[0][0]
				if (trk, tmps_val[0][1]) not in tmp_ctx_list:
					tmp_ctx_list.append((trk, tmps_val[0][1]))
			if (i[:2], tuple(tmp_ctx_list)) not in key_ctx_list:
				key_ctx_list.append((i[:2], tuple(tmp_ctx_list)))
			self.data['cal']['roles'][role_name]['tree'][i[1]]['val'] = root_val
			label = self.find_label_str((i[0], i[1]))
			self.data['cal']['roles'][role_name]['tree'][i[1]]['label'] = label
		for i in to_list:
			try:
				line = self.get_lineage(root, from_to_pair, i[1])
			except RuntimeError:
				self.data['no_lineage'].append(i)
				return False
			line_root = line[0]
			use_ctx = None
			for kcl in key_ctx_list:
				if kcl[0][1] == line_root:
					use_ctx = kcl[1]
			val = OrderedDict()
			if use_ctx == None:
				val = None
			else:
				for uc in use_ctx:
					try:
						tmp_val = self.data['ins']['facts'][i[0]][i[1].lower()]['val_by_date'][uc[0]]
					except KeyError:
						continue
					vals = None
					for tv in tmp_val:
						if tv[1] == uc[1]:
							vals = (tv[0])
					val[uc[0]] = vals
			self.gen_dict_path('cal', line, role_name, i[0], (i[2], i[3], val))
	
	def extract_all_calc(self):
		"""Generate all calcuation trees for a given filing."""
		
		tmp_tags = self.cal_sp.find_all('calculationlink')
		if len(tmp_tags) == 0:
			tmp_tags = self.cal_sp.find_all(name=re.compile('calculation[lL]ink'))
		self.data['cal']['xbrl_titles'] = []
		self.data['cal']['roles'] = OrderedDict()
		for tmp in tmp_tags:
			role = tmp.get('xlink:role')
			role = os.path.split(role)[1]
			title = tmp.get('xlink:title')
			self.data['cal']['xbrl_titles'].append((role))
			arcs = tmp.find_all('calculationarc')
			if len(arcs) == 0:
				arcs = tmp.find_all(name=re.compile('calculationarc'))
			locs = tmp.find_all('loc')
			if len(locs) == 0:
				locs = tmp.find_all(name=re.compile('loc'))
			self.make_calc_tree(arcs, locs, role, title)
				
	##########################
	## Presentation Section ##
	##########################	

	def make_pre_tree(self, pre_arcs, pre_locs, role_name, title):
		"""Generate a presentation tree for a specific role 
		   and populate it with values."""
		
		root = []
		to_list = []
		from_list = []
		from_to_pair = [] #(parent, child)
		locs_pairs = []
		for pl in pre_locs:
			tmp_pl_raw = pl.get('xlink:href')
			tmp_pl = os.path.splitext(tmp_pl_raw)[1]
			if '#' in tmp_pl:
				tmp_pl_idx = tmp_pl.index('#')
				tmp_pl = tmp_pl[tmp_pl_idx+1:]
				pfx_loc = self.get_pfx_gen(tmp_pl, 'ins_t')
				name_loc = self.get_name_gen(tmp_pl, 'ins_t')
				locs_pairs.append((pfx_loc, name_loc))
		for i in pre_arcs:
			#Get preferred label
			label_str = i.get('preferredLabel')
			if label_str == None:
				label_str = i.get('preferredlabel')
				if label_str == None:
					label_str = i.get('xlink:preferredLabel')
					if label_str == None:
						label_str = i.get('xlink:preferredlabel')
			if label_str == None:
				label_str = 'label'
			else:
				label_str = os.path.split(label_str)[1]
			#Start to list
			xlink_to = i.get('xlink:to')
			pfx_to = self.get_pfx_gen(xlink_to, 'ins_t')
			name_to = self.get_name_gen(xlink_to, 'ins_t')
			if not pfx_to and not name_to:
				name_to = xlink_to
				for lp in locs_pairs:
					if name_to == lp[1]:
						pfx_to = lp[0]
						break
			if not pfx_to:
				continue
			if pfx_to and not name_to:
				tmp_to_store = xlink_to
				tmp_to = xlink_to.lower()
				idx_name_s = tmp_to.index(pfx_to)
				xlink_to = xlink_to[idx_name_s:]
				try:
					reg_xt = '(?<={0})[^\W_]*'.format(pfx_to)
					reg_xt_ex = re.search(reg_xt, xlink_to)
					name_to = reg_xt_ex.group(0)
				except AttributeError:
					try:
						reg_xt = '(?<={0})[^\W_]*'.format(pfx_to.upper())
						reg_xt_ex = re.search(reg_xt, xlink_to)
						name_to = reg_xt_ex.group(0)
					except AttributeError:
						pass
			if not name_to:
				tmp_pfx = self.get_pfx_gen(xlink_to, 'ins')
				if tmp_pfx:
					tmp_nt = xlink_to.lower()
					end_pfx = tmp_nt.index(tmp_pfx) + len(tmp_pfx)
					name_to = xlink_to[end_pfx:]
					if '_' in name_to:
						xt_idx = name_to.index('_')
						name_to = name_to[:xt_idx]
				if not name_to:
					if '_' not in xlink_to and ':' not in xlink_to and '-' not in xlink_to:
						if isinstance(xlink_to, str):
							if tmp_pfx == None:
								name_to = xlink_to
					if not name_to:
						if pfx_to:
							if '_' not in xlink_to and ':' not in xlink_to and '-' not in xlink_to:
								if isinstance(xlink_to, str):
									name_to = xlink_to
						if not name_to:
							continue
			#Get order
			order = i.get('order')
			if name_to not in to_list:
				to_list.append((pfx_to, name_to, order, label_str))
			#Start From List
			xlink_from = i.get('xlink:from')
			pfx_from = self.get_pfx_gen(xlink_from, 'ins_t')
			name_from = self.get_name_gen(xlink_from, 'ins_t')
			if not pfx_from and not name_from:
				name_from = xlink_from
				for lp in locs_pairs:
					if name_from == lp[1]:
						pfx_from = lp[0]
						break
			if not pfx_from:
				continue
			if pfx_from and not name_from:
				tmp_from_store = xlink_from
				pfx_from = self.get_pfx_gen(xlink_from, 'ins_t')
				tmp_from = xlink_from.lower()
				idx_name_s = tmp_from.index(pfx_from)
				xlink_from = xlink_from[idx_name_s:]
				try:
					reg_xt = '(?<={0})[^\W_]*'.format(pfx_from)
					reg_xt_ex = re.search(reg_xt, xlink_from)
					name_from = reg_xt_ex.group(0)
				except AttributeError:
					try:
						reg_xt = '(?<={0})[^\W_]*'.format(pfx_to.upper())
						reg_xt_ex = re.search(reg_xt, xlink_from)
						name_from = reg_xt_ex.group(0)
					except AttributeError:
						pass
			if not name_from:
				tmp_pfx = self.get_pfx_gen(xlink_from, 'ins')
				if tmp_pfx:
					tmp_nt = xlink_from.lower()
					end_pfx = tmp_nt.index(tmp_pfx) + len(tmp_pfx)
					name_from = xlink_from[end_pfx:]
					if '_' in name_from:
						xt_idx = name_from.index('_')
						name_from = name_from[:xt_idx]
				if not name_from:
					if '_' not in xlink_from and ':' not in xlink_from and '-' not in xlink_from:
						if isinstance(xlink_from, str):
							if tmp_pfx == None:
								name_from = xlink_from
					if not name_from:
						if pfx_from:
							if '_' not in xlink_from and ':' not in xlink_from and '-' not in xlink_from:
								if isinstance(xlink_from, str):
									name_from = xlink_from
						if not name_from:
							continue
			if name_from not in from_list:
				from_list.append((pfx_from, name_from, order, label_str))
			from_to_pair.append((name_from, name_to, order, label_str))
		for i in from_list:
			in_to_list = False
			for x in to_list:
				if i[:2] == x[:2]:
					in_to_list = True
			if not in_to_list:	
				root.append(i)
		root = list(set(root))
		root.sort(key=lambda tup: tup[2])
		to_list.sort(key=lambda tup: tup[2])
		from_list.sort(key=lambda tup: tup[2])
		if len(root) == 0:
			if len(to_list) > 0 or len(from_list) > 0:
				if len(to_list) == 1 and len(from_list) == 0:
					root = to_list
					root = list(set(root))
				elif len(from_list) == 1 and len(to_list) == 0:
					root = from_list
					root = list(set(root))
				elif len(from_list) == 0:
					root = to_list
					root = list(set(root))
				elif len(to_list) == 0:
					root = from_list
					root = list(set(root))
				elif len(from_list) == 1 and len(to_list) > 1:
					root = from_list
					root = list(set(root))
				elif len(from_list) < len(to_list):
					root = from_list
					root = list(set(root))
				elif to_list == from_list:
					root = from_list
					root = list(set(root))
				else:
					pass
		self.data['pre']['roles'][role_name] = OrderedDict()
		self.data['pre']['roles'][role_name]['title_name'] = title
		self.data['pre']['roles'][role_name]['tree'] = OrderedDict()
		self.data['pre']['roles'][role_name]['from_to'] = from_to_pair
		self.data['pre']['roles'][role_name]['root'] = root
		unique_tmp = from_list + to_list
		unique = list(set(unique_tmp))
		self.data['pre']['roles'][role_name]['unique'] = unique
		for i in root:
			self.data['pre']['roles'][role_name]['tree'][i[1]] = OrderedDict()
			self.data['pre']['roles'][role_name]['tree'][i[1]]['pfx'] = i[0]
			self.data['pre']['roles'][role_name]['tree'][i[1]]['sub'] = OrderedDict()
			try:
				label = self.find_label_str((i[0], i[1]))
			except KeyError:
				label = OrderedDict()
				label[0] = i[1]
			if len(label) > 1:
				label_list = []
				try:
					label_keys = label.keys()
					for k in label_keys:
						if label[k] not in label_list:
							label_list.append(label[k])
				except AttributeError:
					label_list.append(label)
				if len(label_list) == 1:
					label = label_list[0]
				else:
					try:
						label = label[i[3]]
					except KeyError:
						label = label['label']
			else:
				label_keys = label.keys()
				label = label[label_keys[0]]
			self.data['pre']['roles'][role_name]['tree'][i[1]]['label'] = label
		for i in to_list:
			try:
				line = self.get_lineage(root, from_to_pair, i[1])
			except RuntimeError:
				self.data['no_lineage'].append(i)
				continue
			line_root = None
			ins_keys = self.data['ins']['facts'].keys()
			for ik in ins_keys:
				found_lr = False
				for l in line:
					try:
						self.data['ins']['facts'][ik][l.lower()]
						line_root = (ik, l)
						found_lr = True
						break
					except KeyError:
						continue
				if found_lr:
					break
			key_ctx_list = []
			try:
				tmp_root = self.data['ins']['facts'][line_root[0]][line_root[1].lower()]['val_by_date']
				root_val = OrderedDict()
				tr_keys = tmp_root.keys()
				tmp_ctx_list = []
				for trk in tr_keys:
					tmps_val = tmp_root[trk]
					root_val[trk] = tmps_val[0][0]
					if (trk, tmps_val[0][1]) not in tmp_ctx_list:
						tmp_ctx_list.append((trk, tmps_val[0][1]))
				if (i[:2], tuple(tmp_ctx_list)) not in key_ctx_list:
					key_ctx_list.append((line_root[:2], tuple(tmp_ctx_list)))
			except (KeyError, TypeError):
				pass
			try:
				use_ctx = None
				for kcl in key_ctx_list:
					if kcl[0] == line_root:
						use_ctx = kcl[1]
				val = OrderedDict()
				for uc in use_ctx:
					try:
						tmp_val = self.data['ins']['facts'][i[0]][i[1].lower()]['val_by_date'][uc[0]]
					except KeyError:
						continue
					vals = None
					for tv in tmp_val:
						if tv[1] == uc[1]:
							vals = (tv[0])
					val[uc[0]] = vals
			except TypeError:
				pass
			try:
				label = self.find_label_str((i[0], i[1]))
			except KeyError:
				label = OrderedDict()
				label[0] = i[1]
			if len(label) > 1:
				try:
					label = label[i[3]]
				except KeyError:
					try:
						label = label['label']
					except KeyError:
						label = i[1]
				except TypeError:
					label = label
			else:
				label_keys = label.keys()
				label = label[label_keys[0]]
			self.gen_dict_path('pre', line, role_name, i[0], (i[2], val, label))
			try:
				label = self.find_label_str((i[0], i[1]))
			except KeyError:
				label = OrderedDict()
				label[0] = i[1]
			if len(label) > 1:
				try:
					label = label[i[3]]
				except KeyError:
					try:
						label = label['label']
					except KeyError:
						label = i[1]
				except TypeError:
					label = label
			else:
				label_keys = label.keys()
				label = label[label_keys[0]]
			self.gen_dict_path('pre', line, role_name, i[0], label)
			
	def extract_all_pre(self):
		"""Generate all presentation trees for a given filing."""
		
		tmp_tags = self.pre_sp.find_all('presentationlink')
		if len(tmp_tags) == 0:
			tmp_tags = self.pre_sp.find_all(name=re.compile('presentation[lL]ink'))
		self.data['pre']['xbrl_titles'] = []
		self.data['pre']['roles'] = OrderedDict()
		for tmp in tmp_tags:
			role = tmp.get('xlink:role')
			role = os.path.split(role)[1]
			title = tmp.get('xlink:title')
			self.data['pre']['xbrl_titles'].append((role, title))
			arcs = tmp.find_all('presentationarc')
			if len(arcs) == 0:
				arcs = tmp.find_all(name=re.compile('presentationarc'))
			locs = tmp.find_all('loc')
			if len(locs) == 0:
				locs = tmp.find_all(name=re.compile('loc'))
			self.make_pre_tree(arcs, locs, role, title)

