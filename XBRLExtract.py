import settings
import os
import re
import pandas as pd
import pickle
from bs4 import BeautifulSoup as BS

class CalcDictTree:

	def __init__(self, calc_data):
		self.calc_data = calc_data
		self.calc_keys = self.calc_data.keys()

		self.data = {}

		self.populate_tree()

	def get_parent(self, ele):
		try:
			parent = self.calc_data[ele.lower()]['parent']
			ele_re = re.search('(?<=:).+', parent)
			ele_parent = ele_re.group(0)
			return ele_parent.lower()
		except (KeyError, TypeError):
			return False

	def get_levels(self, elem, tree_list=None):
		if not tree_list:
			tree_list = []
		par = self.get_parent(elem.lower())
		if not par:
			tree_list.insert(0, elem.lower())
			return tree_list
		else:
			tree_list.insert(0, elem.lower())
			return self.get_levels(par, tree_list)

	def gen_dict_path(self, list_order, assign=True, ref_self='self'):
		base_str = "{0}.data['tree']".format(ref_self)
		for i in list_order:
			next_ele = "['{0}']".format(i)
			base_str += next_ele
		if assign:
			base_str += ' = {}'
		return base_str

	def check_exist(self, path):
		try:
			exec(path)
			return True
		except KeyError:
			return False

	def populate_tree(self):
		self.data['levels'] = {}
		self.data['tree'] = {}
		for k in self.calc_keys:
			levels = self.get_levels(k)
			self.data['levels'][k] = levels
			for i in range(len(levels)):
				if (i + 1) == len(levels):
					dict_path = self.gen_dict_path(levels)
					path_no_assign = self.gen_dict_path(levels, False)
				else:
					dict_path = self.gen_dict_path(levels[:i+1])
					path_no_assign = self.gen_dict_path(levels[:i+1], False)
				if self.check_exist(path_no_assign):
					pass
				else:
					exec(dict_path)
				
				

class XBRLTaxonomy:

	def __init__(self):
		self.xbrl_elements_csv = os.listdir(settings.XBRL_ELEMENTS_PATH)
		self.xbrl_calcs_csv = os.listdir(settings.XBRL_CALCS_PATH)

		self.elements = 'elements'
		self.calcs = 'calculations'

		self.elements_col_names = None
		self.calcs_col_names = None
		
		self.data = {}
		
		self.add_years()
		self.add_main_sects()
		self.make_ele_cols()
		self.make_calcs_cols()
		self.extract_all_data()
		self.save_all()

	def load_data(self, filename):
		return pd.read_csv(filename)

	def get_year(self, filename):
		return os.path.splitext(filename)[0][:4]

	def add_years(self):
		for item in self.xbrl_elements_csv:
			year = self.get_year(item)
			self.data[year] = {}

	def add_main_sects(self):
		for key in self.data.keys():
			self.data[key][self.elements] = {}
			self.data[key][self.calcs] = {}

	#Elements Methods

	def make_ele_cols(self):
		for xc in self.xbrl_elements_csv:
			year = self.get_year(xc)
			df = pd.read_csv('{0}/{1}'.format(settings.XBRL_ELEMENTS_PATH, xc))
			col_names = list(df.columns.values)
			self.data[year][self.elements]['col_names'] = col_names

	def extract_ele_data(self, fn):
		data = self.load_data('{0}/{1}'.format(settings.XBRL_ELEMENTS_PATH, fn))
		year = self.get_year(fn)
		for i in range(len(data)):
			try:
				name = data.ix[i]['name'].lower()
			except AttributeError:
				name = data.ix[i]['label']
			self.data[year][self.elements][name] = {}
			for col in self.data[year][self.elements]['col_names']:
				 self.data[year][self.elements][name][col] = data.ix[i][col]

	#Calculations Methods

	def make_calcs_cols(self):
		for xc in self.xbrl_calcs_csv:
			year = self.get_year(xc)
			df = pd.read_csv('{0}/{1}'.format(settings.XBRL_CALCS_PATH, xc))
			if year in ['2014', '2016']:
				ixno = 2
			elif year in ['2008', '2009', '2011', '2012', '2013']:
				ixno = 1
			temp_cols = list(df.ix[ixno])
			col_names = []
			for i in temp_cols:
				col_names.append(str(i))
			self.data[year][self.calcs]['col_names'] = col_names

	def check_all_nan(self, data_list):
		nan_count = 0
		size = len(data_list)
		for i in data_list:
			if i == float('nan'):
				nan_count += 1
		if nan_count == size:
			return True
		return False

	def extract_calcs_data(self, fn):
		data = self.load_data('{0}/{1}'.format(settings.XBRL_CALCS_PATH, fn))
		year = self.get_year(fn)
		self.data[year][self.calcs]['all_calcs'] = {}
		self.data[year][self.calcs]['all_calcs']['main'] = {}
		calcs_name = None
		for i in range(len(data)):
			tmp_data = list(data.ix[i])
			if self.check_all_nan(tmp_data):
				continue
			else:
				if tmp_data[0] == 'LinkRole':
					calcs_name = os.path.split(tmp_data[1])[1].lower()
					self.data[year][self.calcs][calcs_name] = {}
					self.data[year][self.calcs][calcs_name]['main'] = {}
				elif tmp_data[0] in ['Definition', float('nan')]:
					continue
				elif tmp_data[0] in self.data[year][self.calcs]['col_names']:
					continue
				else:
					try:
						self.data[year][self.calcs][calcs_name]['main'][tmp_data[1].lower()] = {}
						self.data[year][self.calcs]['all_calcs']['main'][tmp_data[1].lower()] = {}
						for x in tmp_data:
							tmp_idx = tmp_data.index(x)
							col_name = self.data[year][self.calcs]['col_names'][tmp_idx]
							self.data[year][self.calcs][calcs_name]['main'][tmp_data[1].lower()][col_name] = x
							self.data[year][self.calcs]['all_calcs']['main'][tmp_data[1].lower()][col_name] = x
					except AttributeError:
						continue

	def add_calc_trees(self, year):
		calc_names = self.data[year][self.calcs].keys()
		for calc in calc_names:
			if calc in ['col_names', 'all_calcs']:
				continue
			tmp_calc = CalcDictTree(self.data[year][self.calcs][calc]['main'])
			self.data[year][self.calcs][calc]['calc_tree'] = tmp_calc.data	

	def extract_all_data(self):
		for fname in self.xbrl_elements_csv:
			self.extract_ele_data(fname)
			print(fname + ' ' + 'elements')
		for fname in self.xbrl_calcs_csv:
			print(fname + ' ' + 'calcs')
			self.extract_calcs_data(fname)
			fn_year = self.get_year(fname)
			self.add_calc_trees(fn_year)
	
	def save_all(self):
		pickle.dump(self.data, open(settings.XBRL_DICT_PATH, 'wb'))	

if not os.path.exists(settings.XBRL_DICT_PATH,):
	tmp = XBRLTaxonomy()
	xbrl = tmp.data
else:
	with open(settings.XBRL_DICT_PATH, 'rb') as f:
		xbrl = pickle.load(f)

def traverse_print_tree(base, role_keys, tabs=0):
	"""Traverse cal tree and print."""

	for rk in role_keys:
		if rk == 'sub':
			continue
		tab_str = '   ' * tabs
		try:
			lab_str = tab_str + str(rk)
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
			traverse_print_tree(rk_base, rk_base_keys, tabs=tabs+1)
			
def traverse_tree(data, year, name):
	base = data[year]['calculations'][name]['calc_tree']
	base_tree = base['tree']
	role_keys = base_tree.keys()
	traverse_print_tree(base_tree, role_keys)

def traverse_all_trees(data):
	base = data['pre']['roles']
	base_keys = base.keys()
	for bk in base_keys:
		print('\033[1m' + 'Title:' + ' ' + bk + '\033[0m')
		traverse_tree(bk)
		print('\n\n')
	
