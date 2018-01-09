def f1(l, N):
    c, b = 0, [False] * (N + 1)
    for i in l:
        if b[i] == False:
            b[i] = True
            c += 1
    return c

def f2(l):
    return len(set(l))

l = list(map(int, input().split()))
print(f1(l, 100))
print(f2(l))