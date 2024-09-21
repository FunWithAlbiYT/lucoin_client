from multiprocessing import cpu_count

CONFIG = {}

CONFIG['url'] = "network.lucoin.pro"
CONFIG['port'] = 3001

CONFIG['key'] = ""
CONFIG['wallet'] = ""
CONFIG['fee'] = 0.05 # %
CONFIG['socket_timeout'] = 3000 # ms

CONFIG["num_workers"] = cpu_count() # cores
CONFIG["debug_mode"] = False
