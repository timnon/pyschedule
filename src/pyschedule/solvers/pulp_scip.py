import os
from time import clock
import re
import subprocess
import pulp
import pulp.solvers

class SCIP_CMD(pulp.solvers.LpSolver_CMD):
    def __init__(self, path = None, keepFiles = 0, mip = 1,
            msg = 0, options = [], time_limit = None, ratio_gap = None):
        pulp.solvers.LpSolver_CMD.__init__(self, path, keepFiles, mip, msg, options)
        self.time_limit = time_limit
        self.ratio_gap = ratio_gap

    """The SCIP LP solver"""
    def defaultPath(self):
        return self.executableExtension("scip")

    def available(self):
        """True if the solver is available"""
        return self.executable(self.path)

    def actualSolve(self, lp):
        """Solve a well formulated lp problem"""
        if not self.executable(self.path):
            raise pulp.PulpSolverError("PuLP: cannot execute "+self.path)
        if not self.keepFiles:
            pid = os.getpid()
            tmpLp = os.path.join(self.tmpDir, "%d-pulp.lp" % pid)
            tmpSol = os.path.join(self.tmpDir, "%d-pulp.sol" % pid)
        else:
            tmpLp = lp.name+"-pulp.lp"
            tmpSol = lp.name+"-pulp.sol"
        lp.writeLP(tmpLp, writeSOS = 0)
        #proc = ["scip", "-c", "read \"%s\"" % tmpLp, "-c", "set limits time 180", "-c", "optimize", "-c", "write solution \"%s\"" % tmpSol, "-c", "quit"]
        proc = ["scip", "-c", "read \"%s\"" % tmpLp]
        if self.time_limit is not None:
            proc += ["-c", "set limits time %f"%self.time_limit]
        if self.ratio_gap is not None:
            proc += ["-c", "set limits gap %f"%self.ratio_gap]
        proc += ["-c", "optimize", "-c", "write solution \"%s\"" % tmpSol, "-c", "quit"]
        proc.extend(self.options)

        self.solution_time = clock()
        if not self.msg:
            proc[0] = self.path
            pipe = open(os.devnull, 'w')
            rc = subprocess.call(proc, stdout = pipe,
                             stderr = pipe)
            if rc:
                raise pulp.PulpSolverError("PuLP: Error while trying to execute "+self.path)
        else:
            if os.name != 'nt':
                rc = os.spawnvp(os.P_WAIT, self.path, proc)
            else:
                rc = os.spawnv(os.P_WAIT, self.executable(self.path), proc)
            if rc == 127:
                raise pulp.PulpSolverError("PuLP: Error while trying to execute "+self.path)
        self.solution_time += clock()

        if not os.path.exists(tmpSol):
            raise pulp.PulpSolverError("PuLP: Error while executing "+self.path)
        lp.status, values = self.readsol(tmpSol)
        lp.assignVarsVals(values)
        if not self.keepFiles:
            try: os.remove(tmpLp)
            except: pass
            try: os.remove(tmpSol)
            except: pass
        return lp.status

    def readsol(self, filename):
        """Read a SCIP solution file"""
        with open(filename) as f:
            m = re.match(r"^solution status: (.*)", f.readline().strip())
            if not m:
                raise pulp.PulpSolverError("Unknown status returned by SCIP")
            statusString = m.group(1)
            scipStatus = {
                "unknown": pulp.LpStatusNotSolved,
                "user interrupt": pulp.LpStatusNotSolved,
                "node limit reached": pulp.LpStatusNotSolved,
                "total node limit reached": pulp.LpStatusNotSolved,
                "stall node limit reached": pulp.LpStatusNotSolved,
                "time limit reached": pulp.LpStatusOptimal,
                "memory limit reached": pulp.LpStatusNotSolved,
                "gap limit reached": pulp.LpStatusOptimal,
                "solution limit reached": pulp.LpStatusNotSolved,
                "solution improvement limit reached": pulp.LpStatusNotSolved,
                "optimal solution found": pulp.LpStatusOptimal,
                "infeasible": pulp.LpStatusInfeasible,
                "unbounded": pulp.LpStatusUnbounded,
                "infeasible or unbounded": pulp.LpStatusNotSolved,
                }
            if statusString not in scipStatus:
                raise pulp.PulpSolverError("Unknown status returned by SCIP")
            status = scipStatus[statusString]
            f.readline() # objective value:
            values = {}
            for line in f:
                name, val, _ = line.split()
                values[name] = float(val)
        return status, values

SCIP = SCIP_CMD
