import os
import itertools
import random
import networkx
import matplotlib.pyplot as plt
import subprocess
import shutil
import math
import numpy
import time
import graphviz
import copy

cavFieldsG = {}

def sid(clauses, variables, precision, t_max):
    cycle = 0
    og_clauses = copy.deepcopy(clauses)

    for ogc in og_clauses:
        for v in ogc.vars.copy():
            ogc.remVar(v)
        
    for v in variables:
        for ogc in [c for c in og_clauses if c.name in [item.name for item in v.clauses]]:
            ogc.addVar(v, v.get_edge_from_name(c.name))
    
    vars_unfix = set()
    clauses_unsat = set()
    
    for v in variables:
        vars_unfix.add(v)

    for c in clauses:
        clauses_unsat.add(c)
        
    plotGraph(clauses, variables, str(cycle), {})
    
    while len(clauses_unsat) > 0:
        print '\nogc clauses'
        
        for ogc in og_clauses:
            print 'c', ogc.name
            
            for v in ogc.vars:
                print '    v', v.name, v.val
        print '\ncycle', cycle
        print '\nunsat clauses'
        
        for c in clauses_unsat:
            print 'c', c.name, c.checkSAT()
            
            for v in c.vars:
                print '    v', v.name, v.val, v.getEdge(c)
                
        print '\nvariables'
        
        for v in variables:
            print 'v', v.name, v.val
            
            for c in v.clauses:
                print '    c', c.name, c.checkSAT()
                       
        messages =  sur_prop(clauses_unsat, t_max, precision)
        # plotGraph(clauses, variables, str(cycle), messages) 
        if messages == 'UN-CONVERGED':
            return 'UN-CONVERGED'
        
        else:
            trivial = True

            # check if messages trivial
            for message in messages:
                print 'message', message[0].name, message[1].name, messages[message]

                if messages[message]  > 0:
                    trivial = False
                    
            # for var in variables:
            #     if var.val == None:
            #         vars_unfix.add(var)
            #         print 'unfixed var', var.name, var.val
            print 'n unfixed vars', len(vars_unfix)
            print 'n unsat clauses', len(clauses_unsat)
            
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
                max_var = max(variance, key = lambda x : abs(x[1] - x[2]))
                variance.sort(key = lambda x: abs(x[1] - x[2]), reverse = True)

                print 'variance sorted'

                for k in variance:
                    print k[0].name,  abs(k[1] - k[2])

                if max_var[1] > max_var[2]:
                    max_var[0].val = 1
                    print 'var', max_var[0].name, 'val', max_var[0].val

                else:
                    max_var[0].val = -1 
                    print 'var', max_var[0].name, 'val', max_var[0].val
                print '\nsat check'
            
            else:
                walk_sat(og_clauses, clauses, clauses_unsat, variables, vars_unfix)
            decimate(clauses_unsat, vars_unfix)
            
            for var in variables:
                if var.val == None:
                    vars_unfix.add(var)
            
            for c in clauses:
                if c.checkSAT() == 2:
                    clauses_unsat.add(c)
            
        cycle +=1
    # plotGraph(clauses, variables, 'fin', messages)
    # print 'SAT'
    for c in og_clauses:
        print 'c', c.name, c.checkSAT()
            
        for v in c.vars:
            print '    v',v.name, v.val, v.getEdge(c)
    for v in variables:
        print 'v', v.name, v.val

        for c in v.clauses:
            print '    c', c.name, c.checkSAT(), c.getEdge(v)
    print "SATISFIED"
    return clauses, variables

def sur_prop(clauses, t_max, precision):
    messages = {}
    oldMessages = {}
    vars = []
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
    t += 1
    
    # while t < t_max, iterate over every edge in a random fashion and update
    # warnings sequntially using the sp_update routine
    while t < t_max:
        print t
      
        random.shuffle(edges)
        # print  '\nt = ', t

        for edge in edges:
            i = edge[1]
            a = edge[0]

            # store old messages in similar dictionary as messages
            oldMessages[(a,i)] = messages[(a,i)]
            
            # update messages with bpUpdate
            messages[(a,i)] = sp_update(messages, a, i)   
        convergence = True

        # check for convergence
        hi_diff = 0
        diff_sum = 0 
        
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
            print '\nconverged in  t = ', t
            
            return messages

        # if not, and time is up, return uncovnerged
        elif t == t_max:
            return 'UNCONVERGED'
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
            cavFieldsG[(j,a)] = cavFields[(j,a)]
                
            # print '    cav', a.name, j.name, cavFields[(j,a)], '\n'
            newMessage *=  cavFields[(j,a)]
   
    return newMessage


def decimate(clauses_unsat, vars_unfix):
    for c in clauses_unsat.copy():
        if c.checkSAT() == 2:
            print '\nc', c.name, 'UNSAT'
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
            print output
             
        # if c sat
        else:
            print '\nc', c.name, 'SAT'
            print 'removing c', c.name
            clauses_unsat.remove(c)
            
            for v in c.vars:
                if c in v.clauses:
                    print 'removing c', c.name, 'from v', v.name
                    v.remCls(c)
                
    # remove assigned vars from vars_unfix
    for v in vars_unfix.copy():
        if v.val != None:
            print 'removing v', v.name, v.val, 'from vars_unfix'
            vars_unfix.remove(v)

            for c in v.clauses:
                print 'removing v', v.name, v.val, 'from c', c.name 
                c.remVar(v)

def walk_sat(og_clauses, clauses, clauses_unsat, variables, vars_unfix):
    print 'WALKSAT'
    c = random.choice(list(clauses_unsat))
    print 'random c', c.name
    unsatisfiers = {}
    clauses_sat = [cls for cls in clauses if cls not in clauses_unsat]

    # # update og_clauses
    # for ogc in og_clauses:
    #     for ogc_v in ogc.vars:
    #         for v in variables:
    #             if ogc_v.name == v.name:
    #                 ogc_v.val = v.val
    
    if random.random() < 0.8:
        print 'least unsat mode'
        
        for v in c.vars:
            store_unsat(og_clauses, v, unsatisfiers, clauses_sat)

        # find potenial variable flip with least c unsats
        min_unsatisfied = 100
        best = []
        
        for v in unsatisfiers:
            print 'v', v.name, 'n pot unsat', [i.name for i in unsatisfiers[v]]
            
            if len(unsatisfiers[v]) < min_unsatisfied:
                min_unsatisfied = len(unsatisfiers[v])
                best = [v]
                
            elif len(unsatisfiers[v]) == min_unsatisfied:
                best.append(v)
        print 'best list', [i.name for i in best]
        best = random.choice(best)
        
    else:
        print 'random mode'
        best = random.choice(list(c.vars))
        store_unsat(og_clauses, v, unsatisfiers, clauses_sat)
    best.val *= -1
    print 'best var', best.name, 'val', best.val

    # re-add clauses 
    for c in unsatisfiers[best]:
        best.addClause(c, c.getEdge(best))
        print 'added c', c.name, 'to v', best.name
    
def store_unsat(og_clauses, v, unsatisfiers, clauses_sat):
    print 'clauses_sat', [i.name for i in clauses_sat]
    unsatisfied = []
    v.val *= -1
    for c in [ogc for ogc in og_clauses if ogc.name in [x.name for x in clauses_sat]]:

        if c.checkSAT() == 2:
            unsatisfied.append(c)

    v.val *= -1
    print 'unsatisfied'

    for u in unsatisfied:
        print u.name
    unsatisfiers[v] = unsatisfied

def sim_an(clauses, variables):
    # init vals
    score = 100000
    
    for v in variables:
        v.val =  random.randrange(-1, 2, 2)
        
    while score > 0:
        ran_v = random.choice(list(variables))
        ran_v.val *= -1
        new_score = sum(c.checkSAT() for c in clauses)
        
        print 'score', score
        print 'new_score', new_score
            
        if new_score < score:
            score = new_score
            
        else:
            ran_v.val *= -1
        


     
   
    for c in clauses:
        print c.name, c.checkSAT()

        for v in c.vars:
            print '    v', v.name, v.val, v.getEdge(c)
        
        
        
    
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
        for c in self.clauses:
            if c.name == clause_name:
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
    edgs = {}

    for c in range(nc):
        
        ran_vars = random.sample(range(nv), 3)
        
        for v in ran_vars:
            edgs[(c, v)] = random.randrange(-1, 2, 2)
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
    print 'plotgraph: printing cavity fields G'
    
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
        g.node('c '+str(c.name), shape= 'square')
        
        if c.checkSAT() == 2:
            for var in c.vars:

                # if  cavFieldsG.get((var, c)) != None:

                    # print 'c',c.name,'v', var.name, cavFieldsG[(var,c)]

                if c.getEdge(var) == -1:
                    g.edge('c ' + str(c.name), 'v '+str(var.name), color = 'blue')#  \
                               # label = 'm'+str(messages[(c, var)])[:5]  + '\n' + \
                               #  'c'+str(cavFieldsG[(var, c)])[:5])

                else:  
                    g.edge('c ' + str(c.name), 'v '+str(var.name), color = 'red')
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

    g.render('out/'+imgName+'.gv', view=True)  
if __name__== "__main__":
 
    shutil.rmtree('out')
    os.mkdir('out')
    t_max = 10000
    precision = 0.001
    clauses, variables = sat_loader(ran_3sat(100,25))
    sim_an(clauses, variables)
    
   
    # with MyTimer():
    #     # clauses, variables = sat_loader(braun_edgs) 
    #     sid(clauses, variables, precision, t_max)
