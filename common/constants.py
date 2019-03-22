from os.path import abspath, dirname, join

PROJECT_PATH = dirname(dirname(abspath(__file__)))
DIVIDER = '|'
PATH_TO_DATA_DIR = join(PROJECT_PATH, 'files')
PATH_TO_RESULT_DIR = join(PROJECT_PATH, 'data')
PATH_TO_LIST_OF_FILES = join(PROJECT_PATH, 'data', 'files')
PATH_TO_DICT = join(PATH_TO_RESULT_DIR, 'dict')
BYTE = 1024
SPLIT = '\t'
