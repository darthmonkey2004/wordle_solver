import re
from db_get_data import *

class tester():
	def __init__(self, correct='_____', present={}, absent='', starts_with=None, ends_with=None):
		self.correct = correct
		self.present = present
		self.absent = absent
		self.starts_with = starts_with
		self.ends_with = ends_with
		self.tries = []
		self.db = database()
		self.words = self.db.load()

	def update(self, correct=None, present=None, absent=None):
		#print("updating...")
		if correct is not None:
			if type(correct) == list or type(correct) == str:
				self.correct = correct
				#print("Updated correct!", self.correct)
			else:
				#print("error, correct wrong type!", type(correct))
				return False
		if present is not None:
			if type(present) == dict:
				self.present = present
				#print("Updated present!", self.present)
			else:
				#print("error, present is not a dict!", type(present))
				return False
		if absent is not None:
			if type(absent) == list or type(absent) == str:
				self.absent = absent
				#print("Updated absent!")
			else:
				#print("error, absent wrong type!", type(absent))
				return False
		return True

	def _get_idx(self, word, char):
		try:
			return word.index(char)
		except:
			return None

	def _present(self, word, chars, return_data=False):
		out = {}
		if type(chars) == str:
			chars = list(chars)
		#if chars list is not empty...
		if chars != []:
			#test chars against word
			ret = re.findall(str(chars), word)
		else:
			#else no restrictions apply here, so return True
			return True
		if len(ret) > 0:
			for c in ret:
				idx = word.index(c)
				out[c] = idx
			if return_data:
				return True, out
			else:
				return True
		else:
			if return_data:
				return False, None
			else:
				return False

	def _absent(self, word, chars):
		#print("word:", word, "chars:", type(chars))
		if chars != '':
			ret = self._present(word, chars)
			if not ret:
				return True
			if ret:
				return False
		else:
			return True

	def _starts_with(self, word, chars):
		if type(chars) == str:
			chars = list(chars)
		if chars == []:
			return True
		else:
			rgx = f"^{chars}"
			l = re.findall(rgx, word)
			if len(l) > 0:
				return True
			else:
				return False
	

	def _ends_with(self, word, chars):
		if type(chars) == str:
			chars = list(chars)
		if len(chars) > 1:
			cidx = 4 - (len(chars) - 1)
			for char in chars:
				if char in word:
					idx = word.index(char)
					if cidx != idx:
						return False
		elif len(chars) == 1:
			rgx = f"{chars}$"
			l = re.findall(rgx, word)
			if l == []:
				return False
			else:
				return True

	def test_correct(self, word, c=['_', '_', '_', '_', '_']):
		tries = []
		if c != '_____' and c != ['_', '_', '_', '_', '_']:
			#if characters in 'correct' exist in word...
			if not self.test_string_in(word):
				return False, -1
			if self._present(word, c, True):
				#loop through for positional testing
				for char in c:
					tries.append(char)
					if char != '_':
						idx = c.index(char)
						try:
							ret, idxs = self._present(word, char, True)
						except:
							#print(idx, char, c)
							return False, idx
						#grab and test index in correct and compare with word letter match
						if ret:
							if idx == idxs[char]:
								if char not in tries:
									tries.append(char)
									return True, idx
								else:
									#print("char in, got double in word.")
									return True, -2
							else:
								if char in word:
									return True, word.index(char)
								else:
									#print(f"char {char} not in word!")
									return False, None
						else:
							#print("False?", c, ret, idxs)
							return False, None
							#if not match, return False
						if idx == 0:
							self.starts_with = char
						if idx == 4:
							self.ends_with = char
		#if all tests pass without returning False, return True
		return True, None

	def test_absent(self, word, a=''):
		return self._absent(word, a)

	def test_present(self, word, p={}):
		#p should be a dictionary
		#when the tested letter comes back as present,
		#insert the character and its index in the word
		#to ensure future words pass the "doesn't belong here" test.
		chars = list(p.keys())
		# create list of chars from dict
		if self._present(word, chars):
			#if intial test true, loop through c
			for c in chars:
				if c not in word:
					return False
				#grab index of blocked slot
				if type(p[c]) == int:
					match_indexes = [p[c]]
				else:
					match_indexes = p[c]
				for idx in match_indexes:
					#test and get index
					ret, idxs = self._present(word, c, True)
					#if blocked slot not current position...
					if ret:
						print("test present:", ret, idxs)
						if idx != idxs[c]:
							pass
						else:
							#if position is blocked slot, return False
							return False
						print(ret, idx, idxs)
					else:
						print("failed!")
						return False
		else:
			return False
		#if all checks pass, return True
		return True

	def test(self, word):
		isabsent = self.test_absent(word, self.absent)
		if not isabsent:
			return False
		ispresent = self.test_present(word, self.present)
		if not ispresent:
			return False
		iscorrect, idx = self.test_correct(word, self.correct)
		#Fprint(iscorrect, ispresent, isabsent)
		if not iscorrect:
			return False
		if ispresent and isabsent and iscorrect:
			return True


	def test_string_in(self, word):
		chars = self.correct
		ret = []
		chunks = chars.replace('_', ' ').strip().split(' ')
		if '' in chunks:
			idx = chunks.index('')
			_ = chunks.pop(idx)
		for chunk in chunks:
			if chunk in word:
				widx = word.index(chunk)
				cidx = chars.index(chunk)
				if widx != cidx:
					ret.append(False)
				else:
					ret.append(True)
			else:
				ret.append(False)
		if False in ret:
			ret = False
		else:
			ret = True
		return ret

	def test_words(self, words=None):
		if words is not None:
			self.words = words
		keepers = []
		for word in self.words:
			if self.test(word):
				keepers.append(word)
		return keepers

if __name__ == "__main__":
	t = tester()
	t.update(absent="fql", present={"s": 2, "m": 3, "t": 0}, correct="____t")
	#print(f"present:{t.present}, absent:{t.absent}, correct:{t.correct}")
	ret = t.test(word="smart")
	print(ret)
