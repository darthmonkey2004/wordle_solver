import getpass
from db_get_data import *
import keyring
from random import shuffle
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import time
from wordtester import *
class Wordle():
	def __init__(self, guess=None, headless=False, dbfile=None, savefile=None):
		self.present = {}
		self.absent = ''
		self.correct = '_____'
		self.tried_words = []
		self.turn = 0
		self.words = []
		self.chars = {}
		self.starts_with = None
		self.ends_with = None
		self.tester = tester()
		self.db = database()
		self.words = self.db.load()
		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_argument('--incognito')
		if headless:
			chrome_options.add_argument('--headless')
		self.driver = webdriver.Chrome(chrome_options=chrome_options)
		self.driver.get('https://www.nytimes.com/games/wordle/index.html')
		self.open_guesses = ['later', 'adieu', 'audio', 'auloi', 'aurei', 'louie', 'miaou', 'ouija', 'ourie', 'uraei', 'antre', 'irate']
		src = self.driver.page_source
		s = 'Modal-module_closeIcon'
		if s in src:
			t = src.split(s)[1].split('"')[0]
			#split = f"{s}{t}"
			close_icon = f"{s}{t}"
			val = f"//button[@class=\"{close_icon}\"]"
			#val = '//button[@class=\"Modal-module_closeIcon__b4z74\"]'
			try:
				self.driver.find_element(by='xpath', value=val).click()
			except:
				pass
		self.data_dir = os.path.join(os.path.expanduser("~"), 'wordle')
		if dbfile is not None:
			self.dbfile = os.path.join(self.data_dir, os.path.basename(dbfile))
		else:
			self.dbfile = os.path.join(self.data_dir, 'words.db')
		if savefile is not None:
			self.savefile = os.path.join(self.data_dir, os.path.basename(savefile))
		else:
			self.savefile = os.path.join(self.data_dir, 'words.dat')

	def test(self, word):
		#update first before test to ensure latest
		self.update()
		ret = self.tester.test(word)
		if ret:
			self.starts_with = self.tester.starts_with
			self.ends_with = self.tester.ends_with
			print("Word works!", word)
		else:
			pass
			#print("Word failed!", word)
		return ret

	def update(self):
		words = []
		word = ''
		self.chars = self._get_chars()
		for turn in self.chars.keys():
			self.turn = turn
			for pos in self.chars[turn].keys():
				char = self.chars[turn][pos]['char']
				state = self.chars[turn][pos]['state']
				idx = self.chars[turn][pos]['id'] - 1
				#print(f"char:{char}, idx:{idx}, state:{state}")
				word += char
				if state == 'absent':
					self._add_absent(char)
				elif state == 'present':
					self._add_present(char, idx)
				elif state == 'correct':
					self._add_correct(char, idx)
			words.append(word)
		self.tried_words = words
		self.tester.update(correct=self.correct, absent=self.absent, present=self.present)
		testwords = self.words
		words = []
		for word in testwords:
			#print(word)
			if word not in self.tried_words:
				if self.tester.test(word):
					success = True
					if self.starts_with is not None:
						ret1 = self.tester._starts_with(word, self.correct)
						if ret1:
							success = True
						else:
							success = False
					if self.ends_with is not None:
						ret2 = self.tester._ends_with(word, self.correct)
						if ret2:
							success = True
						else:
							success = False
					if success:
						words.append(word)
		self.words = words
		print("updated!")
		print("len words:", len(self.words))
		if '_' in self.correct:
			self.game_over = False
		else:
			self.game_over = True
			print("match found!", self.correct)
		return self.game_over

	def _add_correct(self, char, idx):
		if char not in self.correct:
			l = list(self.correct)
			try:
				l[idx] = char
				j = ''
				self.correct = j.join(l)
			except Exception as e:
				print(f"Couldn't add char ({char}) to correct list ({l}, idx:{idx}): {e}!")
		else:
			print(f"{char} already in ({self.correct})!")
		return self.correct

	def _add_present(self, char, idx):
		if char not in self.present:
			self.present[char] = idx
		else:
			tidx = self.present[char]
			if type(tidx) == int:
				if idx == tidx:
					print(f"{char} already in present ({self.present})!")
				else:
					self.present[char] = [tidx, idx]
			elif type(tidx) == list:
				if idx not in tidx:
					self.present[char].append(idx)
		return self.present


	def _add_absent(self, char):
		if char not in self.absent and char not in self.correct and char not in list(self.present.keys()):
			self.absent += char
		else:
			print(f"{char} already in absent ({self.absent})!")
		return self.absent
			

	def _get_chars(self):
		self.chars = {}
		pos = 0
		_id = 0
		text = None
		char = None
		state = None
		idx = None
		html_to_parse = str(self.driver.page_source)
		s = 'Tile-module_tile'
		t = html_to_parse.split(s)[1].split('"')[0]
		tilexpath = f"{s}{t}"
		html = bs(html_to_parse, 'html.parser')
		elems = html.findAll('div', {'class': tilexpath})
		row = 1
		d = {}
		for line in elems:
			if 'data-state="empty"' not in line and 'data-state="tbd"' not in line:
				try:
					out = str(line).split('aria-label="')[1].split('"')[0].split(' ')
					c = True
				except Exception as e:
					c = False
				if c:
					try:
						state = out[1]
					except:
						state = None
					if out[0] is not None and out[0] != 'empty' and state is not None:
						pos += 1
						if pos >= 1 and pos <= 5:
							idx = pos
						elif pos >= 6 and pos <= 10:
							idx = pos - 5
						elif pos >= 11 and pos <= 15:
							idx = pos - 10
						elif pos >= 16 and pos <= 20:
							idx = pos - 15
						elif pos >= 21 and pos <= 25:
							idx = pos - 20	
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
							d[pos]['id'] = idx
		return self.chars

	def guess(self, word):
		for char in word:
			self.send_letter(char)
		self.submit()
		self.tried_words.append(word)

	def send_letter(self, char):
		e = self.driver.find_element(by='xpath', value=f"//button[@data-key=\"{char}\"]").click()

	def submit(self):
		self.send_letter('↵')

	def auth(self):
		try:
			return self._get_auth()
		except Exception as e:
			log(f"Couldn't get credentials from keystore! Please re-enter Wordle credentials (fomat: 'email:password')", 'warning')
			if self._set_auth():
				log(f"Success!", 'info')
				return self._get_auth()
				

	def _get_auth(self):
		#return subprocess.check_output(f"secret-tool lookup wordle authstr", shell=True).decode().strip()
		return keyring.get_password('wordle', 'authstr')

	def _set_auth(self):
		#ret = subprocess.check_output(f"secret-tool store --label=\"wordle_helper\" wordle authstr", shell=True).decode.strip()
		#if ret != '':
		#	log(f"Error saving password: {ret}", 'error')
		#	return False
		#else:
		#	return True
		pw = getpass.getpass("Enter username:password now:")
		try:
			keyring.set_password('wordle', 'authstr', pw)
			return pw
		except Exception as e:
			print("uh.....", e)
			return None

def get_startswith(correct):
	startswith = []
	for c in correct:
		if c != '_':
			startswith.append(c)
		else:
			break
	return ''.join(startswith)


def _ends_with(word, chars):
	if type(chars) == str:
		chars = list(chars)
	print(len(chars))
	rets = []
	if len(chars) > 1:
		cidx = 4 - (len(chars) - 1)
		for char in chars:
			if char in word:
				idx = word.index(char)
				if cidx != idx:
					rets.append(False)
				else:
					rets.append(True)
		if False in rets:
			return False
		else:
			return True	
	elif len(chars) == 1:
		rgx = f"{chars}$"
		l = re.findall(rgx, word)
		if l == []:
			return False
		else:
			return True


def get_endswith(correct):
	endswith = []
	for c in correct:
		if c == '_':
			endswith = []
		else:
			endswith.append(c)
	return ''.join(endswith)



def test(wordle):
	words = wordle.words
	startswith = get_startswith(wordle.correct)
	endswith = get_endswith(wordle.correct)
	keepers = []
	loseres = []
	for word in words:
		ret = wordle.tester._starts_with(word, startswith)
		if ret:
			keepers.append(word)
		else:
			losers.append(word)
		ret = wordle_tester._ends_with(word, endswith)
		if ret:
			if word not in keepers:
				keepers.append(word)
		else:
			if word not in losers:
				losers.append(word)
	wordle.words = keepers
	keepers = []
	return wordle


if __name__ == "__main__":
	wordle = Wordle()
	shuffle(wordle.open_guesses)
	guess = wordle.open_guesses[0]
	wordle.guess(guess)#turn 1
	time.sleep(1)
	over = wordle.update()
	if over:
		print("Game over! Exiting...")
		wordle.driver.quit()
	time.sleep(1)
	wordle = test(wordle)
	words = wordle.words
	shuffle(words)
	guess = words[0]
	wordle.guess(guess)#turn 2
	over = wordle.update()
	if over:
		print("Game over! Exiting...")
		wordle.driver.quit()
	time.sleep(1)
	wordle = test(wordle)
	words = wordle.words
	shuffle(words)
	guess = words[0]
	wordle.guess(guess)#turn 3
	over = wordle.update()
	if over:
		print("Game over! Exiting...")
		wordle.driver.quit()
	time.sleep(1)
	wordle = test(wordle)
	words = wordle.words
	shuffle(words)
	guess = words[0]#turn4
	wordle.guess(guess)
	over = wordle.update()
	if over:
		print("Game over! Exiting...")
		wordle.driver.quit()
	time.sleep(1)
	wordle = test(wordle)
	words = wordle.words
	shuffle(words)
	guess = words[0]#turn5
	wordle.guess(guess)
	over = wordle.update()
	if over:
		print("Game over! Exiting...")
		wordle.driver.quit()
	
	
	
	
	ret = subprocess.check_output(f"kill $(pgrep chromedriver)", shell=True).decode().strip()
	exit()
