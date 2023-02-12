from distutils.core import setup

setup(name='wordle_solver',
	version='1.1',
	description='Python Wordle solver',
	author='Matt McClellan',
	author_email='darthmonkey2004@gmail.com',
	url='http://www.simiantech.biz/',
	scripts=['install.sh', 'wordle-solver'],
	py_modules=['wordtester', 'wordle', 'db_get_data'],
	data_files=[ ('share/applications', ['wordle-solver.desktop']), 'words.db', 'wordle-solver.jpg'],
	)
