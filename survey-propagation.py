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

cavFieldsG = {}

def sid(clauses, variables, precision, t_max):
    cycle = 0
    vars_unfix = set()

    for var in variables:
        if var.val == None:
            vars_unfix.add(var)
    
    while len(vars_unfix) > 0:
      
        for c in clauses:
            print 'c', c.name
            for v in c.vars:
                print '    v',v.name
        print 'cycle', cycle
        print 'vars_unfix'
        for k in vars_unfix:
            print k.name
        messages =  sur_prop(clauses, t_max, precision)

        if messages == 'UN-CONVERGED':
            return 'UN-CONVERGED'
        
        else:
            trivial = True

            # check if messages trivial
            for message in messages.values():
                # print 'message', message

                if message > 0:
                    trivial = False
                    
            # for var in variables:
            #     if var.val == None:
            #         vars_unfix.add(var)
            #         print 'unfixed var', var.name, var.val
            print 'n unfixed vars', len(vars_unfix)
            if trivial == False:
               
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
                    w_plus = pi_plus / (pi_plus + pi_min + pi_0)
                    w_min = pi_min / (pi_plus + pi_min + pi_0)
                    w_0 = 1 - w_plus - w_min
                    variance.append((i, w_plus, w_min))
                variance.sort(key = lambda x: abs(x[1] - x[2]), reverse = True)

                print 'variance sorted'

                for k in variance:
                    print k[0].name, k[1], k[2], abs(k[1] - k[2])

                if variance[0][1] > variance[0][2]:
                    variance[0][0].val = 1
                    vars_unfix.remove(variance[0][0])
                    
                    print 'var', variance[0][0].name, 'val', variance[0][0].val

                else:
                    variance[0][0].val = -1
                    vars_unfix.remove(variance[0][0])
                    
                    print 'var', variance[0][0].name, 'val', variance[0][0].val

                print '\nsat check'
              
                # new_cls = set()
           
            else:
                print 'TRIVIAL'
                ran_var = random.choice(list(vars_unfix))
                ran_var.val =  random.randrange(-1, 2, 2)
                vars_unfix.remove(ran_var)
                
                print 'v', ran_var.name, 'val', ran_var.val
            plotGraph(clauses, variables, str(cycle), messages)
            decimate(clauses)
            
        cycle +=1
        
    return vars_unfix
                    
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
        for message in messages:
            # print 'c', message[0].name, 'v',message[1].name, 'new: ', messages\
            #     [message], 'old: ', oldMessages[message], 'diff: ',\
            #     abs(messages[message] - oldMessages[message]), 't= ', t
           
            if abs(messages[message] - oldMessages[message]) > precision:
                convergence = False
       
        # if converged return warnings
        if convergence == True:
            # print '\nconverged in  t = ', t
            
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

def decimate(clauses):
    for c in clauses.copy():
        if c.checkSAT() == 2:
            print '\nc', c.name, 'UNSAT'

            for v in c.vars:
                if v.val == None:
                    print 'v', v.name, v.val,

                elif v.val * c.getEdge(v) == 1:
                    print 'v', v.name, v.val, 'UNSAT'

                else:
                    c.remVar(v)
                    print 'removed v', v.name, 'from c', c.name
                    # new_cls.add(c)
        else:
            print '\nc', c.name, 'SAT'
            print 'removing c', c.name
            clauses.remove(c)
            for v in c.vars:
                print 'removing', c.name, 'from', v.name
                v.remCls(c)

class Clause:
    def __init__(self, name, vars):
        self.type = 'c'
        self.name = name
        self.vars = vars
        self.K = len(vars)

        # combine variable objects and edges into key-value pairs
    
    def getEdge(self, var):
            return self.vars[var]
        
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
    
    for i in cavFieldsG:
        
        print 'cavFieldsG entry: ', i[1].name, i[0].name, cavFieldsG[i]
        
   
        
    print 'plotgraph: messages'
    
    for key in messages:
        
        print key[0].name, key[1].name, messages[key]

    g = graphviz.Graph(format='png')
    g.graph_attr.update(ranksep='3')

    for v in variables:
        g.node('v '+str(v.name), 'v '+str(v.name)+'\n'+str(v.val),shape= 'circle')
    print 'plotgraph: cavity fields'
    for c in clauses:
        g.node('c '+str(c.name), shape= 'square')
        
        for var in c.vars:
           
            if  cavFieldsG.get((var, c)) != None:
               
                print 'c',c.name,'v', var.name, cavFieldsG[(var,c)]

                if c.getEdge(var) == -1:
                    g.edge('c ' + str(c.name), 'v '+str(var.name), color = 'blue', \
                               label = 'm'+str(messages[(c, var)])[:5]  + '\n' + \
                                'c'+str(cavFieldsG[(var, c)])[:5])

                else:  
                    g.edge('c ' + str(c.name), 'v '+str(var.name), color = 'red', \
                               label = 'm'+str(messages[(c,var)])[:5] + '\n' + \
                                'c'+str(cavFieldsG[(var, c)])[:5])
            else:
                print c.name, var.name, 'does not have a cavity field'

                if c.getEdge(var) == -1:
                    g.edge('c ' + str(c.name), 'v '+str(var.name), color = 'blue', \
                               label = str(messages[(c,var)])[:5])

                else:  
                    g.edge('c ' + str(c.name), 'v '+str(var.name), color = 'red', \
                               label = str(messages[(c,var)])[:5])              
    g.render('out/'+imgName+'.gv', view=True)  
if __name__== "__main__":
   
     
    t_max = 10000
    precision = 0.001
    clauses, variables = sat_loader(braun_edgs)
   
    with MyTimer():
        # clauses, variables = sat_loader(braun_edgs) 
        sid(clauses, variables, precision, t_max)
