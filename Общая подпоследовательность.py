def f(l1, l2):

    m, n = len(l1), len(l2)
    S = [[0] * (n + 1) for i in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if l1[i - 1] == l2[j - 1]:
                S[i][j] = S[i - 1][j - 1] + 1
            elif S[i - 1][j] >= S[i][j - 1]:
                S[i][j] = S[i - 1][j]
            else:
                S[i][j] = S[i][j - 1]
    k = 0
    for i in S:
        for j in i:
            if j > k: k = j
    return k

l1 = list(map(int, input().split()))
l2 = list(map(int, input().split()))
print(f(l1, l2))