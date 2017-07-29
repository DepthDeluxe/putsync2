import threading

lockeddecoratorlock = threading.RLock()
lockmap = {}

def locked(func):
    def __safe_func(*args, **kwargs):
        funcname = f'{func.__module__}:{func.__name__}'

        # lock for checking if lock already exists
        lockeddecoratorlock.acquire()
        if funcname not in lockmap:
            lockmap[funcname] = threading.RLock()
        lockeddecoratorlock.release()
       
        lockmap[funcname].acquire()
        try:
            func(*args, **kwargs)
        finally:
            lockmap[funcname].release()

    return __safe_func
