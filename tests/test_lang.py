def multi_return():
    return_tuple = ('张三', 12)
    return return_tuple
def multi_return2():
    return '张三', 12
print(multi_return())
result = multi_return()
print(result[0])
print('multi_return2返回值是=,类型是=', result, type(result))