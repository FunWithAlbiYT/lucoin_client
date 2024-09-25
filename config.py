from multiprocessing import cpu_count

CONFIG = {}

CONFIG['url'] = "network.lucoin.pro"
CONFIG['port'] = 3001

CONFIG['key'] = "tsZLphujK1TcynOAiXAmpuv1nPaERSkfcylCF3L1ws3TL56cf2lRRfrNpidm6AOR"
CONFIG['wallet'] = "If1u8cxjXgfHWbDkpDuKsQogMmjvVkWEOCS4KpNWN4"
CONFIG['fee'] = 1.0e-9 # %
CONFIG['socket_timeout'] = 3000 # ms

# miner
CONFIG["dedicated_mode"] = True # set this to false if you don't want your pc to lag while mining,
                            # set to true if you are afk mining.
CONFIG["debug_mode"] = False
