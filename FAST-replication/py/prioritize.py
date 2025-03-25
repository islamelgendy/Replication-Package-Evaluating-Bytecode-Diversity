'''
This file is part of an ICSE'18 submission that is currently under review. 
For more information visit: https://github.com/icse18-FAST/FAST.
    
This is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as 
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this source.  If not, see <http://www.gnu.org/licenses/>.
'''

import math
import os
import pickle
import sys

import competitors
import fast
import metric


usage = """USAGE: python py/prioritize.py <dataset> <entity> <algorithm> <repetitions>
OPTIONS:
  <dataset>: test suite to prioritize.
    options: flex_v3, grep_v3, gzip_v1, make_v1, sed_v6, closure_v0, lang_v0, math_v0, chart_v0, time_v0
  <entity>: BB or WB (function, branch, line) prioritization.
    options: bbox, function, branch, line
  <algorithm>: algorithm used for prioritization.
    options: FAST-pw, FAST-one, FAST-log, FAST-sqrt, FAST-all, STR, I-TSD, ART-D, ART-F, GT, GA, GA-S
  <repetitions>: number of prioritization to compute.
    options: positive integer value, e.g. 50
NOTE:
  STR, I-TSD are BB prioritization only.
  ART-D, ART-F, GT, GA, GA-S are WB prioritization only."""


def bboxPrioritization(name, prog, v, ctype, k, n, r, b, repeats, selsize, testType = 'text'):
    javaFlag = True #if v == "v0" else False

    if testType == 'text':
        fin = "input/{}_{}/{}-{}.txt".format(prog, v, prog, ctype)
        ftsv = "{}-{}.tsv".format(name, ctype)
    else:
        fin = "input/{}_{}/{}-{}-{}.txt".format(prog, v, prog, ctype, testType)
        ftsv = "{}-{}-{}.tsv".format(name, ctype, testType)
    if javaFlag:
        fault_matrix = "input/{}_{}/fault_matrix.pickle".format(prog, v)
    else:
        fault_matrix = "input/{}_{}/fault_matrix_key_tc.pickle".format(prog, v)
    outpath = "output/{}_{}/".format(prog, v)
    ppath = outpath + "prioritized"

    if name == "FAST-" + selsize.__name__[:-1]:
        if (ftsv) not in set(os.listdir(outpath)):
            ptimes, stimes, apfds = [], [], []
            for run in range(repeats):
                print (" Run", run)
                if javaFlag:
                    stime, ptime, prioritization = fast.fast_(
                        fin, selsize, r=r, b=b, bbox=True, k=k, memory=False)
                else:
                    stime, ptime, prioritization = fast.fast_(
                        fin, selsize, r=r, b=b, bbox=True, k=k, memory=True)
                writePrioritization(ppath, name, ctype, run, prioritization)
                apfd = metric.apfd(prioritization, fault_matrix, javaFlag)
                apfds.append(apfd)
                stimes.append(stime)
                ptimes.append(ptime)
                print("  Progress: 100%  ")
                print ("  Running time:", stime + ptime)
                if javaFlag:
                    print ("  APFD:", sum(apfds[run]) / len(apfds[run]))
                else:
                    print ("  APFD:", apfd)
            rep = (name, stimes, ptimes, apfds)
            writeOutput(outpath, ctype, rep, javaFlag)
            print("")
        else:
            print (name, "already run.")

    elif name == "FAST-pw":
        if (ftsv) not in set(os.listdir(outpath)):
        # if ("{}-{}-bytecode.tsv".format(name, ctype)) not in set(os.listdir(outpath)):
            ptimes, stimes, apfds = [], [], []
            for run in range(repeats):
                print (" Run", run)
                if javaFlag:
                    stime, ptime, prioritization = fast.fast_pw(
                        fin, r, b, bbox=True, k=k, memory=False)
                else:
                    stime, ptime, prioritization = fast.fast_pw(
                        fin, r, b, bbox=True, k=k, memory=True)
                writePrioritization(ppath, name, ctype, run, prioritization)
                # continue
                # apfd = metric.apfd(prioritization, fault_matrix, javaFlag)
                total = stime + ptime
                apfds.append(str(total))
                stimes.append(stime)
                ptimes.append(ptime)
                print("  Progress: 100%  ")
                print ("  Running time:", stime + ptime)
                # if javaFlag:
                #     print ("  APFD:", sum(apfds[run]) / len(apfds[run]))
                # else:
                #     print ("  APFD:", apfd)
            rep = (name, stimes, ptimes, apfds)
            writeOutput(outpath, ctype, rep, javaFlag)
            print("")
        else:
            print (name, "already run.")

    elif name == "STR":
        if ("{}-{}.tsv".format(name, ctype)) not in set(os.listdir(outpath)):
            ptimes, stimes, apfds = [], [], []
            for run in range(repeats):
                print (" Run", run)
                stime, ptime, prioritization = competitors.str_(fin)
                writePrioritization(ppath, name, ctype, run, prioritization)
                apfd = metric.apfd(prioritization, fault_matrix, javaFlag)
                apfds.append(apfd)
                stimes.append(stime)
                ptimes.append(ptime)
                print("  Progress: 100%  ")
                print ("  Running time:", stime + ptime)
                if javaFlag:
                    print ("  APFD:", sum(apfds[run]) / len(apfds[run]))
                else:
                    print ("  APFD:", apfd)
            rep = (name, stimes, ptimes, apfds)
            writeOutput(outpath, ctype, rep, javaFlag)
            print("")
        else:
            print (name, "already run.")

    elif name == "I-TSD":
        if ("{}-{}.tsv".format(name, ctype)) not in set(os.listdir(outpath)):
            ptimes, stimes, apfds = [], [], []
            for run in range(repeats):
                print (" Run", run)
                stime, ptime, prioritization = competitors.i_tsd(fin)
                writePrioritization(ppath, name, ctype, run, prioritization)
                apfd = metric.apfd(prioritization, fault_matrix, javaFlag)
                apfds.append(apfd)
                stimes.append(stime)
                ptimes.append(ptime)
                print("  Progress: 100%  ")
                print ("  Running time:", stime + ptime)
                if javaFlag:
                    print ("  APFD:", sum(apfds[run]) / len(apfds[run]))
                else:
                    print ("  APFD:", apfd)
            rep = (name, stimes, ptimes, apfds)
            writeOutput(outpath, ctype, rep, javaFlag)
            print("")
        else:
            print (name, "already run.")

    else:
        print("Wrong input.")
        print(usage)
        exit()


def wboxPrioritization(name, prog, v, ctype, n, r, b, repeats, selsize):
    javaFlag = True if v == "v0" else False

    fin = "input/{}_{}/{}-{}.txt".format(prog, v, prog, ctype)
    if javaFlag:
        fault_matrix = "input/{}_{}/fault_matrix.pickle".format(prog, v)
    else:
        fault_matrix = "input/{}_{}/fault_matrix_key_tc.pickle".format(prog, v)

    outpath = "output/{}_{}/".format(prog, v)
    ppath = outpath + "prioritized/"

    if name == "GT":
        if ("{}-{}.tsv".format(name, ctype)) not in set(os.listdir(outpath)):
            ptimes, stimes, apfds = [], [], []
            for run in range(repeats):
                print (" Run", run)
                stime, ptime, prioritization = competitors.gt(fin)
                writePrioritization(ppath, name, ctype, run, prioritization)
                apfd = metric.apfd(prioritization, fault_matrix, javaFlag)
                apfds.append(apfd)
                stimes.append(stime)
                ptimes.append(ptime)
                print("  Progress: 100%  ")
                print ("  Running time:", stime + ptime)
                if javaFlag:
                    print ("  APFD:", sum(apfds[run]) / len(apfds[run]))
                else:
                    print ("  APFD:", apfd)
            rep = (name, stimes, ptimes, apfds)
            writeOutput(outpath, ctype, rep, javaFlag)
            print("")
        else:
            print (name, "already run.")

    elif name == "FAST-" + selsize.__name__[:-1]:
        if ("{}-{}.tsv".format(name, ctype)) not in set(os.listdir(outpath)):
            ptimes, stimes, apfds = [], [], []
            for run in range(repeats):
                print (" Run", run)
                if javaFlag:
                    stime, ptime, prioritization = fast.fast_(
                        fin, selsize, r=r, b=b, memory=False)
                else:
                    stime, ptime, prioritization = fast.fast_(
                        fin, selsize, r=r, b=b, memory=True)
                writePrioritization(ppath, name, ctype, run, prioritization)
                apfd = metric.apfd(prioritization, fault_matrix, javaFlag)
                apfds.append(apfd)
                stimes.append(stime)
                ptimes.append(ptime)
                print("  Progress: 100%  ")
                print ("  Running time:", stime + ptime)
                if javaFlag:
                    print ("  APFD:", sum(apfds[run]) / len(apfds[run]))
                else:
                    print ("  APFD:", apfd)
            rep = (name, stimes, ptimes, apfds)
            writeOutput(outpath, ctype, rep, javaFlag)
            print("")
        else:
            print (name, "already run.")

    elif name == "FAST-pw":
        if ("{}-{}.tsv".format(name, ctype)) not in set(os.listdir(outpath)):
            ptimes, stimes, apfds = [], [], []
            for run in range(repeats):
                print (" Run", run)
                if javaFlag:
                    stime, ptime, prioritization = fast.fast_pw(fin, r, b)
                else:
                    stime, ptime, prioritization = fast.fast_pw(
                        fin, r, b, memory=True)
                writePrioritization(ppath, name, ctype, run, prioritization, testType)
                apfd = metric.apfd(prioritization, fault_matrix, javaFlag)
                apfds.append(apfd)
                stimes.append(stime)
                ptimes.append(ptime)
                print("  Progress: 100%  ")
                print ("  Running time:", stime + ptime)
                if javaFlag:
                    print ("  APFD:", sum(apfds[run]) / len(apfds[run]))
                else:
                    print ("  APFD:", apfd)
            rep = (name, stimes, ptimes, apfds)
            writeOutput(outpath, ctype, rep, javaFlag)
            print("")
        else:
            print (name, "already run.")

    elif name == "GA":
        if ("{}-{}.tsv".format(name, ctype)) not in set(os.listdir(outpath)):
            ptimes, stimes, apfds = [], [], []
            for run in range(repeats):
                print (" Run", run)
                stime, ptime, prioritization = competitors.ga(fin)
                writePrioritization(ppath, name, ctype, run, prioritization)
                apfd = metric.apfd(prioritization, fault_matrix, javaFlag)
                apfds.append(apfd)
                stimes.append(stime)
                ptimes.append(ptime)
                print("  Progress: 100%  ")
                print ("  Running time:", stime + ptime)
                if javaFlag:
                    print ("  APFD:", sum(apfds[run]) / len(apfds[run]))
                else:
                    print ("  APFD:", apfd)
            rep = (name, stimes, ptimes, apfds)
            writeOutput(outpath, ctype, rep, javaFlag)
            print("")
        else:
            print (name, "already run.")

    elif name == "GA-S":
        if ("{}-{}.tsv".format(name, ctype)) not in set(os.listdir(outpath)):
            ptimes, stimes, apfds = [], [], []
            for run in range(repeats):
                print (" Run", run)
                stime, ptime, prioritization = competitors.ga_s(fin)
                writePrioritization(ppath, name, ctype, run, prioritization)
                apfd = metric.apfd(prioritization, fault_matrix, javaFlag)
                apfds.append(apfd)
                stimes.append(stime)
                ptimes.append(ptime)
                print("  Progress: 100%  ")
                print ("  Running time:", stime + ptime)
                if javaFlag:
                    print ("  APFD:", sum(apfds[run]) / len(apfds[run]))
                else:
                    print ("  APFD:", apfd)
            rep = (name, stimes, ptimes, apfds)
            writeOutput(outpath, ctype, rep, javaFlag)
            print("")
        else:
            print (name, "already run.")

    elif name == "ART-D":
        if ("{}-{}.tsv".format(name, ctype)) not in set(os.listdir(outpath)):
            ptimes, stimes, apfds = [], [], []
            for run in range(repeats):
                print (" Run", run)
                stime, ptime, prioritization = competitors.art_d(fin)
                writePrioritization(ppath, name, ctype, run, prioritization)
                apfd = metric.apfd(prioritization, fault_matrix, javaFlag)
                apfds.append(apfd)
                stimes.append(stime)
                ptimes.append(ptime)
                print("  Progress: 100%  ")
                print ("  Running time:", stime + ptime)
                if javaFlag:
                    print ("  APFD:", sum(apfds[run]) / len(apfds[run]))
                else:
                    print ("  APFD:", apfd)
            rep = (name, stimes, ptimes, apfds)
            writeOutput(outpath, ctype, rep, javaFlag)
            print("")
        else:
            print (name, "already run.")

    elif name == "ART-F":
        if ("{}-{}.tsv".format(name, ctype)) not in set(os.listdir(outpath)):
            ptimes, stimes, apfds = [], [], []
            for run in range(repeats):
                print (" Run", run)
                stime, ptime, prioritization = competitors.art_f(fin)
                writePrioritization(ppath, name, ctype, run, prioritization)
                apfd = metric.apfd(prioritization, fault_matrix, javaFlag)
                apfds.append(apfd)
                stimes.append(stime)
                ptimes.append(ptime)
                print("  Progress: 100%  ")
                print ("  Running time:", stime + ptime)
                if javaFlag:
                    print ("  APFD:", sum(apfds[run]) / len(apfds[run]))
                else:
                    print ("  APFD:", apfd)
            rep = (name, stimes, ptimes, apfds)
            writeOutput(outpath, ctype, rep, javaFlag)
            print("")
        else:
            print (name, "already run.")

    else:
        print("Wrong input.")
        print(usage)
        exit()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def writePrioritization(path, name, ctype, run, prioritization, testType='text'):
    if testType == 'text':
        fout = "{}/{}-{}-{}.pickle".format(path, name, ctype, run+1)
    else:
        fout = "{}/{}-{}-{}-{}.pickle".format(path, name, ctype, run+1, testType)
    pickle.dump(prioritization, open(fout, "wb"))


def writeOutput(outpath, ctype, res, javaFlag, testType='text'):
    if testType == 'text':
        fileout = "{}/{}-{}.tsv".format(outpath, name, ctype)
    else:
        fileout = "{}/{}-{}-{}.tsv".format(outpath, name, ctype, testType)
    if javaFlag:
        name, stimes, ptimes, apfds = res

        with open(fileout, "w") as fout:
            fout.write("SignatureTime\tPrioritizationTime\tTotal\n")
            for st, pt, total in zip(stimes, ptimes, apfds):
                tsvLine = "{}\t{}\t{}\n".format(st, pt, total)
                fout.write(tsvLine)
    else:
        name, stimes, ptimes, apfds = res
        
        with open(fileout, "w") as fout:
            fout.write("SignatureTime\tPrioritizationTime\tAPFD\n")
            for st, pt, apfd in zip(stimes, ptimes, apfds):
                tsvLine = "{}\t{}\t{}\n".format(st, pt, apfd)
                fout.write(tsvLine)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


if __name__ == "__main__":
    if len(sys.argv) == 5:
        # print("Wrong input.")
        # print(usage)
        # exit()
        prog_v, entity, algname, repeats, prj, testType = sys.argv[1:]
        
    elif len(sys.argv) == 3:
        prog_v = 'math_v4'
        entity = 'bbox'
        algname = 'FAST-pw'
        repeats = '1'
        prj, testType = sys.argv[1:]
    else:
        prj = 'math'
        prog_v = 'math_v4'
        entity = 'bbox'
        algname = 'FAST-pw'
        repeats = '1'
        testType = 'text'

    repeats = int(repeats)
    algnames = {"FAST-pw", "FAST-one", "FAST-log", "FAST-sqrt", "FAST-all",
                "STR", "I-TSD",
                "ART-D", "ART-F", "GT", "GA", "GA-S"}
    prog_vs = {"flex_v3", "grep_v3", "gzip_v1", "make_v1", "sed_v6",
               "closure_v0", "lang_v0", "math_v0", "chart_v0", "time_v0"}
    entities = {"bbox", "function", "branch", "line"}

    # if prog_v not in prog_vs:
    #     print("<dataset> input incorrect.")
    #     print(usage)
    #     exit()
    if entity not in entities:
        print("<entity> input incorrect.")
        print(usage)
        exit()
    elif algname not in algnames:
        print("<algorithm> input incorrect.")
        print(usage)
        exit()
    elif repeats <= 0:
        print("<repetitions> input incorrect.")
        print(usage)
        exit()

    prog, v = prog_v.split("_")

    directory = "output/{}_{}/".format(prog, v)
    if not os.path.exists(directory):
        os.makedirs(directory)
    directory += "prioritized/"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # FAST parameters
    k, n, r, b = 5, 10, 1, 10

    # FAST-f sample size
    if algname == "FAST-all":
        def all_(x): return x
        selsize = all_
    elif algname == "FAST-sqrt":
        def sqrt_(x): return int(math.sqrt(x)) + 1
        selsize = sqrt_
    elif algname == "FAST-log":
        def log_(x): return int(math.log(x, 2)) + 1
        selsize = log_
    elif algname == "FAST-one":
        def one_(x): return 1
        selsize = one_
    else:
        def pw(x): pass
        selsize = pw

    if prj == 'math':
        projects = ['4', '5', '6', '9', '13', '14', '17', '18', '19',
                    '20', '21', '23', '24', '25', '26', '27', '28', 
                    '30', '32', '33', '37', '42', '47', '49', '50', 
                    '51', '52', '54', '56', '58', '61', '64', '65', 
                    '67', '68', '69', '70', '73', '76', '78', '80', '81']
        # projects = ['61']

    # jsoup projects:
    # prj = 'jsoup'
    elif prj == 'jsoup':
        projects = [ '4', '15', '16', '19', '20', '26', '27', '29', 
                    '30', '33', '35', '36', '37', '38', '39', '40']

    # lang projects:
    # prj = 'lang'
    elif prj == 'lang':
        projects = [ '4', '6', '15', '16', '17', '19', '22', '23', '24', '25', '27', '28', '31', '33', '35']
        # projects = [ '4',            '16',                   '23', '24', '25', '27',       '31',       '35']

    # time projects:
    # prj = 'time'
    elif prj == 'time':
        projects = ['11','13']

    # cli projects:
    # prj = 'cli'
    elif prj == 'cli':
        projects = ['30','31','32','33','34']
        # projects = ['31','34']

    # csv projects:
    # prj = 'csv'
    elif prj == 'csv':
        projects = ['2', '3', '4', '5', '7', '8', '10', '11', '12', '16']
        # projects = ['2', '3', '4',           '8',             '12']

    # Codec jacoco coverage is not generating, so it is not working
    # codec projects:
    # prj = 'codec'
    # projects = ['11', '12', '15', '16']

    # compress projects:
    # prj = 'compress'
    elif prj == 'compress':
        projects = [ '1', '11', '16', '22', '24', '26', '27']

    for id in projects:
        if entity == "bbox":
            # bboxPrioritization(algname, prog, v, entity, k, n, r, b, repeats, selsize)
            bboxPrioritization(algname, prj, f'v{id}', entity, k, n, r, b, repeats, selsize, testType)
        else:
            wboxPrioritization(algname, prog, v, entity, n, r, b, repeats, selsize)
