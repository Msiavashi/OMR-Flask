import os


ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) # This is Project Root
print ROOT_DIR
STATIC_DIR = os.path.join(ROOT_DIR, "project/static/")
print STATIC_DIR