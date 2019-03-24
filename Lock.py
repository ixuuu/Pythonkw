# coding：utf-8
"""
Python 线程锁相关

"""
import time
import threading
# Part1 标准库 threading
# -------------多线程-----------------------

def funcA():
    for  _ in range(1000000):
        pass
def funcB():
    for _ in range(1000000):
        pass

# 多线程创建方法 1: 创建threading.Thread对象，args传递target参数
t1 = threading.Thread(group=None, target=funcA, name='funcA-Thread', args=(), kwargs={}, daemon=None)
t2 = threading.Thread(group=None, target=funcB, name='funcB-Thread', args=(), kwargs={}, daemon=None)

s_time = time.time_ns()
t1.start() # ibvoke object’s run()
t2.start()
print('t1 is alive? %s' % t1.is_alive())
#t1.join() # or not 
print('t1 is alive? %s' % t1.is_alive())

print('t2 is alive? %s' % t2.is_alive())
#t2.join()
print('t1 is alive? %s' % t1.is_alive())
print('t2 is alive? %s' % t2.is_alive())
e_time = time.time_ns()
print('consumed %d' % (e_time - s_time))
# other functions
print(t1.name)
print(t1.ident)
print(t1.daemon)

# 多线程创建方法2: 继承Thread类，重写run方法
class MyThread(threading.Thread):
    """
     only override the __init__() and run() methods of this class
    """
    def __init__(self):
        super(MyThread, self).__init__()
    
    def run(self):
        for _ in range(100000):
            pass

t3 = MyThread()
print('t3 is alive? %s' % t3.is_alive())
t3.start()
print('t3 is alive? %s' % t3.is_alive())

# when no thread
s_time = time.time_ns()
funcA()
funcB()
e_time = time.time_ns()
print('consumed %d' % (e_time - s_time))

# --------------Lock Objects-------------------------------
"""
原始锁是一种同步原语
class threading.Lock
acquire(blocking=True, timeout=-1)
release()
"""
lock = threading.Lock() # type: <class '_thread.lock'>

num = 0
def sum_n(i):
    #lock.acquire() # # add lock or not
    global num
    time.sleep(1)
    num += 1
    print(num)
    #lock.release() # # add lock or not

for i in range(8):
    t = threading.Thread(target=sum_n, args=(i,))
    t.start() # 结果确定但很慢 # 结果速度快但不确定

# --------------RLock Objects-------------------------------
def funcC():
    # 普通锁
    # 线程安全，但不可重入
    lock.acquire()
    # do somethine
    #return funcC() # 重入会导致死锁
    lock.release()
funcC()

# RLock 解决普通互斥锁不可重入的问题
"""
class threading.RLock
acquire(blocking=True, timeout=-1)
在不带参数的情况下调用：如果此线程已拥有锁，则将递归级别递增1，并立即返回。否则，如果另一个线程拥有该锁，则阻塞直到锁被解锁。
锁解锁后（不属于任何线程），然后获取所有权，将递归级别设置为1，然后返回
如果多个线程被阻塞等待锁解锁，则一次只能有一个线程获取锁的所有权。在这种情况下没有返回值。
release()
释放锁定，递减递归级别
If after the decrement it is zero, reset the lock to unlocked (not owned by any thread), and if any other threads are blocked waiting for the lock to become unlocked, allow exactly one of them to proceed. 
仅在调用线程拥有锁时调用此方法。
"""
rlock = threading.RLock()
def funcD():
    # 可重入
    rlock.acquire()
    print('rlock acquire by funcD')
    funcE() # Into funcE() will change the lockedby from Thread funcD to Thread funcE.
    rlock.release()
    print('rlock release by funcD')

def funcE():
    rlock.acquire()
    print('rlock acquire by funcE')
    rlock.release()
    print('rlock release by funcE')
funcD()


# RLock部分源码
import _thread
_allocate_lock = _thread.allocate_lock
get_ident = _thread.get_ident

class _RLock:
    def __init__(self):
        self._block = _allocate_lock()
        self._owner = None
        self._count = 0
    
    def acquire(self, blocking=True, timeout=-1):
        me = get_ident()
        if self._owner == me:
            self._count += 1 # 保证可重入，仅增加计数器
            return 1
        rc = self._block.acquire(blocking, timeout)
        if rc:
            self._owner = me
            self._count = 1
        return rc

    def release(self):
        if self._owner != get_ident():
            raise RuntimeError("cannot release un-acquired lock")
        self._count = count = self._count - 1 # 仅本线程递减
        if not count:
            self._owner = None
            self._block.release()  # 仅当计数器归零才真正释放
    
    # ---------为 Condition准备的函数---------------------
    def _acquire_restore(self, state):
        self._block.acquire()
        self._count, self._owner = state  # state作输入

    def _release_save(self):
        if self._count == 0:
            raise RuntimeError("cannot release un-acquire lock")
        count = self._count
        self._count = 0
        owner = self._owner
        self._owner = None
        self._block.release()
        return (count, owner) # 重置状态后返回状态tuple
    def _is_owned(self):
        return self._owner == get_ident()

# -------------Condition Objects----------------------
"""
class threading.Condition(lock=None)
如果给出了lock参数而不是None，则它必须是Lock或RLock对象，并且它被用作底层锁。否则，将创建一个新的RLock对象并将其用作基础锁。
acquire(*args)
获取底层锁。此方法在底层锁上调用相应的方法;返回值是该方法返回的任何值。
release()
释放底层锁。此方法在底层锁上调用相应的方法;没有返回值。
wait(timeout=None)
wait_for(predicate, timeout=None)
predicate应该是可调用的，结果将被解释为布尔值。
notify(n=1)
此方法最多唤醒等待条件变量的n个线程;如果没有线程在等待，那么这是一个无操作
notify_all()
"""
try:
    _CRLock = _thread.RLock
except AttributeError:
    _CRLock = None

_PyRLock = _RLock

def RLock(*args, **kwargs):
    """Factory function that returns a new reentrant lock.

    A reentrant lock must be released by the thread that acquired it. Once a
    thread has acquired a reentrant lock, the same thread may acquire it again
    without blocking; the thread must release it once for each time it has
    acquired it.

    """
    if _CRLock is None:
        return _PyRLock(*args, **kwargs)
    return _CRLock(*args, **kwargs)

# -----------以上提供RLock---------------------
try:
    from _collections import deque as _deque
except ImportError:
    from collections import deque as _deque
# ---------以上提供 deque----------------
from itertools import islice as _islice, count as _count


class Condition:
    def __init__(self, lock=None):
        if lock is None:
            lock = RLock() # 默认RLock
        self._lock = lock
        # Export the lock's acquire() and release() methods
        self.acquire = lock.acquire
        self.release = lock.release # 本地化
        # -----------------
        # 若提供RLock的函数，本地化
        try:
            self._release_save = lock._release_save
        except AttributeError:
            pass
        try:
            self._acquire_restore = lock._acquire_restore
        except AttributeError:
            pass
        try:
            self._is_owned = lock._is_owned
        except AttributeError:
            pass
        # ----------------
        self._waiters = _deque()

    def wait(self, timeout=None):
        if not self._is_owned():
            raise RuntimeError("cannot wait on un-acquired lock")
        
        waiter = _allocate_lock() # 每次调用wait() 产生新的一把锁 _thread.allocate_lock
        waiter.acquire() # 加锁
        self._waiters.append(waiter) # 锁入队列
        saved_state = self._release_save() # 保存状态量，并释放底层锁，供其他线程获得执行权
        gotit = False
        try:    # restore state no matter what (e.g., KeyboardInterrupt)
            if timeout is None:
                waiter.acquire() # 其他notify()会释放waiter，否则阻塞
                gotit = True
            else:
                if timeout > 0:
                    gotit = waiter.acquire(True, timeout)
                else:
                    gotit = waiter.acquire(False)
            return gotit
        finally:
            self._acquire_restore(saved_state) # 获取底层锁，否则阻塞
            if not gotit:
                try:
                    self._waiters.remove(waiter) # wait() notify() 均尝试把此waiter删除，总有一个会成功
                except ValueError:
                    pass
    
    def notify(self, n=1):
        if not self._is_owned():
            raise RuntimeError("cannot notify on un-acquired lock")
        all_waiters = self._waiters
        waiters_to_notify = _deque(_islice(all_waiters, n)) # n=len(self._waiters) 为notify_all
        if not waiters_to_notify:
            return
        for waiter in waiters_to_notify: # islice()返回可迭代对象
            waiter.release()
            try:
                all_waiters.remove(waiter)
            except ValueError:
                pass
        # notifyAll = notify_all # 兼容

cond = threading.Condition()
def funcF():
    cond.acquire() # 底层锁，执行权

    cond.wait() # 等待 呼叫 1
    print("funcF 应答 1")
    cond.notify() # 通知 收到应答 1

    cond.wait() # 等待 呼叫 2
    print("funcF 应答 2")
    cond.notify() # 通知 收到应答 2

    cond.wait()
    print('funcF 应答 3')
    cond.notify()

    cond.release()

def funcG():
    cond.acquire()

    print('funcG 呼叫 1')
    cond.notify() # 通知应答 1
    cond.wait() # 等待 收到应答 确认 1

    print('funcG 呼叫 2')
    cond.notify() # 通知应答 2
    cond.wait() # 等待 收到应答 确认 2

    print('funcG 呼叫 3')
    cond.notify()
    cond.wait()

    cond.release()

t4 = threading.Thread(target=funcF)
t5 = threading.Thread(target=funcG)
t4.start()
t5.start()
#t4.start() # 执行顺序需 t4 在 t5 之前
# --------------
# funcG 呼叫 1
# funcF 应答 1
# funcG 呼叫 2
# funcF 应答 2
# funcG 呼叫 3
# funcF 应答 3
# --------------

# -------------Semaphore Objects-----------------
# 在linux系统中，二进制信号量（binary semaphore）又称互斥锁（Mutex）
"""
class threading.Semaphore(value=1)
acquire()
release

clas threading.BoundedSemaphore(value=1)
有界信号量检查以确保其当前值不超过其初始值。
"""
Lock = _allocate_lock
from time import monotonic as _time
# Semaphore 源码
class Semaphore:
    def __init__(self, value=1):
        if value < 0:
            raise ValueError('semaphore initial value must be >= 0')
        self._cond = threading.Condition(Lock())
        self._value = value # condition+value --> semaphore
    
    def acquire(self, blocking=True, timeout=None):
        # ...
        rc = False
        endtime = None
        with self._cond:
            while self._value == 0: # 信号量计数器为0，则wait()一定时间
                if not blocking:
                    break
                if timeout is not None:
                    if endtime is None:
                        endtime = _time() + timeout
                    else:
                        timeout = endtime - _time()
                        if timeout <= 0:
                            break
                self._cond.wait(timeout) # wait
            else: # 否则，计数器减一
                self._value -= 1
                rc = True
        return rc
    __enter__ = acquire # with

    def release(self):
        with self._cond:
            self._value += 1
            self._cond.notify() # notify

    def __exit__(self, t, v, tb): # t, v, tb ? ---> object.__exit__(self, exc_type, exc_value, traceback)
        self.release() # with

sem = threading.Semaphore(value=3)

def funcH(i):
    sem.acquire()
    t = time.asctime()
    print(t)
    time.sleep(6)
    sem.release()
    
# for i in range(10):
#     t_h = threading.Thread(target=funcH, args=(i,))
#     t_h.start()
"""
...39...
...39...
...39...
...45...
...45...
...45...
"""

# ---------Event Objects-------------------
"""
class threading.Event

is_set()
set()
clear()
wait(timeout=None)
"""
class Event:
    def __init__(self):
        self._cond = threading.Condition(Lock())
        self._flag = False
    # ...
    def set(self):
        with self._cond:
            self._flag = True
            self._cond.notify_all()

    def clear(self):
        with self._cond:
            self._flag = False

    def wait(self, timeout=None):
        with self._cond:
            signaled = self._flag
            if not signaled:
                signaled = self._cond.wait(timeout)
            return signaled


# ------------Timer Objects----------------------
"""
class threading.Timer(interval, function, args=None, kwargs=None)
cancel()

"""
from threading import Thread
from threading import Event

class Timer(Thread):
    def __init__(self, interval, function, args=None, kwargs=None):
        Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.finished = Event()

    def cancel(self):
        self.finished.set() # only work if the timer is still in its waiting stage

    def run(self):
        self.finished.wait(self.interval)
        if not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
        self.finished.set()

# ----------------------Barrior Objects--------------------------
"""
class threading.Barrier(parties, action=None, timeout=None)
为parties数量的线程创建一个barrier对象
wait(timeout=None)  所有线程都调用此函数时，它们都会同时释放。
返回值从1至parties-1。可指定一个线程作其他事情
i = barrier.wait()
if i == 0:
    # Only one thread needs to print this
    print("passed the barrier")

reset()
abort()
parties
n_waiting
broken

exception threading.BrokenBarrierError
RuntimeError 子类，reset or broken产生异常
"""
# Lock, RLock, Condition, Semaphore, and BoundedSemaphore 可以with语句简化

# source code
from threading import Condition
from threading import BrokenBarrierError
class Barrier:
    def __init__(self, parties, action=None, timeout=None):
        self._cond = Condition(Lock())
        self._action = action
        self._timeout = timeout
        self._parties = parties
        self._state = 0 # 0 filling, 1, draining, -1 resetting, -2 broken
        # filling, draining 使barrier循环; resetting同draining，但在结束时抛出异常; borken 均抛出异常
        self._count = 0

    def wait(self, timeout=None):
        if timeout is None:
            timeout = self._timeout
        with self._cond:
            self._enter()

            index = self._count
            self._count += 1
            try:
                if index + 1 == self._parties: # 到达parties数量，释放barrier
                    self._release()
                else:
                    self._wait(timeout) # 阻塞等待
                return index
            finally:
                self._count -= 1
                self._exit()
    
    def _enter(self):
        while self._state in (-1, 1): # draining or reseting
            self._cond.wait() # 一直阻塞
        if self._state < 0:
            raise BrokenBarrierError
        assert self._state == 0
    
    def _release(self):
        try:
            if self._action:
                self._action() # 释放后才运行函数
            
            self._state = 1 # 进入 draining 状态
            self._cond.notify_all()
        except:
            self._break()
            raise