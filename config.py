from multiprocessing import cpu_count

CONFIG = {}

CONFIG['url'] = "network.lucoin.pro"
CONFIG['port'] = 3001

CONFIG['key'] = ""
CONFIG['wallet'] = ""
CONFIG['fee'] = 0.05 # %
CONFIG['socket_timeout'] = 3000 # ms

# miner
CONFIG["dedicated_mode"] = True # set this to false if you don't want your pc to lag while mining,
                            # set to true if you are afk mining.
CONFIG["debug_mode"] = False
