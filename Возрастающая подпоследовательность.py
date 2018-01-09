import sys

def bin_search(l, x):
    i, j = -1, len(l)
    while i < j - 1:
        m = int((i + j) / 2)
        if l[m] <= x:
            i = m
        else:
            j = m
    return j

def f(l):
    try:
        for i in range(len(l)):
            l[i] = int(l[i])
    except ValueError:
        print('Wrong Input')
        return
    else:
        n = len(l)
        d = [sys.maxsize] * (n + 1)
        d[0] = -sys.maxsize - 1
        for i in range(n):
            j = bin_search(d, l[i])
            if d[j - 1] < l[i] and l[i] < d[j]:
                d[j] = l[i]
        #return d
        for i in range(n, 0, -1):
            if d[i] != sys.maxsize:
                return i

l = input().split()
print(f(l))