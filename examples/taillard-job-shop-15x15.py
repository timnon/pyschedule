#! /usr/bin/python
import pyschedule
import math

# Taillards 15x15 job-shop instance downloaded from
# http://mistic.heig-vd.ch/taillard/problemes.dir/ordonnancement.dir/jobshop.dir/tai15_15.txt
# columns = jobs, rows = machines
proc = '\
94 66 10 53 26 15 65 82 10 27 93 92 96 70 83\n\
74 31 88 51 57 78  8  7 91 79 18 51 18 99 33\n\
 4 82 40 86 50 54 21  6 54 68 82 20 39 35 68\n\
73 23 30 30 53 94 58 93 32 91 30 56 27 92  9\n\
78 23 21 60 36 29 95 99 79 76 93 42 52 42 96\n\
29 61 88 70 16 31 65 83 78 26 50 87 62 14 30\n\
18 75 20  4 91 68 19 54 85 73 43 24 37 87 66\n\
32 52  9 49 61 35 99 62  6 62  7 80  3 57  7\n\
85 30 96 91 13 87 82 83 78 56 85  8 66 88 15\n\
 5 59 30 60 41 17 66 89 78 88 69 45 82  6 13\n\
90 27  1  8 91 80 89 49 32 28 90 93  6 35 73\n\
47 43 75  8 51  3 84 34 28 60 69 45 67 58 87\n\
65 62 97 20 31 33 33 77 50 80 48 90 75 96 44\n\
28 21 51 75 17 89 59 56 63 18 17 30 16  7 35\n\
57 16 42 34 37 26 68 73  5  8 12 87 83 20 97'

mach = '\
 7 13  5  8  4  3 11 12  9 15 10 14  6  1  2\n\
 5  6  8 15 14  9 12 10  7 11  1  4 13  2  3\n\
 2  9 10 13  7 12 14  6  1  3  8 11  5  4 15\n\
 6  3 10  7 11  1 14  5  8 15 12  9 13  2  4\n\
 8  9  7 11  5 10  3 15 13  6  2 14 12  1  4\n\
 6  4 13 14 12  5 15  8  3  2 11  1 10  7  9\n\
13  4  8  9 15  7  2 12  5  6  3 11  1 14 10\n\
12  6  1  8 13 14 15  2  3  9  5  4 10  7 11\n\
11 12  7 15  1  2  3  6 13  5  9  8 10 14  4\n\
 7 12 10  3  9  1 14  4 11  8  2 13 15  5  6\n\
 5  8 14  1  6 13  7  9 15 11  4  2 12 10  3\n\
 3 15  1 13  7 11  8  6  9 10 14  2  4 12  5\n\
 6  9 11  3  4  7 10  1 14  5  2 12 13  8 15\n\
 9 15  5 14  6  7 10  2 13  8 12 11  4  3  1\n\
11  9 13  7  5  2 14 15 12  1  8  4  3 10  6'

proc_table = [[int(x) for x in row.replace('  ', ' ').strip().split(' ')]
              for row in proc.split('\n')]
proc_table = [[int(math.ceil(int(x) / 10.0)) for x in row.replace('  ',
                                                                  ' ').strip().split(' ')] for row in proc.split('\n')]
mach_table = [[int(x) for x in row.replace('  ', ' ').strip().split(' ')]
              for row in mach.split('\n')]
n = 6  # len(proc_table)

S = pyschedule.Scenario('Taillards_Job_Shop_15x15')
T = {(i, j): S.Task('T_%i_%i' % (i, j), length=proc_table[
    i][j]) for i in range(n) for j in range(n)}
R = {j: S.Resource('R_%i' % j) for j in range(n)}

S += [T[i, j] < T[i, j + 1] for i in range(n) for j in range(n - 1)]
for i in range(n):
    for j in range(n):
        T[i, j] += R[mach_table[i][j] % n]

S.use_makespan_objective()
if pyschedule.solvers.mip.solve_bigm(S, time_limit=120, msg=1):
    pyschedule.plotters.matplotlib.plot(
        S, resource_height=100.0, hide_tasks=[S._tasks['MakeSpan']])
else:
    print('no solution found')
