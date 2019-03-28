# -*-coding:utf-8 -*-

import concurrent.futures
"""
class concurrent.futures.Executor
submit(fn, *args, **kwargs)
map(func, *iterables, timeout=None, chunksize=1)
shutdown(wait=True)

class concurrent.futures.ThreadPoolExecutor(max_workers=None, thread_name_prefix=",initializer=None,initargs=())

class concurrent.futures.ProcessPoolExecutor(max_workers=None, mp_context=None, initializer=None, initargs=())

class concurrent.future.Future
cancel()
cancelled()
running()
done()
result(timeout=None)
exception(timeout=None)
add_done_callback(fn)
set_running_or_notify_cancel()
set_result(result)
set_exception(exception)
"""