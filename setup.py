from distutils.core import setup

setup(name='wordle_helper',
	version='1.1',
	description='Python Wordle helper',
	author='Matt McClellan',
	author_email='darthmonkey2004@gmail.com',
	url='http://www.simiantech.biz/',
	scripts=['install.sh', 'solver.py'],
	py_modules=['wordtester', 'wordle', 'db_get_data'],
	data_files=['words.db'],
	)
