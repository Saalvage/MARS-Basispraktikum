#!/usr/bin/python
from cagd.vec import vec2


# solves the system of linear equations Ax = res
# where A is a tridiagonal matrix with diag2 representing the main diagonal
# diag1 and diag3 represent the lower and upper diagonal respectively
# all four parameters are vectors of size n
# the first element of diag1 and the last element of diag3 are ignored
# therefore diag1[i], diag2[i] and diag3[i] are located on the same row of A
def solve_tridiagonal_equation(diag1, diag2, diag3, res):
    assert (len(diag1) == len(diag2) == len(diag3) == len(res))

    beta = [diag2[0]]
    v = [0]

    for i in range(1, len(diag2)):
        v_i = diag3[i - 1] / beta[i - 1]
        v.append(v_i)
        beta.append(diag2[i] - diag1[i] * v_i)

    y = [res[0] * (1.0 / beta[0])]
    for i in range(1, len(res)):
        y.append((res[i] - diag1[i] * y[i - 1]) * (1.0 / beta[i]))

    solution = [None for _ in range(len(res))]
    solution[-1] = y[-1]
    for i in range(len(res) - 2, -1, -1):
        solution[i] = y[i] - v[i + 1] * solution[i + 1]

    return solution


# solves the system of linear equations Ax = res
# where A is an almost tridiagonal matrix with diag2 representing the main diagonal
# diag1 and diag3 represent the lower and upper diagonal respectively
# all four parameters are vectors of size n
# the first element of diag1 and the last element of diag3 represent the top right and bottom left elements of A
# diag1[i], diag2[i] and diag3[i] are located on the same row of A
def solve_almost_tridiagonal_equation(diag1, diag2, diag3, res):
    assert (len(diag1) == len(diag2) == len(diag3) == len(res))

    a = [None] + diag1
    b = [None] + diag2
    c = [None] + diag3
    d = [None] + res

    n = len(diag1)
    v = [0]
    y = [vec2(0, 0)]
    s = [1]

    for k in range(1, n):
        z = 1 / (b[k] + (a[k] * v[k - 1]))
        v.append(-z * c[k])
        y.append(z * (d[k] - a[k] * y[k - 1]))
        s.append(-a[k] * s[k - 1] * z)

    t = [None] * n + [1]
    w = [None] * n + [vec2(0, 0)]

    for k in range(n - 1, 0, -1):
        t[k] = v[k] * t[k + 1] + s[k]
        w[k] = v[k] * w[k + 1] + y[k]

    x = [None] * (n + 1)
    x[n] = (d[n] - c[n] * w[1] - a[n] * w[n - 1]) * (1 / (c[n] * t[1] + a[n] * t[n - 1] + b[n]))

    for k in range(n - 1, 0, -1):
        x[k] = t[k] * x[n] + w[k]

    return x[1:]
