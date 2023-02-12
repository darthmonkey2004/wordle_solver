import os
import pickle
import requests
import subprocess

class database():
	def __init__(self, dbfile=None, savefile=None):
		self.data_dir = os.path.join(os.path.expanduser("~"), 'wordle')
		if not os.path.exists(self.data_dir):
			print("Data director doesn't exist! Creating..")
			os.makedirs(self.data_dir, exist_ok=True)
			print("created at:", self.data_dir)
		if dbfile is not None:
			self.dbfile = os.path.join(self.data_dir, os.path.basename(dbfile))
		else:
			self.dbfile = os.path.join(os.path.expanduser("~"), '.local', 'words.db')
	#		self.dbfile = '/home/monkey/wordle/words.db'
		if savefile is not None:
			self.savefile = os.path.join(self.data_dir, os.path.basename(savefile))
		else:
			self.savefile = '/home/monkey/wordle/words.dat'
		self.mkdb()
		print("self.savefile:", self.savefile, "self.dbfile:", self.dbfile)

	def test(self, word):
		rgx = str(list(word)).replace(' ', '').replace("'", '')
		com = f"sqlite3 \"{self.dbfile}\" -cmd \".load /usr/lib/sqlite3/pcre.so\" \"select word from words where word REGEXP \'{rgx}\';\""
		ret = subprocess.check_output(com, shell=True).decode().strip().split("\n")
		if ret != '':
			print(len(ret))
			return ret
		else:
			print("ok!")
		return ret

	def mkdb(self):
		com = f"\"sqlite3\" \"{self.dbfile}\" \"CREATE TABLE IF NOT EXISTS words (id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT, starts_with CHAR, ends_with CHAR, char_0 CHAR, char_1 CHAR, char_2 CHAR, char_3 CHAR, char_4 CHAR);\""
		ret = subprocess.check_output(com, shell=True).decode().strip()
		if ret != '':
			return False, ret
		else:
			return True, None

	def add(self, word):
		com = f"sqlite3 \"{self.dbfile}\" \"INSERT INTO words (word, starts_with, ends_with, char_0, char_1, char_2, char_3, char_4) VALUES(\'{word}\', \'{word[0]}\', \'{word[1]}\', \'{word[0]}\', \'{word[1]}\', \'{word[2]}\', \'{word[3]}\', \'{word[4]}\');\""
		ret = subprocess.check_output(com, shell=True).decode().strip()
		if ret != '':
			return False, ret
		else:
			return True, None

	def grab(self):
		self.mkdb()
		data = self.load()
		ct = len(data)
		pos = 0
		for word in data:
			pos += 1
			print(f"Progress:{pos}/{ct}")
			ret, errmsg = self.add(word)
			if not ret:
				print(f"Error adding word: {errmsg}!")
				input("Press enter to continue..")

	def get_data(self):
		out = []
		string = 'abcdefghijklmnopqrstuvwxyz'
		ct = len(string)
		pos = 0
		for c in string:
			pos += 1
			url = f"https://wordfinderx.com/words-for/_/words-start-with/{c}/length/5/?dictionary=wwf&extended_fields=true&length=5&page_size=1500"
			r = requests.get(url)
			d = r.text.splitlines()
			data = r.text.splitlines()
			dpos = 0
			for line in d:
				dct = len(d)
				dpos += 1
				print(f"progress: {pos}/{ct}, {dpos}/{dct}")
				words = []
				if 'wordblock-link changeable-word' in line:
					word = line.split("data-word='")[1].split("'")[0]
					if word not in out:
						words.append(word)
						self.add(word)
				out += words
		self.save(out)
		print("done!")
		return out

	def save_savefile(self, out):
		try:
			with open(self.savefile, 'wb') as f:
				pickle.dump(out, f)
				f.close()
			return True
		except Exception as e:
			print(f"error saving to save file {self.savefile}: {e}!", 'error')
			return False

	def load_savefile(self):
		print("self.savefile", self.savefile)
		try:
			with open(self.savefile, 'rb') as f:
				out = pickle.load(f)
				f.close()
			return out
		except Exception as e:
			print(f"Error loading save file {self.savefile}: {e}! Rebuilding...", 'error')
			input("Press enter to continue, ctrl+c to abort!")
			out = self.get_data()
			self.save(out)
			return out

	def load(self):
		words = subprocess.check_output(f"sqlite3 \"{self.dbfile}\" \"select distinct word from words;\"", shell=True).decode().strip().split("\n")
		return words
if __name__ == "__main__":
	db = database()
