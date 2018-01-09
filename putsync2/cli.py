from .core.offline import ConfiguredSchedulePool

# OfflineScanner().run()
# OfflineProcessor().run()

pool = ConfiguredSchedulePool()
pool.start()

while True:
    import time
    time.sleep(10)
