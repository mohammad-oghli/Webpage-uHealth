from queue import Queue
from threading import local

# Shared Global Variables
q = Queue(maxsize=0)
thread_local = local()
h_links = []
uh_links = []