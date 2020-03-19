import json
import ast
import csv
import sys
import multiprocessing
import os
import itertools
import random
import networkx
import matplotlib.pyplot as plt
import subprocess
import shutil
import math
import numpy as np
import time
import graphviz
import copy
import datetime
import time
sys.setrecursionlimit(100000)

# cavFieldsG = {}

def sid(clauses, variables, precision, t_max, frac):
    start = time.clock()
    iters = 0
    cycle = 0
    # og_clauses = copy.deepcopy(clauses)

    # # connect og_clauses with variables
    # for ogc in og_clauses:
    #     for v in ogc.vars.copy():
    #         ogc.remVar(v)
      
    # for v in variables:
    #     for c in v.clauses:    
    #         for ogc in og_clauses:
    #             if c.name == ogc.name:
    #                 ogc.addVar(v, v.clauses[c])
                   
        
    #     for ogc in og_clauses:
    #         # print 'ogc', ogc.name
    #         for item in v.clauses:
    #             if c.name == ogc.name:
    #                 # print c.name, ogc.name
    #                 ogc.addVar(v, v.get_edge_from_name(c.name))
    #         # if ogc.name in [c for c in og_clauses if c.name in [item.name for item in v.clauses]]:

              #   print ogc.name
            # print 'ogc add var'
       

    # keep track of unfixed vars and unsat clauses
    vars_unfix = set()
    clauses_unsat = set()
    # print 'copy done'
    for v in variables:
        vars_unfix.add(v)

    for c in clauses:
        clauses_unsat.add(c)
        
    # plotGraph(og_clauses, variables,  '-', {})

    # finished if all clauses are satisfied
    while len(clauses_unsat) > 0:
        # print '\nogc clauses'

        # print og clauses sub variables
        # for ogc in og_clauses:
        #     print 'c', ogc.name
            
        #     for v in ogc.vars:
        #         print '    v', v.name, v.val
        # print '\ncycle', cycle
        # print '\nog_clauses'
        # print sorted([(c.name, sorted([(v.name, c.getEdge(v)) for v in c.vars])) for c in og_clauses])
        # print '\nunsat clauses'
        # print sorted([(c.name, sorted([(v.name, c.getEdge(v)) for v in c.vars])) for c in clauses_unsat])
        # print 'unfixed variables'
        # print sorted([(v.name, sorted([(c.name, v.getEdge(c)) for c in v.clauses])) for v in vars_unfix])
        # print 'variables'
        # print sorted([(v.name, sorted([(c.name, v.getEdge(c)) for c in v.clauses])) for v in variables])
        # print unsat clauses sub vars
        # for c in clauses_unsat:
        #     print 'c', c.name, c.checkSAT()
            
        #     for v in c.vars:
        #         print '    v', v.name, v.val, v.getEdge(c)
                
        # print '\nvariables'

        # # print variables sub clauses
        # for v in variables:
        #     print 'v', v.name, v.val
            
        #     for c in v.clauses:
        #         print '    c', c.name, c.checkSAT()
        prop_res= sur_prop(clauses_unsat, start, t_max, precision)
        messages =  prop_res[0]
        iters += prop_res[1]
        # plotGraph(og_clauses, variables, str(cycle), messages) 
        if messages == 'UNCONVERGED':
            # print 'UNCONVERGED'
            c_sat = 0
            for c in clauses:
                if c.checkSAT() == 0:
                    c_sat +=1
            end = time.clock()
           
            return  len(variables), len(clauses), c_sat, end - start, iters, 'unconverged', {v.name: v.val for v in variables}
        

        else:
            trivial = True

            # check if messages trivial
            # print 'messages'
            
            # try:
            #     print sorted( [(i[0].name, i[1].name, messages[i]) for i in messages], key=lambda x:x[1])
            # except:
            #     pass
            for message in messages:
            #     print 'message', message[0].name, message[1].name, message[1].getEdge(message[0]), messages[message]

                if messages[message]  > 0 + precision:
                    trivial = False
                    break
            # for var in variables:
            #     if var.val == None:
            #         vars_unfix.add(var)
            #         print 'unfixed var', var.name, var.val
           
            
            if trivial == False and len(vars_unfix) > 0:
                variance = []

                for i in vars_unfix:
                    prod_v_plus = 1.
                    prod_v_min = 1.
                    prod_v_0 = 1.

                    for a in i.clauses:
                        prod_v_0 *= (1 - messages[(a, i)])

                        if a.getEdge(i) == 1:
                            prod_v_min *= (1 - messages[(a, i)])

                        elif a.getEdge(i) == -1:
                            prod_v_plus *= (1 - messages[(a, i)])
                    pi_plus = (1 - prod_v_plus) * prod_v_min
                    pi_min = (1 - prod_v_min) * prod_v_plus
                    pi_0 = prod_v_0

                    # no zero division
                    if pi_plus == 0:
                        w_plus = 0
                        
                    else:
                        w_plus = pi_plus / (pi_plus + pi_min + pi_0)
                        
                    if pi_min == 0:
                        w_min = 0
                        
                    else:
                        w_min = pi_min / (pi_plus + pi_min + pi_0)
                    w_0 = 1 - w_plus - w_min
                    variance.append((i, w_plus, w_min))
                # max_var = max(variance, key = lambda x : abs(x[1] - x[2]))
                variance.sort(key = lambda x: abs(x[1] - x[2]), reverse = True)
                n_fix = ceildiv(len(vars_unfix) , frac)
                for max_var in variance[:n_fix]:
                # print 'variance sorted'
                              
                # for k in variance:
                    # print k[0].name,  abs(k[1] - k[2])

                    if max_var[1] > max_var[2]:
                        max_var[0].val = 1
                        # print 'var', max_var[0].name, 'val', max_var[0].val

                    else:
                        max_var[0].val = -1 
                        # print 'var', max_var[0].name, 'val', max_var[0].val
                    # print '\nsat check'
            
            else:
                print 'should walk_sat'
                c_sat = 0
                for c in clauses:                        
                    if c.checkSAT() == 0:
                        c_sat +=1
                end = time.clock()                    
                return len(variables), len(clauses), c_sat, end - start, iters,\
                'out of vars',  {v.name: v.val for v in variables}
                
                # walk_sat(og_clauses, clauses, clauses_unsat, variables, vars_unfix)
            decimate(clauses_unsat, vars_unfix)

            # for c in clauses
            for v in vars_unfix:
                if check_contra(v, messages, precision):
                    c_sat = 0
                    
                    for c in clauses:
                        
                        if c.checkSAT() == 0:
                            c_sat +=1
                    end = time.clock()
                    return len(variables), len(clauses), c_sat, end - start, iters, 'contradiction',  {v.name: v.val for v in variables}
                
            for var in variables:
                if var.val == None:
                    vars_unfix.add(var)
            
            for c in clauses:
                if c.checkSAT() == 2:
                    clauses_unsat.add(c)
            # plotGraph(og_clauses,  variables, str(cycle), {})
            # print 'n unfixed vars', len(vars_unfix)
            # print 'n unsat clauses', len(clauses_unsat)
       
        cycle +=1
    # plotGraph(clauses, variables, 'fin', messages)
    # print 'SAT'
    # for c in og_clauses:
    #     # print 'c', c.name, c.checkSAT()
            
    #     for v in c.vars:
            # print '    v',v.name, v.val, v.getEdge(c)
    # for v in variables:
    #     print 'v', v.name, v.val

    #     for c in v.clauses:
    #         print '    c', c.name, c.checkSAT(), c.getEdge(v)
    # print "SATISFIED"
    c_sat = 0
    for c in clauses:
        if c.checkSAT() == 0:
            c_sat +=1
    end = time.clock()
    return len(variables), len(clauses), c_sat, end - start, iters, 'succesful', {v.name: v.val for v in variables}

                              
def check_contra(var , messages, precision):
    # print 'check_contra'
    # print 'v', var.name
    clause_list = list(var.clauses)
    
    for c in clause_list:
        for c2 in [c2 for c2 in clause_list if clause_list.index(c2) > clause_list.index(c)]:
            # print clause_list.index(c2), clause_list.index(c),  messages[(c, var)], messages[(c2, var)], messages[(c, var)] * messages[(c2, var)] + precision
            if messages[(c, var)] * messages[(c2, var)] + precision >= 1. and var.getEdge(c) != var.getEdge(c2):
                print 'Contradiction', 'var', var.name, 'c1', c.name, 'e1', var.getEdge(c), 'm1', messages[(c, var)], 'c2', c2.name, 'e2', var.getEdge(c2), 'm2', messages[(c2, var)]
                return True
    else:
        return False
   
                
           
def sur_prop(clauses, start, t_max, precision):

    # clauses = clauses_unsat
    messages = {}
    oldMessages = {}
    t = 0
   
    # generate random messages u_a -> i, messages from clauses to variables
    for a in clauses:
        for i in a.vars:
            messages[(a, i)] = random.random()

    # print '\ninitial u_a - > i: '
    # print 'clause, variable, message value'
    # for message in messages:
    #     print "c_"+str(message[0].name), "v_"+str(message[1].name), messages[message]

    edges = messages.keys()
    # print 'len(edges)', len(edges)
    t += 1
    
    # while t < t_max, iterate over every edge in a random fashion and update
    # warnings sequntially using the sp_update routine
    
    while t <= t_max:
        random.shuffle(edges)
        # print  '\nt = ', t
        
        for edge in edges:
            i = edge[1]
            a = edge[0]

            # store old messages in similar dictionary as messages
            oldMessages[(a,i)] = messages[(a,i)]
            
            # update messages with sp_update
            messages[(a,i)] = sp_update(messages, a, i)
        convergence = True

        # # check for convergence
        # hi_diff = 0
        # diff_sum = 0 
        
        for message in messages:
            # diff =  abs(messages[message] - oldMessages[message])
            # diff_sum += diff
            
            # if diff > hi_diff:
            #     hi_diff = diff
            
            # print 'c', message[0].name, 'v',message[1].name, 'new: ', messages\
            #     [message], 'old: ', oldMessages[message], 'diff: ',\
            #     abs(messages[message] - oldMessages[message]), 't= ', t
        
           
            if abs(messages[message] - oldMessages[message]) > precision:
                convergence = False
        # avg_diff =  diff_sum / len(messages)
        # print 't', t, 'hi_diff', hi_diff, 'avg_diff', avg_diff
        # print 't', t
        
        # if converged return warnings
        
        if convergence == True:
            # print '\nconverged in  t = ', t
            return messages, t
        
       
        # if not, and time is up, return uncovnerged
        elif t == t_max:
            return 'UNCONVERGED',t
        t += 1
        
        
def sp_update(messages, a, i):
    # print 'a, i', a.name, i.name
    newMessage = 1.0
    cavFields = {}
 
    for var in a.vars:
        prob_u = 1.
        prob_s = 1.
        prob_0 = 1.
        
        if var != i:
            j = var
            # print 'a', a.name, 'v', var.name
           
            edgeVal_a_j = a.getEdge(j)
            # print 'edgeval a j ', edgeVal_a_j

            # print '    a, j', a.name, j.name

            for clause in j.clauses:
                if clause != a:
                    b = clause
                    edgeVal_b_j = j.getEdge(b)

                    # print '        b, j', b.name, j.name
                    prob_0 *= (1. - messages[(b, j)])

                    # print '    prob_0', prob_0
                    
                    # if b element of V^s_a(j) multiply prob_s by
                    # (1 - message value)
                    if edgeVal_a_j == edgeVal_b_j:
                        prob_u *= (1. - messages[(b, j)])
                        
                        # print '    prob_u', prob_u
                     
                    # else if b element of V^u_a(j), multiply prob_u by
                    # (1 - message value)
                    elif edgeVal_a_j == -1. * edgeVal_b_j:
                        prob_s *= (1. - messages[(b, j)])
                        
                        # print '    prob_s', prob_s
     
            # store cavity field and update new warning
            # print 'j = ', j.name
            pi_u = (1 - prob_s) * prob_u
            pi_s = (1 - prob_u) * prob_s
            pi_0 = prob_0
            
            if prob_u != 0:
                cavFields[(j,a)] = prob_u / (prob_u + prob_s + prob_0)

            else:
                cavFields[(j,a)] = 0.
                
            # print 'appending to cavfieldsG in bpUpdate'
            # cavFieldsG[(j,a)] = cavFields[(j,a)]
                
            # print '    cav', a.name, j.name, cavFields[(j,a)], '\n'
            newMessage *=  cavFields[(j,a)]
    return newMessage

def decimate(clauses_unsat, vars_unfix):
    for c in clauses_unsat.copy():

        # print clauses_unsat sub vars after algorithm                      
        if c.checkSAT() == 2:
            # print '\nc', c.name, 'UNSAT'
            output = ''
            
            for v in c.vars:
                if v.val == None:
                    output += 'v ' + str(v.name) + ' ' + str(v.val) + '\n'
                    # print 'v', v.name, v.val,

                elif v.val * c.getEdge(v) == 1:
                    output += 'v ' + str(v.name) + ' ' + str(v.val) + ' UNSAT\n'
                    # print 'v', v.name, v.val, 'UNSAT'
                    
                else:
                    raise Exception('oh no')
            # print output
             
        # if c sat
        else:
            # print '\nc', c.name, 'SAT'
            # print 'removing c', c.name
            # remove clause from clauses_unsat
            clauses_unsat.remove(c)

            # remove sat clauses from variables
            for v in c.vars:
                if c in v.clauses:
                    # print 'removing c', c.name, 'from v', v.name
                    v.remCls(c)
                
    # remove assigned vars from vars_unfix
    for v in vars_unfix.copy():
        if v.val != None:
            # print 'removing v', v.name, v.val, 'from vars_unfix'
            vars_unfix.remove(v)

            # remove variables from clauses if they are assigned a val
            for c in v.clauses:
                # print 'removing v', v.name, v.val, 'from c', c.name 
                c.remVar(v)

def walk_sat(og_clauses, clauses, clauses_unsat, variables, vars_unfix):
    # print 'WALKSAT
    
    c = random.choice(list(clauses_unsat))
    # print 'random c', c.name
    unsatisfiers = {}
    clauses_sat = [cls for cls in clauses if cls not in clauses_unsat]

    # # update og_clauses
    # for ogc in og_clauses:
    #     for ogc_v in ogc.vars:
    #         for v in variables:
    #             if ogc_v.name == v.name:
    #                 ogc_v.val = v.val
    
    if random.random() < 0.8:
        # print 'least unsat mode'
        
        for v in c.vars:
            store_unsat(og_clauses, v, unsatisfiers, clauses_sat)

        # find potenial variable flip with least c unsats
        min_unsatisfied = 100
        best = []
        
        for v in unsatisfiers:
            # print 'v', v.name, 'n pot unsat', [i.name for i in unsatisfiers[v]]
            
            if len(unsatisfiers[v]) < min_unsatisfied:
                min_unsatisfied = len(unsatisfiers[v])
                best = [v]
                
            elif len(unsatisfiers[v]) == min_unsatisfied:
                best.append(v)
        # print 'best list', [i.name for i in best]
        best = random.choice(best)
        
    else:
        # print 'random mode'
        best = random.choice(list(c.vars))
        store_unsat(og_clauses, v, unsatisfiers, clauses_sat)
    best.val *= -1
    # print 'best var', best.name, 'val', best.val

    # re-add clauses 
    for c in unsatisfiers[best]:
        best.addClause(c, c.getEdge(best))
        # print 'added c', c.name, 'to v', best.name
    
def store_unsat(og_clauses, v, unsatisfiers, clauses_sat):
    # print 'clauses_sat', [i.name for i in clauses_sat]
    unsatisfied = []
    v.val *= -1
    for c in [ogc for ogc in og_clauses if ogc.name in [x.name for x in clauses_sat]]:

        if c.checkSAT() == 2:
            unsatisfied.append(c)

    v.val *= -1
    # print 'unsatisfied'

    # for u in unsatisfied:
    #     print u.name
    unsatisfiers[v] = unsatisfied
    
def sim_an(clauses, variables, t_max):
   
    start = time.clock()
    # print 'start', start
    t = time.clock() - start
    s_max = len(clauses)
    # start_score = s_max - (sum(c.checkSAT() for c in clauses) / 2.)
    # print 's_max', s_max
    
    for v in variables:
        v.val =  random.randrange(-1, 2, 2)
    score = sum(c.checkSAT() for c in clauses) / 2.
    hi_score = score
    cur_state = {v: v.val for v in variables}
   
    while score > 0:
        # tx.append(t)
        # sx.append(score)
        ran_v = random.choice(list(variables))
        ran_v.val *= -1
        new_score = sum(c.checkSAT() for c in clauses) / 2.
        a_T = -1
        b_T = t_max
        T = lin_eq(t, a_T, b_T)
        x = new_score - score
        P = prob(x, t_max, t, T)
      
        ran = random.random()
    
        if  ran <=P:
            # if x > 0:
                # print 'P', P
                # print ran, '<=', P, 't', t, 'new score', new_score, 'T', T 
            # print 'cur_state', sorted([(i.name, cur_state[i])\
            #                            for i in cur_state], key=lambda x: x[0])

        
            score = new_score
            
            cur_state = {v : v.val for v in variables}

            if score < hi_score:
                hi_score = score
                # print s_max - hi_score, s_max

            
            # print 'new_state', sorted([(i.name, cur_state[i])\
            #                            for i in cur_state], key=lambda x: x[0])
            
        else:
            revert_state(cur_state, variables)
        t = time.clock() - start
        # print 't', t - start, 'tmax', t_max
        if t >= t_max:
            end = time.clock()
            
            return len(variables), len(clauses), s_max - hi_score, end - start, 'unsuccesful', {v.name : v.val for v in cur_state}
            # return tx, sx, score, sorted([(i.name, cur_state[i]) for i in cur_state], key=lambda x: x[0])
    # return tx, sx, sorted([(i.name, cur_state[i]) for i in cur_state], key=lambda x: x[0])
    end = time.clock()
    return len(variables), len(clauses), s_max - hi_score, end - start, 'succesful', {v.name : v.val for v in cur_state}
def revert_state(state, variables):
    for v in variables:
        v.val = state[v]

def prob(x,  t_max, t, T):
   
    if x > 0:
        n = 2 / abs(x)
        P = (T / (2 * t_max)) * n
       
        
    elif x < 0:
        P = 1
    
    else:
        P = .5
       
    return P
    
def lin_eq(x, a, b):
    return a * x + b

   
        
def ceildiv(a, b):
    return -(-a / b)

     
   
    # for c in clauses:
    #     print c.name, c.checkSAT()

    #     for v in c.vars:
    #         print '    v', v.name, v.val, v.getEdge(c)
        
        
        
    
class Clause:
    def __init__(self, name, vars):
        self.type = 'c'
        self.name = name
        self.vars = vars
        self.K = len(vars)

        # combine variable objects and edges into key-value pairs
    
    def getEdge(self, var):
            return self.vars[var]
        
    def get_edge_from_name(self, var_name):
        for v in self.vars:
            if v.name == var_name:
                return self.vars[v]
    
    def addVar(self, var, edge):
        self.vars[var] = edge
        self.K += 1

    def remVar(self, var):
        del self.vars[var]
        self.K -= 1
    
    def checkSAT(self):
    # check if variables satisfy clause, returns 0 (SAT) or 2 (UNSAT)

        # products of edge values {-1, 1}, and variable values {-1, 1}
        edgeValProducts = set()
        
        # calculate edge * value
        empty = True 
        for var in self.vars:
            if var.val != None:
                empty = False
                edgeValProducts.add(var.val * self.getEdge(var))

                # if var.val * self.getEdge(var) == -1:
                #     print 'variable: ', var.name, 'SAT'
                    
                # else:
                #     print 'variable: ', var.name, 'UNSAT' 

        # sat = 0 if at least one variable satisfies clause, else sat = 2
        # [mezard K-SAT paper eq. 5]
        
        if empty == True:
            return 2
        
        else:
            sat = 1
            
            for i in edgeValProducts:
                sat *= (1 + i) / 2.0

                # if one variable satisfies, do not calculate others
                if sat == 0:
                    break
                
            return int(2 * sat)
    
class Variable:
    def __init__(self, name, clauses):
        self.type = 'v'
        self.name = name
        self.val = None
        self.clauses = clauses
        self.K = len(clauses)

    def getEdge(self, clause):
        return self.clauses[clause]

    def get_edge_from_name(self, clause_name):
        print [(c.name, self.clauses[c]) for c in self.clauses]
        print clause_name
        for c in self.clauses:
            print 'v', self.name, 'c', c.name
            if c.name == clause_name:
                print self.clauses[c], c.name, clause_name
                return self.clauses[c]
    
    def addClause(self, clause, edge):
        self.clauses[clause] = edge
        self.K += 1
        
    def remCls(self, clause):
        del self.clauses[clause]
        self.K -= 1

class MyTimer():
    def __init__(self):
        self.start = time.time()
 
    def __enter__(self):
        return self
 
    def __exit__(self, exc_type, exc_val, exc_tb):
        end = time.time()
        runtime = end - self.start
        msg = 'The function took {time} seconds to complete'
        print(msg.format(time=runtime))


def ran_3sat(nc, nv):
    while True:
        loop = 0
        edgs = {}
        indi_vars = set()
        enough_edges = False
        all_v_included = True
        # print 'loop', loop
        
        for c in range(nc):
            ran_vars = {}
            # print 'c', c
            while len(ran_vars) < 3:
                ran_vars = {random.choice(range(nv)) for _ in range(3)}
       
            for v in ran_vars:
                # print v
                edgs[(c, v)] = random.randrange(-1, 2, 2)
                indi_vars.add(v)

        # checks
        if len(edgs) == (3 * nc):
            enough_edges = True
            
        # else:
            # print 'edges', len(edgs), 'req:', 3 * nc

        for v in range(nv):
            # print v
            if v not in indi_vars:
                # print v, 'not in', indi_vars
                all_v_included = False
        loop +=1
        
        if enough_edges == True and all_v_included == True:
            break
    return edgs
            
        

# Braunstein survey propogation paper Fig. 3
braun_edgs = {(1, 1) : -1,\
               (2, 2) : 1,\
               (3, 1) : 1, (3, 2) : -1, (3, 3) : -1,\
               (4, 3) : 1, (4, 4) : -1 ,\
               (5, 3) : -1, (5, 5) : -1,\
               (6, 4) : -1,\
               (7, 4) : -1,(7, 7) : 1,\
               (8, 5) : -1, (8, 8) : -1,\
               (9, 5) : 1, (9, 6) : -1}

def sat_loader(es):
    cs = {}
    vs = {}
    cs_out = set()
    vs_out = set()

    for e in es:      
        if e[0] not in cs:
            cs[e[0]] = Clause(e[0], {})

        if e[1] not in vs:
            vs[e[1]] = Variable(e[1], {})
        cs[e[0]].addVar(vs[e[1]], es[e])
        vs[e[1]].addClause(cs[e[0]], es[e])
   
    for c in cs:
        cs_out.add(cs[c])
        
    for v in vs:
        vs_out.add(vs[v])
    
    return cs_out, vs_out

def plotGraph(clauses, variables, imgName, messages):
        
    # print 'plotgraph: printing cavity fields G'
    
    # for i in cavFieldsG:
        
        # print 'cavFieldsG entry: ', i[1].name, i[0].name, cavFieldsG[i]
        
   
        
    # print 'plotgraph: messages'
    
    # for key in messages:
        
    #     print key[0].name, key[1].name, messages[key]

    g = graphviz.Graph(format='png')
    g.graph_attr.update(ranksep='3')

    for v in variables:
        g.node('v '+str(v.name), 'v '+str(v.name)+'\n'+str(v.val),shape= 'circle')
    # print 'plotgraph: cavity fields'
    for c in clauses:
        if c.checkSAT() == 2:
            
            g.node('c ' + str(c.name)  , shape= 'square', color='black')
        else:
            
            g.node('c ' + str(c.name)  , shape= 'square', color = 'green')
        
        # if c.checkSAT() == 2:
        for var in c.vars:

                # if  cavFieldsG.get((var, c)) != None:

                    # print 'c',c.name,'v', var.name, cavFieldsG[(var,c)]
          

            if var.val == None or c.getEdge(var) * var.val != -1:
                if c.getEdge(var) == -1:
                    # print 'c', c.name, 'v', var.name, 'e', c.getEdge(var), 'val', var.val, 'blue' # 
                    g.edge('c ' + str(c.name), 'v '+str(var.name), color = 'blue')


                elif c.getEdge(var) == 1:
                    # print 'c', c.name, 'v', var.name, 'e', c.getEdge(var),'val', var.val, 'red'
                    g.edge('c ' + str(c.name), 'v '+str(var.name), color = 'red')
                    
            else:
                if c.getEdge(var) == -1:
                    # print 'c', c.name, 'v', var.name, 'e', c.getEdge(var),'val', var.val, 'purple
                    
                    g.edge('c ' + str(c.name), 'v '+str(var.name), color = 'green')
                   
                elif c.getEdge(var) == 1:
                      # print 'c', c.name, 'v', var.name, 'e', c.getEdge(var),'val', var.val, 'orange'
                  
                      g.edge('c ' + str(c.name), 'v '+str(var.name), color = 'green')

                        
            # if c.getEdge(var) == -1 and var.val == -1 or var.val == None
            
               
               #  \
                               # label = 'm'+str(messages[(c, var)])[:5]  + '\n' + \
                               #  'c'+str(cavFieldsG[(var, c)])[:5])

            # elif c.getEdge(var) == 1 and var.val == 1 or var.val ==  None:
               
                               # label = 'm'+str(messages[(c,var)])[:5] + '\n' + \
                               #  'c'+str(cavFieldsG[(var, c)])[:5])
                # else:
                #     # print c.name, var.name, 'does not have a cavity field'

                #     if c.getEdge(var) == -1:
                #         g.edge('c ' + str(c.name), 'v '+str(var.name), color = 'blue', \
                #                    label = str(messages[(c,var)])[:5])

                #     else:  
                #         g.edge('c ' + str(c.name), 'v '+str(var.name), color = 'red', \
                #                    label = str(messages[(c,var)])[:5])       
       
            # elif c.getEdge(var)  == -1 and var.val == 1:
               
            # elif c.getEdge(var)  == 1 and var.val == -1:
              
                    
    g.render('out/'+imgName, view=False)
def a_seq(base, lo, up, step):
    return np.arange(base * lo, base * up, base * (up - lo) / step)


        

      
            # if i in selection:
            #     print 'in'
            # else:
            #     print 'out'
            # if str(i)[10:15] in selection:
            #     print i
  
            

    
    
    # with open("problems/problems.json", "r") as f:
    #     q = json.load(f)
    #     converted={ast.literal_eval(k): v for k, v in q.iteritems()} 
    #     print '\n',sorted(converted.keys(), key = lambda x : x[1])

    
    # p_copy = copy.deepcopy(p)
    
    # shutil.rmtree('out')
    # os.mkdir('out')
    # t_max = 1000.
    # precision = 0.001

    # results = []
    
        
    # # result = sid(p[0], p[1],precision, t_max)
    # t_sim = 12.
    # simres = sim_an(p_copy[0], p_copy[1], t_sim)
    # results.append(', simres:'+str(simres))
        
    # print results   s


def get_problems(n, start, end):
    todo = {}
    a_range =  np.arange(3.400, 4.624, 0.024)
    selection = ["{:.3f}".format(i) for i in a_range[start:end]]
    print 'selection', selection, 'len(selection)', len(selection)
    path = "./problems/"
    c = 0
    
    for s in selection:
        todo[s] = []
        
        for i in os.listdir("./problems/"):
            if i[:4] == n and i[10:15] in s:
                todo[s].append(i)
        else:
            todo[s].sort()    

    return todo


def exe_algs(part, t_max, precision, frac):
    save_str =  part[0][0:4] + '_' +  part[0][10:15] + '_' + part[0][16:18]\
                + '--'  + part[len(part) - 1][10:15] + '_' + part[len(part) - 1][16:18]
    
    with open(uniq_output("results/18-03/"+str(frac)+"/"+save_str), 'w') as fo:
        cw = csv.writer(fo, delimiter=';')
        cw.writerow(['prob', 'n_v_sid', 'n_c_sid','n_c_solved_sid',
                     't_solved_sid', 'sur_prop_iters',  'result_sid', 'n_v_sim', 'n_c_sim', 'n_solved_sim', 't_solved_sim', 'result_sim'])
        part_start = time.clock()
        for p in part:
            print list(part).index(p), len(part) - 1
            print p
            with open("./problems/" + p, "r") as fi:
                r = [p]
                j = json.load(fi)
                interpreted = {ast.literal_eval(k): v for k, v in j.iteritems()}
                j = sat_loader(interpreted)
                sid_res = sid(j[0], j[1], precision, t_max, frac)
                r.extend(sid_res[:-1])
                with open("./results/solutions/" + "sid" + p, 'w') as sol:
                    json.dump(sid_res[-1:], sol)
                t_sim = sid_res[3]
                j = sat_loader(interpreted)
                sim_res=sim_an(j[0], j[1], t_sim)
                with open("./results/solutions/" + "sim" + p, 'w') as sol:
                    json.dump(sim_res[-1:], sol)
                r.extend(sim_res[:-1])
                cw.writerow(r)
        else:
            part_end = time.clock()
            cw.writerow([part_end - part_start])




def main(n, start, end, t_max, precision, frac):
    jobs =[]
    todo = get_problems(str(n).zfill(4), start, end)
    for a in sorted(todo.keys()):
        print a
        print todo[a]

  
        split = np.array_split(todo[a], 4)

        for part in split:
            proc = multiprocessing.Process(target=exe_algs, args=(part, t_max, precision, frac,))
            jobs.append(proc)
            proc.start()

        for proc in jobs:
            proc.join()

    
   

    
def uniq_output(name):
    if os.path.isfile('./' + name +  '.csv'):
        print './' + name +  '.csv already exists, making new csv'
        i = 1

        # create unique fname
        while os.path.isfile("{}{:s}.csv".format('./'+ name ,\
                                                 '(' + str(i) + ')')):
            i += 1
        savename = "{}{:s}.csv".format('./'+ name, '(' +\
                                       str(i) + ')')
        print 'saving as',  savename 
    else:
        savename = './'+ name + '.csv'
        print 'saving as', './'+ name +  '.csv'
        
    return savename

if __name__== "__main__":
    main(125, 0, 10, 1000, 0.001, 50)
   



            

   

    

    
    
# def problem_generator():
    
#     for n in [125, 250, 500, 1000]:
#         seq =  a_seq(n, 3.4, 4.6, 50)
        
#         for c in seq:
            
#             for r in range(50):
        
#                 print "problems/"+ str(n).zfill(4)+"_"+"{:.3f}".format(c / n)+"_"+str(int(c)).zfill(2)+"_"+str(r).zfill(2)+".json",
#                 print "{:.2f}"."{:.2f}".
                
#                 with open("problems/"+ str(n).zfill(4)+"_"+"{:.3f}".format(c / n)+"_"+str(int(c)).zfill(2)+"_"+str(r).zfill(2)+".json", "w") as f:
#                     print n,  c, list(seq).index(c,) r
#                     p = ran_3sat(c, n)
#                     # print sorted(p.keys(), key = lambda x : x[1])
#                     p = {str(k): v for k, v in p.iteritems()}
#                     json.dump(p, f)

    # with open("problems/problems.json", "r") as f:
    #     q = json.load(f)
    #     converted={ast.literal_eval(k): v for k, v in q.iteritems()} 
    #     print '\n',sorted(converted.keys(), key = lambda x : x[1])

    
    # p_copy = copy.deepcopy(p)
    
    # shutil.rmtree('out')
    # os.mkdir('out')
    # t_max = 1000.
    # precision = 0.001

    # results = []
    
        
    # # result = sid(p[0], p[1],precision, t_max)
    # t_sim = 12.
    # simres = sim_an(p_copy[0], p_copy[1], t_sim)
    # results.append(', simres:'+str(simres))
        
    # print results   
    
    
    # graph = ran_3sat(9455, 2500)
    # clauses_b, variables_b = sat_loader(graph)
    # graph = ran_3sat(10360, 2500)
    # clauses_c, variables_c = sat_loader(graph)
    # graph = ran_3sat(11265, 2500)
    # clauses_d, variables_d = sat_loader(graph)
    # print 'c',len(clauses), 'v', len(variables)
    # v_n = set()
    # c_n = set()
    # for v in variables:
    #     v_n.add(v)
    # for c in clauses:
    #     c_n.add(c)
    # print sorted([v.name for v in v_n])
    # print sorted([v.name for v in c_n])
    # print len(v_n)
    # print len(c_n)
    
        
        
    # typ_a =  sim_an(clauses_a, variables_a, t_max)
    # typ_b =  sim_an(clauses_b, variables_b, t_max)
    # typ_c = sim_an(clauses_c, variables_c, t_max)
    # typ_d = sim_an(clauses_d, variables_d, t_max)
  
    # xa = typ_a[0]
    # ya = typ_a[1]
    # xb = typ_b[0]
    # yb = typ_b[1]
    # xc = typ_c[0]
    # yc = typ_c[1]
    # xd = typ_d[0]
    # yd = typ_d[1]
  
    # # x2 = typ_b[0]
    # # y2 = typ_b[1]
    # plt.title('Simulated Annealing at N = 2500')
    # plt.plot(xa, ya, 'r', label = '$\\alpha = 3.420$')
    # plt.plot(xb, yb, 'magenta', label = '$\\alpha = 3.782$')
    # plt.plot(xc, yc, 'g', label = '$\\alpha = 4.144$')
    # plt.plot(xd, yd, 'blue', label = '$\\alpha = 4.506$')
    # plt.xlabel('$t$')
    # plt.ylabel('$n$ Unsatisfied Clauses')
    
    # plt.legend()
    # plt.show()
    # ka = 5
  
    # for i in range(100):
    #     print {random.choice(range(ka)) for _ in range(3)}
    
  

   
    # with MyTimer():
    #     # clauses, variables = sat_loader(braun_edgs) 
    #     sid(clauses, variables, precision, t_max)
