import sys,os
from load_datn.models import create_database_structure

sys.path.append(os.getcwd())


if __name__ == '__main__':
    globals()[sys.argv[1]]()

# You can now call your function by running
# python myscript.py myfunction