# -*- coding:utf-8 -*-

# 1 we don't need to initial the instance using explicity 'self' in '__init__' method. such as:
class A:
    def __init__(*args, **kwargs):
        self, *args = args
        print(self)
        print(args)
        print(kwargs)

a = A(1, b=1)
""" that's work.
<__main__.A object at 0x011EDC30>
[1]
{'b': 1}
"""