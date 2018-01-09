def f(x, n):
    if n == 0:
        return 1
    elif n == 1:
        return x
    else:
        c = f(x, n // 2)
        if n % 2 == 0:
            return c * c
        else:
            return c * c * x

x, n = int(input()), int(input())
print(f(x, n))