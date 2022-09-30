#!/usr/bin/env python3


from re import search, findall
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as bs
from collections import OrderedDict

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--incognito')


class wordle():
	def __init__(self):
		self.buttons = {}
		self.present = []
		self.absent = []
		self.correct = []
		self.contains = []
		self.starts_with = None
		self.ends_with = None
		self.words = []
		self.boxes = {}
		self.round = 0
		self.locked = {}
		self.locked[0] = False
		self.locked[1] = False
		self.locked[2] = False
		self.locked[3] = False
		self.locked[4] = False
		self.blacklist = {}
		self.blacklist[0] = []
		self.blacklist[1] = []
		self.blacklist[2] = []
		self.blacklist[3] = []
		self.blacklist[4] = []
		self.chars = None# initialize main container data for extracted element values
		self.char = {}
		self.char[0] = None
		self.char[1] = None
		self.char[2] = None
		self.char[3] = None
		self.char[4] = None
		self.driver = webdriver.Chrome(chrome_options=chrome_options)
		self.driver.get('https://www.nytimes.com/games/wordle/index.html')
		self.words_url = None
		self.regex = None
		

	def check_word(self, word):
		url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
		r = requests.get(url)
		if r.status_code == 200:
			return True
		else:
			return False


	def get_buttons(self, html):
		self.buttons = OrderedDict()
		btns = html.findAll('div', {'class': 'Keyboard-module_keyboard__1HSnn'})
		set_btns = html.findAll('div', {'class': 'Key-module_key__Rv-Vp Key-module_fade__37Hk8'})
		rows = html.findAll('div', {'class': 'Keyboard-module_row__YWe5w'})
		txt = str(next(next(btns[0].children).children))
		#for row in btns:
		for row in rows:
			bs = html.findAll('button', {'class': 'Key-module_key__Rv-Vp'})
			pos = -1
			for btn in bs:
				d = {}
				if 'data-state' in str(btn):
					pos += 1
					if pos == 3:
						pos = 0
					elif pos == 4:
						pos = 1
					elif pos == 1:
						pos = 2
					elif pos == 0:
						pos = 3
					elif pos == 2:
						pos = 4
					d['data_state'] = str(btn).split('data-state="')[1].split('"')[0]
					d['idx'] = pos
					d['val'] = str(btn).split('data-key="')[1].split('"')[0]
					val = d['val']
					#print("Data state: ", d['data_state'])
					self.buttons[val] = d
					
		return self.buttons


	def auth(self):
		try:
			return self._get_auth()
		except Exception as e:
			log(f"Couldn't get credentials from keystore! Please re-enter Wordle credentials (fomat: 'email:password')", 'warning')
			if self._set_auth():
				log(f"Success!", 'info')
				return self._get_auth()
				

	def _get_auth(self):
		return subprocess.check_output(f"secret-tool lookup wordle authstr", shell=True).decode().strip()


	def _set_auth(self):
		ret = subprocess.check_output(f"secret-tool store --label=\"wordle_helper\" wordle authstr", shell=True).decode.strip()
		if ret != '':
			log(f"Error saving password: {ret}", 'error')
			return False
		else:
			return True


	def get_chars(self):
		self.chars = {}
		pos = 0
		_id = 0
		text = None
		char = None
		state = None
		idx = None
		html_to_parse = str(self.driver.page_source)
		html = bs(html_to_parse, 'html.parser')
		elems = html.findAll('div', {'class': 'Tile-module_tile__3ayIZ'})
		row = 1
		d = {}
		for line in elems:
			if 'data-state="empty"' not in line and 'data-state="tbd"' not in line:
				try:
					out = str(line).split('aria-label="')[1].split('"')[0].split(' ')
					c = True
				except Exception as e:
					c = False
				if c is True:
					try:
						state = out[1]
					except:
						state = None
					if out[0] is not None and out[0] != 'empty' and state is not None:
						pos += 1
						if pos == 6:
							row += 1
							pos = 1
						else:
							_id += 1
						try:
							d = self.chars[row]
						except:
							self.chars[row] = {}
							d = self.chars[row]
						d[pos] = {}
						try:
							char, state = out
							if state == 'tbd':
								char, state = None, None
						except:
							pass
						if char is not None and state is not None:
							d[pos] = {}
							d[pos]['state'] = state
							d[pos]['char'] = char
							d[pos]['id'] = _id
		return self.chars



	def write(self, slot, char):
		if self.lock[slot] is not True:
			if char not in self.blacklist[slot]:
				self.char[slot] = char
				print(f"Updated index {slot} with '{char}'!")
				return True
			else:
				print(f"already tried this slot ({slot}, char={char}). Skipping...")
				return False
		else:
			print(f"Slot is already locked to correct value! Slot:{slot}, Value:{char}")
			return False


	def block(self, slot, char):
		if char not in self.blacklist[slot]:
			self.blacklist[slot].append(char)
			return True
		else:
			#print(f"Blacklist already contains char {char} in slot {slot}!")
			return False


	def lock(self, slot, char):
		if self.locked[slot] is False:
			self.char[slot] = char
			self.locked[slot] = True
			return True
		else:
			print(f"Error: Already locked to correct value: {self.char[slot]}!")
			return False
	


	def update(self, data=None):
		if self.chars is None or self.chars == {}:
			self.chars = self.get_chars()
		if self.chars == {}:
			return None
		complete_ct = 0
		completed_ct = len(self.char)
		for val in self.char.values():
			if val is not None:
				complete_ct += 1
		if complete_ct == completed_ct:
			self.match = f"{self.char[0]}{self.char[1]}{self.char[2]}{self.char[3]}{self.char[4]}"
			print(f"Match found! (From all characters filled) Match: {self.match}, All characters confirmed ({complete_ct}/{completed_ct})")
			return True
		state = None
		char = None
		if data is None:
			data = self.get_chars()
		for row in data.keys():
			row_data = data[row]
			for idx in row_data.keys():
				#step idx down for python array indexes
				pos = idx - 1
				elem_data = row_data[idx]
				l = list(elem_data.values())
				for item in l:
					state, char, _id = l
					if state == 'present':
						#if present (exists but wrong position) flag set, add to blocklist on this index, add to contains.
						if char not in self.contains:
							self.contains.append(char)
						if char not in self.present:
							self.present.append(char)
						self.block(pos, char)
					elif state == 'absent':
						# if absent flag for char is set, add to blocklist on all slots
						for i in range(0, 5):
							if char not in self.blacklist[i]:
								#print(f"Updated blacklist for slot {i}: {char}")
								self.block(i, char)
						#add to absent list
						if char not in self.absent and char not in self.correct:
							#if char not in absent list AND not in correct list(Not sure how they wind up here yet...)
							self.absent.append(char)
					elif state == 'correct':
						ret = True
						#if present and in correct position, lock to slot (prevents write change), add to contains.
						pos = idx - 1
						if self.locked[pos] is False:
							ret = self.lock(pos, char)
							#print(f"locked value {char} to pos {pos}! Chars: {self.char}")
						if char not in self.contains:
							self.contains.append(char)
						if char not in self.correct:
							self.correct.append(char)
						if ret:
							if ret is not True:
								print(f"Lock returned data: {ret}")
								input("Press a key to continue...")
						else:
							print("ok")
						if pos == 0 and self.starts_with is None:
							self.starts_with = char
							print("startswith:", char)
						elif pos == 4 and self.ends_with is None:
							self.ends_with = char
							print("endswith:", char)
		if len(self.words) == 0:
			self.get_words()
		matches = self.get_matches()
		if matches is not None:
			if len(matches) > 1:
				return False
			elif len(matches) == 1:
				self.match = matches[0]
				print(f"Match found: (From wordlist regex) Match: {self.match}")
				return True
		else:
			return False


	def get_words(self):
		#alpha = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
		#letters = []
		#for a in alpha:
		#	if a not in self.absent:
		#		letters.append(a)
		j = ''
		base_url = 'https://fly.wordfinderapi.com/api/search'
		query_string = []
		query_string.append("length=5")
		#contains = j.join(letters)
		#self.contains = contains
		#query_string.append(f"letters={contains}")
		query_string.append(f"word_sorting=az")
		query_string.append(f"group_by_length=true")
		query_string.append(f"page_size=100000")
		query_string.append(f"dictionary=wwf2")
		absent = j.join(self.absent)
		query_string.append(f"exclude_letters={absent}")
		if self.starts_with is not None:
			query_string.append(f"starts_with={self.starts_with}")
		if self.ends_with is not None:
			query_string.append(f"ends_with={self.ends_with}")
		j = '&'
		query_string = j.join(query_string)
		self.words_url = f"{base_url}?{query_string}"
		r = requests.get(self.words_url)
		results = json.loads(r.text)['word_pages']
		if results is not None:
			try:
				for result in results:
					for word in result['word_list']:
						self.words.append(word['word'])
				return self.words
			except Exception as e:
				print(f"Error getting words list: {e}, Results:{results}")
		else:
			print("Results was None?? Status Code:", r.status_code, "Data:", r.text)
			return []
			
	



	def get_missing(self, _list):
		print(_list, type(_list))
		return [x for x in range(_list[0], _list[-1]+1) if x not in _list]

	def get_matches(self, chars=None):
		self.regex = None
		if chars is None:
			char = self.char
		j = ''
		l = []
		for i in range(0, 5):
			l.append(None)

		for idx in char.keys():
			c = char[idx]
			if c is not None:
				l[idx] = c
			else:
				l[idx] = '.'
		self.regex = j.join(l)
		if self.regex == '.....':
			self.regex = None
		if self.regex is not None:
			#print("Searching with regex:", self.regex)
			sw = str(self.words)
			matches = findall(self.regex, sw)
			if matches is not None:
				m = []
				for match in matches:
					if match not in m:
						m.append(match)
				matches = m
				#s, e = matches.span()
				#match = sw[s:e]
				if len(matches) == 1:
					match = matches[0]
					return match
				else:
					self.words = matches
					return self.words
			else:
				print("No matches for regex:", self.regex)
				return None


if __name__ == "__main__":
	wordle = wordle()
	init_chars = wordle.get_chars()
	import time
	time.sleep(2)
	wordle.driver.find_element(by='xpath', value='//div[@class=\"Modal-module_closeIcon__b4z74\"]').click()
	time.sleep(2)
	update = False
	#initial update
	print("Initializing...")
	wordle.update()
	print("Starting loop! (Word count:)", len(wordle.words), "Chars:", wordle.char)
	while True:
		t = 0
		vals = wordle.char.values()
		for val in vals:
			if val is None:
				break
			else:
				t += 1
		if t == 5:
			wordle.match = f"{wordle.char[0]}{wordle.char[1]}{wordle.char[2]}{wordle.char[3]}{wordle.char[4]}"
			print("Match found!", wordle.match)
			break
		wordle.get_chars()
		if init_chars != wordle.chars:
			init_chars = wordle.chars
			update = True
		else:
			update = False
		if update is True:
			print("Updating in 3...")
			time.sleep(1)
			print("Updating in 2...")
			time.sleep(1)
			print("Updating in 1...")
			time.sleep(1)
			print("Updating...")
			hasmatch = wordle.update()
			if hasmatch is not None:
				if hasmatch is True:
					print("Match found!", match)
					break
				else:
					if len(wordle.words) > 75:
						suggested = wordle.words[0]		
						print(f"Suggested word: {suggested}")
						print(f"Absent: {len(wordle.absent)}, Present: {len(wordle.present)}, Correct: {len(wordle.correct)}")
					elif len(wordle.words) <= 75:
						print(wordle.words)
					elif len(wordle.words) == 0:
						print(f"Words is empty??? {wordle.words}")
		time.sleep(2)

