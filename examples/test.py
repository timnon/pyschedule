from pyschedule import *

S = Scenario('my scenario')

I1 = S.Task('I1')
I2 = S.Task('I2')
I3 = S.Task('I3')
I4 = S.Task('I4')
MakeSpan = S.Task('MakeSpan') #TODO: length < 1 does not work with GLPK???


R1 = S.Resource('R1')
R2 = S.Resource('R2')
'''
R3 = S.Resource('R3')
'''

#S += I2 << I1 << I3
#S += 1 < I3 #TODO: creates bug


S += MakeSpan
S += MakeSpan > { I1, I2, I3, I4 }


#S += I1,I2,I3,I4#I1 << I2, I2 < I3#, I3, I4
#S += I1 > 4

I1 += R1


I2 += R1
I3 += R1
I4 += R1


#S += I1 < I2
#S += I1 <> I2
#R1 += I1,I2,I1

R1 += I2 + 3 << I1,  I1 + 4 << I2
R1 += I3 + 3 << I1,  I1 + 4 << I3
R1 += I3 + 3 << I2,  I2 + 4 << I3

#S += I1 <> I2
#I3 += R1
#S += I3
#I1 += R1 & R2
#I2 += R2 & R1


print S.__repr__()

solvers.pulp(S,kind='GLPK',msg=0,lp_filename='tmp.lp',return_pulp_prob=False)

#print prob
print S.solution()

if S != 0 :
	plotters.gantt_matplotlib(S)#,img_filename='tmp.png')
else :
	print('no solution')




