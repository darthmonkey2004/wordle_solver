#!/usr/bin/python3

import time
from wordle import *
from random import shuffle

w = Wordle()
shuffle(w.open_guesses)
guess = (w.open_guesses[0])
w.guess(guess)
time.sleep(2)
ret = w.update(); print("Update return:", ret)
if ret:
	exit()
time.sleep(2)

shuffle(w.words)
guess = (w.words[0])
w.guess(guess)
time.sleep(2)
ret = w.update(); print("Update return:", ret)
if ret:
	exit()
time.sleep(2)

shuffle(w.words)
guess = (w.words[0])
w.guess(guess)
time.sleep(2)
ret = w.update(); print("Update return:", ret)
if ret:
	exit()
time.sleep(2)

shuffle(w.words)
guess = (w.words[0])
w.guess(guess)
time.sleep(2)
ret = w.update(); print("Update return:", ret)
if ret:
	exit()
time.sleep(2)

shuffle(w.words)
guess = (w.words[0])
w.guess(guess)
time.sleep(2)
ret = w.update(); print("Update return:", ret)
if ret:
	exit()
time.sleep(2)
