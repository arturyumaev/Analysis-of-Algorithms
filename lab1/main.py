import numpy as np
import pandas as pd
import string
import random
import time
import sys
from matplotlib import pyplot as plt

def levenshtein_rec(s1, s2):
    i, j = len(s1), len(s2)

    if min(i, j) == 0:
        return max(i, j)
    return min(levenshtein_rec(s1[0:i], s2[0:j - 1]) + 1,
               levenshtein_rec(s1[0:i - 1], s2[0:j]) + 1,
               levenshtein_rec(s1[0:i - 1], s2[0:j - 1]) + (0 if s1[i - 1] == s2[j - 1] else 1))

def levenshtein_matrix(s1, s2, return_matrix=False):
    matrix = alloc_matrix(s1, s2)

    # 1. Simple cases
    for i in range(matrix.shape[0]): # Fill the first column
        matrix[i][0] = i
    for i in range(matrix.shape[1]): # Fill the first row
        matrix[0][i] = i

    # 2. i > 0, j > 0
    for i in range(1, matrix.shape[0]):
        for j in range(1, matrix.shape[1]):
            x = matrix[i - 1][j - 1]
            y = matrix[i - 1][j]
            z = matrix[i][j - 1]
            matrix[i][j] = min(y + 1, z + 1, x + (0 if s1[i - 1] == s2[j - 1] else 1))

    distance = matrix[matrix.shape[0] - 1][matrix.shape[1] - 1]
    
    if return_matrix:
        return matrix, distance
    else:
        return distance


def domerau_levenshtein_matrix(s1, s2, return_matrix=False):
    matrix = np.zeros((len(s1) + 2, len(s2) + 2)) # column is s1

    # 1. Simple cases
    for i in range(1, matrix.shape[0] - 1):  # Fill the first column
        matrix[i + 1][1] = i
    for i in range(1, matrix.shape[1] - 1):  # Fill the first row
        matrix[1][i + 1] = i

    for i in range(2, matrix.shape[0]):
        for j in range(2, matrix.shape[1]):
            y = matrix[i - 1][j] + 1
            z = matrix[i][j - 1] + 1
            x = matrix[i - 1][j - 1] + (0 if s1[i - 2] == s2[j - 2] else 1)
            q = matrix[i - 2][j - 2] + (1 if s1[i - 2] == s2[j - 3] and s2[j - 2] == s1[i - 3] else np.inf)
            matrix[i][j] = min(y, z, x, q)

    distance = matrix[matrix.shape[0] - 1][matrix.shape[1] - 1]

    if return_matrix:
        return matrix, distance
    else:
        return distance


def domerau_levenshtein_rec(s1, s2):
    i = len(s1)
    j = len(s2)

    if min(i, j) == 0:
        return max(i, j)
    elif (i > 1 and j > 1 and s1[i - 1] == s2[j - 2] and s1[i - 2] == s2[j - 1]):
        return min(
            domerau_levenshtein_rec(s1[:i - 1], s2[:j]) + 1,
            domerau_levenshtein_rec(s1[:i], s2[:j - 1]) + 1,
            domerau_levenshtein_rec(s1[:i - 2], s2[:j - 2]) + 1,
            domerau_levenshtein_rec(s1[:i - 1], s2[:j - 1]) + (0 if s1[i - 1] == s2[j - 1] else 1),
        )
    else:
        return min(
            domerau_levenshtein_rec(s1[:i - 1], s2[:j]) + 1,
            domerau_levenshtein_rec(s1[:i], s2[:j - 1]) + 1,
            domerau_levenshtein_rec(s1[:i - 1], s2[:j - 1]) + (0 if s1[i - 1] == s2[j - 1] else 1),
        )


def alloc_matrix(s1, s2):
    matrix_shape = (len(s1) + 1, len(s2) + 1)
    return np.zeros(matrix_shape)


def print_result(title, s1, s2, distance, matrix=None, dom=False):
    print("Distance between \"{0}\" and \"{1}\" according to {2} is {3}".format(s1, s2, title, int(distance)))
    if matrix is not None:
        spaces = ("  " if dom else " ")
        df = pd.DataFrame(matrix, columns=list(spaces + s2))
        df.index = list(spaces + s1)
        print(df)
    print()


def test_matrix():
    # Sum of the kernel and user-space CPU time will be measured

    lev_measure = []
    dom_lev_measure = []
    times = 1
    n = 10

    for i in range(1, 11):
        # Generate 2 random string
        s1 = "".join(random.choices(string.ascii_lowercase, k=i))
        s2 = "".join(random.choices(string.ascii_lowercase, k=i))

        # Levenstain time measurement
        time_start = time.process_time()
        for i in range(times):
            _ = levenshtein_matrix(s1, s2)
        time_end = (time.process_time() - time_start) / times
        lev_measure.append(time_end)
        print(time_end)

        # Domerau-Levenstain measurement
        time_start = time.process_time()
        for i in range(times):
            _ = levenshtein_rec(s1, s2)
        time_end = (time.process_time() - time_start) / times
        dom_lev_measure.append(time_end)
        print(time_end)
        print()

    print(lev_measure)
    print(dom_lev_measure)

    plt.title("Measurement of the operating time of the Levenshtein and Damerau-Levenshtein")
    plt.grid(True)
    plt.xlabel("Words length")
    plt.ylabel("Seconds")
    x = list(range(n))
    plt.plot(x, lev_measure, "ro--")
    plt.plot(x, dom_lev_measure, "go--")
    plt.legend([levenshtein_matrix.__name__, levenshtein_rec.__name__])
    plt.show()

def main():
    # Test
    s1, s2 = "qwert", "qewtr"
    
    lm, lm_d = levenshtein_matrix(s1, s2, return_matrix=True)
    print_result("Levenshtein Matrix", s1, s2, lm_d, matrix=lm)

    lrd = levenshtein_rec(s1, s2) # Levenstein recursion distance
    print_result("Levenstain Recursive Method", s1, s2, lrd)

    dlm, dlm_d = domerau_levenshtein_matrix(s1, s2, return_matrix=True)
    print_result("Domerau-Levenshtein Matrix", s1, s2, dlm_d, matrix=dlm, dom=True)

    dlrd = domerau_levenshtein_rec(s1, s2)
    print_result("Domerau-Levenstain Recursive Method", s1, s2, dlrd)


if __name__ == "__main__":
    main()
    #test_matrix()
