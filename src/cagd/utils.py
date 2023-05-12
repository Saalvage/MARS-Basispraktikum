#!/usr/bin/python
from cagd.vec import vec2

#solves the system of linear equations Ax = res
#where A is a tridiagonal matrix with diag2 representing the main diagonal
#diag1 and diag3 represent the lower and upper diagonal respectively
#all four parameters are vectors of size n
#the first element of diag1 and the last element of diag3 are ignored
#therefore diag1[i], diag2[i] and diag3[i] are located on the same row of A
def solve_tridiagonal_equation(diag1, diag2, diag3, res):
    assert(len(diag1) == len(diag2) == len(diag3) == len(res))
    
    beta = [diag2[0]]
    v = [0]
    
    for i in range(1, len(diag2)):
        v_i = diag3[i-1] / beta[i-1]
        v.append(v_i)
        beta.append(diag2[i] - diag1[i] * v_i)
    
    y = [res[0] * (1.0/beta[0])]
    for i in range(1, len(res)):
        y.append((res[i] - diag1[i] * y[i-1]) * (1.0/beta[i]) )
    
    solution = [None for _ in range(len(res))]
    solution[-1] = y[-1] 
    for i in range(len(res) - 2, -1, -1):
        solution[i] = y[i] - v[i+1] * solution[i + 1]
        
    return solution
     

#solves the system of linear equations Ax = res
#where A is an almost tridiagonal matrix with diag2 representing the main diagonal
#diag1 and diag3 represent the lower and upper diagonal respectively
#all four parameters are vectors of size n
#the first element of diag1 and the last element of diag3 represent the top right and bottom left elements of A
#diag1[i], diag2[i] and diag3[i] are located on the same row of A
def solve_almost_tridiagonal_equation(diag1, diag2, diag3, res):
    assert(len(diag1) == len(diag2) == len(diag3) == len(res))
    solution = None
    return solution

