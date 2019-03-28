# -*- coding:utf-8 -*-

def wapper(func):
    def f(*args, **kwargs):
        print(func.__name__ + 'called')
        'do something'
        func(*args, **kwargs)
    return f
def test1():
  print('i  am test1')

test1 = wapper(test1)
#print(test1)
"""
<function wapper.<locals>.f at 0x037CFDF8>
"""

# 等价于

@wapper
def test2():
    print('i am test2')
#test2()
"""
test2called
i am test2
"""

# 被称为一个横切面(Aspect)，这种编程方式被称为面向切面的编程(Aspect-Oriented Programming)。

# --------------------------------------------------------------------------------------
# 带参数的装饰器

def wrapper(param):
    def decorator(func):
        def f(*args, **kwargs):
            print(func.__name__ + 'called with param {}'.format(param))
            'do something with param'
            return func(*args, **kwargs)
        return f
    return decorator

@wrapper('i am param')
def test3(*args, **kwargs):
    print('i am test3')
#test3()

"""
test3called with param i am param
i am test3
"""

# --------------------------------------------------------------------------
# 类装饰器
# object.__call__(self[, args...])模拟可调用对象

class Wapper(object):
    def __init__(self, func):
        self._func = func

    def __call__(self):
        print(self.__getattribute__('__call__'))
        self._func() # 执行

@Wapper
def test4():
    print('i am test4')

#test4()
"""
<bound method Wapper.__call__ of <__main__.Wapper object at 0x0321CA90>>
i am test4
"""

# ----------------------------------------------------------------------------------
# 普通函数使用装饰器其函数元信息丢失，例如
def dec(func):
    def f(*args, **kwargs):
        print(f.__name__)
        return func(*args, **kwargs)
    return f

@dec
def test5():
    print("test5's name: {}".format(test5.__name__))

test5()
"""
f
test5's name: f
"""


# ----------------functools.wraps---------------------------

# (1) partial (From https://docs.python.org/3/library/functools.html#functools.partial)
# functions.partial(func, *args, **keywords)
# Roughly equivalent to
def partial(func, *args, **keywords):
    def newfunc(*fargs, **fkeywords):
        newkeywords = keywords.copy()
        newkeywords.update(fkeywords)
        return func(*args, *fargs, **newkeywords)
    
    newfunc.func = func
    newfunc.args = args
    newfunc.keywords = keywords
    return newfunc

# For Example
from functools import partial
basetwo = partial(int, base=2)
# print(basetwo('11100'))
# print(basetwo.func)
# print(basetwo.args)
# print(basetwo.keywords)
"""result
28
<class 'int'>
()
{'base': 2}
"""
# ==================================================================================================
""" Source Code in CPYTHON functools.py"""
class partial:

    __slot__ = "func", "args", "keywords", "__dict__", "__weakref__"

    def __new__(*args, **keywords):
        if not args:
            raise TypeError("descriptor '__new__' of partial needs an argument")
        if len(args) < 2:
            raise TypeError("type 'partial' takes at least one argument") # 至少是一个函数，外加一个特定参数
        cls, func, *args = args # unpack
        if not callable(func):
            raise TypeError("the first argument must be callable") # 检查函数是否可调用
        
        args = tuple(args)

        if hasattr(func, "func"):
            args = func.args + args # 将func的args添加构成新的args
            tmpkkw = func.keywords.copy()
            tmpkkw.update(keywords)
            keywords = tmpkkw # 更新构成新keywords，若keywords存在，则替换其，通常为一个默认值如  (int, base=2)
            del tmpkkw
            func = func.func

        self = super(partial, cls).__new__(cls) # 父类构建实例

        self.func = func # 实例属性设置 较原函数多余添加的属性
        self.args = args
        self.keywords = keywords
        return self
    
    def __call__(*args, **keywords): # 不必写self
        if not args:
             raise TypeError('...')
        self, *args = args # self 在此
        newkeywords = self.keywords.copy()
        newkeywords.update(keywords)
        return self.func(*self.args, *args, **newkeywords)


# (2) wraps
WRAPPER_ASSIGNMENTS = ('__module__', '__name__', '__qualname__', '__doc__',
                       '__annotations__')
WRAPPER_UPDATES = ('__dict__',)

def wraps(wrapped,
          assigned = WRAPPER_ASSIGNMENTS,
          updated = WRAPPER_UPDATES):
    """Decorator factory to apply update_wrapper() to a wrapper function

       Returns a decorator that invokes update_wrapper() with the decorated
       function as the wrapper argument and the arguments to wraps() as the
       remaining arguments. Default arguments are as for update_wrapper().
       This is a convenience function to simplify applying partial() to
       update_wrapper().
    """
    return partial(update_wrapper, wrapped=wrapped,
                   assigned=assigned, updated=updated)

def update_wrapper(wrapper,
                   wrapped,
                   assigned = WRAPPER_ASSIGNMENTS,
                   updated = WRAPPER_UPDATES):
    """
    Update a wrapper function to look like the wrapped function

    """

    for attr in assigned: # 为wrapper设置wrapped的一些属性值 
        try:
            value = getattr(wrapped, attr)
        except AttributeError:
            pass
        else:
            setattr(wapper, attr, value)
    for attr in updated:
        getattr(wrapper, attr).update(getattr(wrapped, attr, {}))
    
    wapper.__wrapped__ = wrapped
    return wapper

# ---------------------------------------------------------------------------
""" 举个栗子

例如
>>> def my_decorator(f):
...     @wraps(f)
...     def wrapper(*args, **kwds):
...         print('Calling decorated function')
...         return f(*args, **kwds)
...     return wrapper

[1]
首先调用wraps(f)。
其中参数 wrapped = f     assigned = WRAPPER_ASSIGNMENTS       updated = WRAPPER_UPDATES

返回 partial(update_wrapper, wrapped=f, 'assigned':WRAPPER_ASSIGNMENTS, 'updated':WRAPPER_UPDATES)

[2]
partial 初始化实例，借用 func 即此时的 update_wrapper 属性更新 args keywords. 

示例中得到
self = functools.partial(...)
self.func = update_wrapper
self.args = []
self.keywords={'wrapped':f, 'assigned':WRAPPER_ASSIGNMENTS, 'updated':WRAPPER_UPDATES}

返回更新参数的partial实例。

[3] 
进入函数wapper的装饰

wrapper = wraps(f) (wapper)
即调用 partial 的 __call__()方法。
传入参数，即示例函数的 wapper。
调用 self.func(*self.args, *args, **self.keywords)。即 
update_wrapper(wapper, f, WRAPPER_ASSIGNMENTS, WRAPPER_UPDATES)
对应参数为 self.args = [] ; *args=wapper ; **keywords=f, WRAPPER_ASSIGNMENTS, WRAPPER_UPDATES

此时 update_wrapper 将已包装函数 f 的部分属性值复制到 未包装函数 wapper , 并返回。 同时解决了部分信息丢失的问题。

"""

"""
partial大致功能。
partial类提供 对输入函数，参数的临时场所。用来将更新的参数值传入函数。并将 func、args、keywords实例属性存储函数对象、传入的args,keywords。
类定义 __call__方法 提供对已更新参数的函数调用。
从而，从外界来看，实现偏函数。

"""