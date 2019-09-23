import os
import itertools
import random
import networkx
import matplotlib.pyplot as plt
import subprocess
import shutil
import math
import multiprocessing
import numpy
import graphviz

cavFieldsG = {}

class Clause:
# input:
#     string                       name
#     list of variable objects     vars
#     list of integers {-1, 1}     edges
    
    def __init__(self, name, vars, edges):

        for edge in edges:
            
            assert edge == 1 or edge == -1, 'edge value has to be be 1 or -1'
            
        assert len(vars) == len(edges), 'no equal amount of variables & edges'
        self.type = 'c'
        self.name = name
        self.vars = vars
        self.K = len(vars)
        self.edges = {}

        # combine variable objects and edges into key-value pairs
        for i in range(len(vars)):
            self.edges[vars[i]] = edges[i]
            
    def info(self):
        info = []
        
        print self.name
        print 'var, edge, val'
        
        for var in self.vars:
            info.append([var.name, self.edges[var], var.val])         
        return info

    
    def getEdge(self, var):
        return self.edges[var]

    def addVar(self, var):
        self.vars.append(var)
        self.K += 1
        self.edges[vars] = var.getEdge(self)
        
    def checkSAT(self):
    # check if variables satisfy clause, returns 0 (SAT) or 2 (UNSAT)

        # products of edge values {-1, 1}, and variable values {-1, 1}
        edgeValProducts = []
        
            
        # calculate edge * value
        empty = True 
        for var in self.vars:
            
            if var.val != None:
                empty = False
                edgeValProducts.append(var.val * self.getEdge(var))

                if var.val * self.getEdge(var) == -1:
                    print >>f, 'variable: ', var.name, 'SAT'
                else:
                    print >>f, 'variable: ', var.name, 'UNSAT' 

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
        
            
    def generateSATtable(self):
    # tries all combinations of var. values and prints sat. table
        
        table = []
        n = len(self.vars)
        
        # list of all combinations (also lists),  map() casts tuple to list
        valGrid =  map(list, itertools.product([-1, 1], repeat = n))
        
        for valSet in valGrid:

            # set var. values to generated values
            for i in range(len(valSet)):
                self.vars[i].val = valSet[i]

            table.append([valSet, self.checkSAT()])
       
        # return '0 = sat, 2 = unsat'
        print '0 = SAT, 2 = UNSAT'
        
        for entry in table:
            
            print entry
            
        return None

 
    
class Variable:
# input
#     int     name
    
    def __init__(self, name, clauses, edges):
        
        for edge in edges:
            
            assert edge == 1 or edge == -1, 'edge value has to be be 1 or -1'
            
        assert len(clauses) == len(edges), 'no equal amount of clauses & edges'

        self.type = 'v'
        self.name = name
        self.val = None
        self.clauses = clauses
        self.K = len(clauses)
        self.edges = {}

        # combine variable objects and edges into key-value pairs
        for i in range(len(clauses)):
            self.edges[clauses[i]] = edges[i]

    def getEdge(self, clause):
        return self.edges[clause]
    
    def addClause(self, clause):
        self.clauses.append(clause)
        self.K += 1
        self.edges[clause] = clause.getEdge(self)
        


        
def belResults(clauses, variables, precision):
    messages =  belProp(clauses, 10000, precision)
    belVars = []
    probs = []
    edges = messages.keys()
        
    print 'variables'
    
    for i in variables:
        
        print 'i', i.name
        
        negProd = 1.
        posProd = 1.
        
        for edge in edges:
            
            if edge[1] == i:
                a = edge[0]
                
                print 'a', a.name
                
                if a.getEdge(i) == 1:
                    negProd *= (1 - messages[(a, i)])
                    
                elif a.getEdge(i) == -1:
                    posProd *= (1 - messages[(a, i)])
       
            
  
        if negProd != 0:   
            probTrue = negProd / (negProd + posProd)
            
        else:
            probTrue = 0
            
        probs.append([i.name, probTrue])
        
   

    # calculate entropy and N
    cSum = 0.
    
    for a in clauses:
        tendency_1 = 1.
        tendency_2 = 1.
        print '\n clause: ', a.name
        
        for i in a.vars:
            edgeVal_a_i = a.getEdge(i)
            tendSat = 1.
            tendUnsat = 1.
            
            print '\n variable', i.name
            
            for edge in edges:
               
                # find b
                if edge[1] == i and edge[0] != a:
                
                    b = edge[0]
                    edgeVal_b_i =  b.getEdge(i)
                    
                    if edgeVal_b_i == edgeVal_a_i:
                        tendSat *= (1.0 - messages[(b,i)])
                      
                    elif edgeVal_b_i == -1 * edgeVal_a_i:
                        tendUnsat *= (1.0 - messages[(b,i)])
                       
                    print 'tendSat',tendSat
                    print 'tendUnsat',tendUnsat
            tendency_1 *= (tendSat + tendUnsat)
           
            tendency_2 *= tendUnsat
            print 'tend1', tendency_1, 'tend2', tendency_2
        tendSum = tendency_1 - tendency_2
        print 'tendSum', tendSum
        if tendSum > 0:
            cSum += numpy.log(tendSum)
    print 'cSum', cSum

    vSum = 0.
    for i in variables:
        print 'variable: ', i.name
        posProd = 1.0
        negProd = 1.0
        n_i = 0
      
        for edge in edges:

            if edge[1] == i:
                b = edge[0]
                n_i += 1
                edgeVal_b_i = b.getEdge(i)
                
                if edgeVal_b_i == -1:
                 
                    posProd *= (1.0 - messages[(b, i)])
              
                elif edgeVal_b_i == 1:
                    negProd *= (1.0 - messages[(b, i)])
        prodSum = posProd + negProd
        lnSum = numpy.log(prodSum)
        
        print 'prodSum', prodSum
        print 'lnSum', lnSum
        print 'degree', n_i
        
        vSum += ((1 - n_i) * lnSum)
        
        print 'vSum', vSum
        
    entropy = cSum + vSum
    nStates = 2**len(variables)
    nSatStates = numpy.exp(entropy)
    fracSat = nSatStates / nStates
    
    print >>f, 'entropy: ', entropy, 'nSATStates: ', nSatStates, 'nStates: ',\
        nStates, 'fracSat: ', fracSat
    print 'entropy: ', entropy, 'nSATStates: ', nSatStates, 'nStates: ',\
        nStates, 'fracSat: ', fracSat

    print 'probability var is True '
    for i in range(len(probs)):
        
        print >>f, probs[i]
        print probs[i]
        
        variables[i].val = round(probs[i][1], 2)
    plotGraph(clauses, variables, 'belProp', messages)
    
def belProp(clauses, tmax, precision):
    messages = {}
    oldMessages = {}
    vars = []
    t = 0
   
    # generate random messages u_a -> i, messages from clauses to variables
    for a in clauses:

        for i in a.vars:
            messages[(a, i)] = float(random.randint(0,1))

    print '\ninitial u_a - > i: '
    print 'clause, variable, message value'
    for message in messages:
        print "c_"+str(message[0].name), "v_"+str(message[1].name), messages[message]

    edges = messages.keys()
    t += 1
    
    # while t < tmax, iterate over every edge in a random fashion and update
    # warnings sequntially using the wpUpdate routine
    while t < tmax:
      
        random.shuffle(edges)
        
        print >>f, '\nt = ', t

        for edge in edges:
            i = edge[1]
            a = edge[0]

            # store old messages in similar dictionary as messages
            oldMessages[(a,i)] = messages[(a,i)]
            
            # update messages with bpUpdate        
            messages[(a,i)]  = bpUpdate(edges, messages, a, i)
        convergence = True

        # check for convergence
        for message in messages:

            print 'c', message[0].name, 'v',message[1].name, 'new: ', messages\
                [message], 'old: ', oldMessages[message], 'diff: ',\
                abs(messages[message] - oldMessages[message]), 't= ', t
           
            if abs(messages[message] - oldMessages[message]) > precision:
                convergence = False
       
        # if converged return warnings
        if convergence == True:
            
            print >>f, '\nconverged in  t = ', t
            
            return messages

        # if not, and time is up, return uncovnerged
        elif t == tmax:
            return 'UNCONVERGED'
        t += 1
    
# input: shuffled order of edges, warnings, edge a i
# output: updated warning for edge a i
def bpUpdate(edges, messages, a, i):
    print 'a, i', a.name, i.name
    newMessage = 1.0
    cavFields = {}
 
    for var in a.vars:
        prob_u = 1.
        prob_s = 1.
        
        if var != i:
            j = var
            edgeVal_a_j = a.getEdge(j)

            print '    a, j', a.name, j.name

            for clause in j.clauses:
                
                if clause != a:
                    b = clause
                    edgeVal_b_j = j.getEdge(b)

                    print '        b, j', b.name, j.name
                        
                    # if b element of V^s_a(j) multiply prob_s by
                    # (1 - message value)
                    if edgeVal_a_j == edgeVal_b_j:
                        prob_u *= (1. - messages[(b, j)])
                        
                        print '    prob_u', prob_u
                     
                    # else if b element of V^u_a(j), multiply prob_u by
                    # (1 - message value)
                    elif edgeVal_a_j == -1. * edgeVal_b_j:
                        prob_s *= (1. - messages[(b, j)])
                        
                        print '    prob_s', prob_s
     
            # store cavity field and update new warning
            print 'j = ', j.name
            
            if prob_u != 0.:
                cavFields[(j,a)] = prob_u / (prob_u + prob_s)

            elif prob_u == 0.:
                cavFields[(j,a)] = 0.
                
            print 'appending to cavfieldsG in bpUpdate'
            cavFieldsG[(j,a)] = cavFields[(j,a)]
                
            print '    cav', a.name, j.name, cavFields[(j,a)], '\n'

#####################################################3
            #schrodinger's print statement
            
            for k in cavFieldsG:
                print "cavfieldsG"    
                print k, cavFieldsG[k]
                ########################c###########
            newMessage *=  cavFields[(j,a)]
   
    
    return newMessage
        
        
def WID(plot, clauses, variables, tmax):
    WIDvars = []
    locFieldCount = {}

    # initialize the list containing all variables
    for var in variables:
        WIDvars.append(var)
    unfixedCount = len(WIDvars)
    WIDcycle = 0
    
    if plot == 0:
        plotGraph(clauses, variables, '0000')
        
    while unfixedCount > 0:
        
        locFieldCount[WIDcycle] = 0
      
        messages = warnProp(clauses, tmax)
      
        
        if messages == 'UN-CONVERGED':
            return 'UN-CONVERGED'

        # only run if wp converges
        else:
            edges = messages.keys()
            print >>f, '\nu*_a -> i'
        
            for i in messages:
                print >>f, i[0].name, i[1].name, messages[i]
    
            locFields = {}
            conNumbs = {}
            curVars = []

            # make list of unassignedd variables 
            for var in WIDvars:
                if var.val == None:
                    curVars.append(var)
                    
            print >>f, '\nusing these variables this WIDcycle: '
            for var in curVars:
                print >>f, var.name
            print >>f, '\nWIDcycle = ', WIDcycle, '\nN unfixed variables: '\
                , unfixedCount
            print WIDcycle
            # for every variable calculate local field and contradiction number
            for i in curVars:
                
                # print >>f, 'current variable: ', i.name
                locField = 0
                posEdgeVarWarnSum = 0
                negEdgeVarWarnSum = 0
                   
                # look for b's and update local field from corresponding
                # warnings
                for edge in edges:
                    
                    # if b, add to LF, PEVWS, NEVWS
                    if edge[1] == i:
                       
                        b = edge[0]
                        edgeVal = b.getEdge(i)
                        warning = messages[(b, i)]
                        locField += (edgeVal * warning)

                        # part of math for contradiction numbers
                        if edgeVal == -1:
                            posEdgeVarWarnSum += warning

                       
                        elif edgeVal == 1:
                            negEdgeVarWarnSum += warning

                           
                # store local field in dictionary
                locFields[i] = -1 *  locField

                 # calculate contradiction number
                if posEdgeVarWarnSum * negEdgeVarWarnSum > 0:      
                    conNum = 1

                else:
                    conNum = 0
                conNumbs[i] = conNum

            print >>f, '\nlocal fields: '
            for i in locFields:
                print >>f, i.name, locFields[i]
            print >>f, '\ncontradiction numbers: '
            for i in conNumbs:
                print >>f, i.name, conNumbs[i]
            print >>f, '\n'

            # check if fig is UNSAT with contradiction numbers
            for var in conNumbs:

                if conNumbs[var] != 0:
                    print 'UNSAT'
                    return 'UNSAT'
                else:
                    pass

            # check for local fields, set variable values according to
            # local fields
            locFieldPresent = False
    
            for var in curVars:

                if locFields[var] > 0:
                    locFieldCount[WIDcycle] += 1
                    locFieldPresent = True
                    var.val = 1
                    unfixedCount -= 1

                elif locFields[var] < 0:
                    locFieldCount[WIDcycle] += 1
                    locFieldPresent = True
                    var.val = -1
                    unfixedCount -= 1

                else:
                    pass

            if locFieldPresent == True: 
                print >>f, 'variables after taking into account local fields: '
                for var in curVars: 
                    print >>f, 'var: ', var.name, 'val: ', var.val

            # if no local fields, set random var to random var value
            if locFieldPresent ==  False:
               
                ranVar = random.choice(curVars)
                ranVal = random.randrange(-1, 2, 2)
                ranVar.val = ranVal
                print >>f, 'no local fields, doing something random'
                print >>f, ranVar.name, ranVal
                unfixedCount -= 1
            
            # clean figure

            print >>f, '\ncleaning . . . \n'
            
            newFig = []
            
            for clause in clauses:
                
                print >>f, 'clause: ', clause.name

                # if not SAT
                if clause.checkSAT() == 2:
                    newVars = []
                    
                    for var in clause.vars:

                        # if variable unassigned
                        if var.val == None:
                            
                            print >>f, 'clause: ', clause.name, 'variable: ',\
                                 var.name, var.val,

                            # keep var
                            newVars.append(var)

                        # else if variable does not satisfy clause
                        elif var.val * clause.getEdge(var) == 1:

                            # keep var
                            newVars.append(var)
                            
                            print >>f, 'clause: ', clause.name, 'variable: ',\
                                var.name, 'UNSAT'

                        # else if variable satisfies clause, do not keep var
                        else:
                            
                             print >>f, 'clause: ', clause.name, 'variable: ',\
                                 var.name, 'SAT'
                             
                             print >>f, 'removed var: ', var.name, 'from clause: '\
                                 , clause.name
        
                       
                    print >>f, 'newVars: '
                    for var in newVars:
                        print >>f, var.name
                    clause.vars = newVars
                    newFig.append(clause)
                else:
                    print >>f, 'removed clause: ', clause.name
            clauses = newFig
            print >>f, 'newFig: '
            for clause in newFig:
                print >>f, clause.name
                for var in clause.vars:
                    print >>f, '    ', var.name
            print >>f, '\nvariable values: '
            for var in WIDvars:
                print >>f, var.name, var.val
                
        WIDcycle += 1
        imgName = (4  - len(str(WIDcycle))) * '0' + str(WIDcycle)
       
        if plot == 0:
            print 'image', imgName
            plotGraph(clauses, variables, imgName)
        
    print >>f, '\nall variables assigned in: ', WIDcycle, 'cycles. \n'
    print >>f, 'local fields processed: '
    for entry in locFieldCount:
        print >>f, entry, locFieldCount[entry]
   
    if plot == 0:
        WIDcycle +=1
        imgName = (4  - len(str(WIDcycle))) * '0' + str(WIDcycle)
        plotGraph(clauses, variables, imgName)
    return WIDvars




        
# input CNF graph and tmax
# output u*_a -> i
def warnProp(clauses, tmax):
    messages = {}
    oldMessages = {}
    vars = []
    t = 0

    # generate random messages u_a -> i, messages from clauses to variables
    for a in clauses:

        for i in a.vars:
            messages[(a, i)] = random.randint(0,1)
 
    print >>f, '\ninitial u_a - > i: '
    print >>f, 'clause, variable, message value'
    for message in messages:
        print >>f, "c_"+str(message[0].name), "v_"+str(message[1].name), messages[message]

    edges = messages.keys()
    t += 1
    
    # while t < tmax, iterate over every edge in a random fashion and update
    # warnings sequntially using the wpUpdate routine
    while t < tmax:
      
        random.shuffle(edges)
        
        print >>f, '\nt = ', t

        for edge in edges:
            i = edge[1]
            a = edge[0]

            # store old warnings in similar dictionary to messages
            oldMessages[(a,i)] = messages[(a,i)]
            
            # update varwarns with wpUpdate
       
            messages[(a,i)] = wpUpdate(edges, messages, a, i)
        convergence = True
        
        for i in messages:
            print >>f,  "c_"+str(i[0].name), "v_"+str(i[1].name), messages[i]
            
        # check for convergence
        for message in messages:
        
            if messages[message] != oldMessages[message]:
                convergence = False
       
        # if converged return warnings
        if convergence == True:
            
            print >>f, '\nconverged in  t = ', t
            
            return messages

        # if not, and time is up, return uncovnerged
        elif t == tmax:
            return 'UNCONVERGED'
        t += 1
            
        

# input: shuffled order of edges, warnings, edge a i
# output: updated warning for edge a i
def wpUpdate(edges, messages, a, i):
    newMessage = 1
    cavFields = {}
    
    # find (j) element of V(a)\i, i.e. the other variables attached to (a)
    for edge in edges:

        # if any (j) exists, set sums of warnings u_b -> j to 0
        if edge[0] == a and edge[1] != i:

            # print >>f, '    var (j) with matching clause to (a): ',edge[0].name,\
            #     edge[1].name
            
            j = edge[1]
            posEdgeVarWarnSum = 0
            negEdgeVarWarnSum = 0
            
            # compute cavity fields h_j -> a, messages from variables to clauses
            for edge in edges:

                # find (b) element of V(j)\a, i.e. the other clauses besides (a)
                # attached to (j)
                if edge[1] == j and edge[0] != a:
                    b = edge[0]
                    edgeVal = b.getEdge(j)
                    
                    # print >>f, '        clause (b) with matching var to (j): ',\
                    #     edge[0].name, edge[1].name

                    # if edge value = -1 (solid line), add u_b -> j to
                    # sum of warnings from un-negated variables
                    if edgeVal == -1:
                        posEdgeVarWarnSum += messages[(b,j)]
                        
                        # print >>f, '        edgeVal: ', edgeVal, ' posEdgeVarWarn: '\
                        #     , messages[(b,j)]

                    # else if edge value = 1 (dotted line), add u_b > j to
                    # sum of warnings from negated variables
                    elif edgeVal == 1:
                        
                        # print >>f,  '        edgeVal: ', edgeVal, 'negEdgeVarWarn: ',\
                        #     messages[(b,j)]
                        
                        negEdgeVarWarnSum += messages[(b,j)]
                        
            # store cavity field and update new warning
            cavFields[(j,a)] = posEdgeVarWarnSum - negEdgeVarWarnSum
            newMessage *=  theta(cavFields[(j,a)] * a.getEdge(j))
    
    return newMessage



def theta(x):
    if x <= 0:
        return 0
    if x > 0:
        return 1



def ranGraph(kMin, kMax, cMin, cMax, vMin, vMax):
    
    clauses = []
    variables = []
  
    nVar = random.randint(vMin,vMax)
    nCls = random.randint(cMin,cMax)
    
    print >>f, 'nCls: ', nCls, 'nVar: ', nVar

    for i in range(nVar):
        variables.append(Variable(i))
   
    for clause in range(nCls):
        edgeVals = []
        ranVars = random.sample(variables, random.randrange(kMin, kMax + 1))
        
        for ranVar in ranVars:
            edgeVals.append(random.randrange(-1,2,2))
            # edgeVals.append(-1)
        clauses.append(Clause(clause, ranVars, edgeVals))
        
    print >>f, 'c, v, e'
    
    for clause in clauses:
        for var in clause.vars:
            
            print >>f,  clause.name, var.name, clause.getEdge(var)
        
    return clauses, variables

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
                               label = str(messages[(c, var)])[:5]  + '\n' + \
                                str(cavFieldsG[(var, c)])[:5])

                else:  
                    g.edge('c ' + str(c.name), 'v '+str(var.name), color = 'red', \
                               label = str(messages[(c,var)])[:5] + '\n' + \
                                str(cavFieldsG[(var, c)])[:5])
            else:
                print c.name, var.name, 'does not have a cavity field'

                if c.getEdge(var) == -1:
                    g.edge('c ' + str(c.name), 'v '+str(var.name), color = 'blue', \
                               label = str(messages[(c,var)])[:5])

                else:  
                    g.edge('c ' + str(c.name), 'v '+str(var.name), color = 'red', \
                               label = str(messages[(c,var)])[:5])              
    g.render('out/'+imgName+'.gv', view=True)  
# def plotGraph(clauses, variables, imgName): 
  
#     G = networkx.Graph()
#     G.clear()
#     labels = {}
    
#     for v in variables:
#         G.add_node(v, s = 'o')
#         labels[v] = 'V_'+str(v.name)+'\n'+str(v.val)

#     for c in clauses:
#         G.add_node(c, s = 's')
#         labels[c] = 'C_'+str(c.name)
               
#         for i in range(len(c.vars)):
            
#             if c.edges[i] == -1:
#                 G.add_edge(c, c.vars[i], color = 'blue')
            
#             else:  
#                 G.add_edge(c, c.vars[i], color = 'red')
#     colors = [G[u][v]['color'] for u,v in G.edges]
#     nodeShapes = set((aShape[1]["s"] for aShape in G.nodes(data=True)))
#     nodePos = networkx.kamada_kawai_layout(G)

#     for aShape in nodeShapes:
#         networkx.draw_networkx_nodes(
#             G, 
#             nodePos,
#             labels = labels,
#             with_labels = True, 
#             node_shape = aShape, 
#             node_color = 'white',
#             linewidths = 0.1,
#             node_size = 10, 
#             nodelist = [sNode[0] for sNode \
#                         in filter(lambda x: x[1]["s"] == aShape, G.nodes(data=True))]
#         )
#     networkx.draw_networkx_edges(G, nodePos, edge_color = colors, width = 0.1, alpha = 0.5)
#     networkx.draw_networkx_labels(G, nodePos, labels = labels, font_size = 1)
#     print 'name in plotGraph', imgName
#     plt.savefig('out/'+imgName+'.png', bbox_inches='tight', dpi = 700)
#     plt.clf()





# Braunstein survey propogation paper Fig. 3
braunVars = [Variable(1, [], []),Variable(2, [], []), Variable(3, [], []), Variable(4, [], []), Variable(5, [], []), \
            Variable(6, [], []), Variable(7, [], []), Variable(8, [], [])]

braunClauses = [Clause(1, [braunVars[0]], [-1]), Clause(2, [braunVars[1]], [1]), \
                Clause(3, [braunVars[0], braunVars[1], braunVars[2]], [1, -1, -1]), Clause(4, [braunVars[2], braunVars[3]], [1, -1]), \
                Clause(5, [braunVars[2], braunVars[4]], [-1, -1]), Clause(6, [braunVars[3]], [-1]), \
                Clause(7, [braunVars[3], braunVars[6]], [-1, 1]), Clause(8, [braunVars[4], braunVars[7]], [-1, -1]), \
                Clause(9, [braunVars[4], braunVars[5]], [1, -1])]

for var in braunVars:
    for clause in braunClauses:
        if var in clause.vars:

         
       
            var.addClause(clause)
            # print 'added', clause.name, 'to', var.name

# for clause in braunClauses:
#     print 'c', clause.name
#     for var in clause.vars:
#         print '    v', var.name
#         print '    e', clause.getEdge(var)

# for var in braunVars:
#     print 'v', var.name
#     for clause in var.clauses:
#         print '    c', clause.name
#         print '    e', var.getEdge(clause)


# print braunClauses[0].getEdge(braunVars[0])
# print 'name c', braunClauses[0].name
# print 'name v', braunVars[0].name

# print braunVars[0].getEdge(braunClauses[0])
if __name__== "__main__":
 
    shutil.rmtree('out')
    os.mkdir('out')
    os.mkdir('out/resized')
    f = open('out/output.txt','w')
    clauses = braunClauses
    variables = braunVars
    # clauses, variables = ranGraph(1, 2, 2, 2, 2, 2)
    # x1 = Variable(1)
    # x2 = Variable(2)
    # x3 = Variable(3)
    # x4 = Variable(4)
    # x5 = Variable(5)
    # x6 = Variable(6)
    # x7 = Variable(7)
    # x8 = Variable(8)
    # c_a = Clause(1, [x1], [-1])
    # c_b = Clause(2, [x2], [1])
    # c_c = Clause(3, [x1, x2, x3], [1, -1, -1])
    # c_d = Clause(4, [x3, x4], [1, -1])
    # c_e = Clause(5, [x3, x5], [-1, -1])
    # c_f = Clause(6, [x4], [-1])
    # c_g = Clause(7, [x4, x7], [-1, 1])
    # c_h = Clause(8, [x5, x8], [-1, -1])
    # c_i = Clause(9, [x5, x6], [1, -1])
  
    print >>f, belResults(clauses, variables, 0.000001)
    # print >>f, WID(0, clauses, variables, 100)
    # subprocess.call(["mogrify", "-path", "out/resized", "-resize", "1920x1060", "out/*.png"])
    # subprocess.call(["ffmpeg", "-r", "0.75", "-pattern_type", "glob", "-i", "out/resized/*.png", "-c:v", "copy", "out/slideshow.avi"])
   

    








#16:13



















# c_z = Clause('z', [x1, x2, x3, x4, x5, x6, x7], [-1,-1, -1, -1, -1, -1, -1])
#print 'clause z SAT-table: \n', c_z.generateSATtable(), '\n'
#print 'fig. 3: '
#for clause in fig3:
#    print clause.info(), '\n'


# print WID(fig3, 100)         
# 0 and 1 are opposite
# # -1 and 1 are opposite


 # x1 = Variable(1)
 #    x2 = Variable(2)
 #    x3 = Variable(3)

 #    c_a = Clause(1, [x1, x2], [-1, 1])
 #    c_b = Clause(2, [x2, x3], [-1, 1])
 #    c_c = Clause(3, [x3, x1], [-1, -1])




 


# def clsPicker(nVar, nCls, varSamples):
   
#     nVarClssTot = 0
#     nVarClssDic = {}
    
#     for var in varSamples:
#         nVarClss = random.randrange(0, nCls + 1)
#         print 'nVarClss', nVarClss
#         nVarClssDic[var.name] = nVarClss
#         print 'nVarClssDic', nVarClssDic
#         nVarClssTot += nVarClss
#         print 'nVarClssTot',nVarClssTot 

#         if nVarClssTot > nCls:
#             clsPicker(nVar, nCls, varSamples)
#             print 'too many total clauses'
#     else:
    
#         return nVarClssDic
        
        

# def ranTree(kMin, kMax, cMin, cMax, vMin, vMax):

    
#     clauses = []
#     variables = []
#     possLevelVarPicks = []
#     nVar = random.randint(vMin,vMax)
#     nCls = random.randint(cMin,cMax)
#     word = True
#     curClauses = []
#     print 'Nvars', nVar
#     print 'Nclss', nCls
#     print 'K', kMin, kMax
    
#     # generate number of connections
#     print 'vSplits'
#     while word == True:
#         varSplits = []
#         for i in range(nVar):
#             varSplits.append(random.randrange(0, 3))
#         print sum(varSplits), nCls-1
#         if sum(varSplits) == nCls-1:
#             break
#     print 'varSplits',  varSplits
    
#     print 'clssplits'
    
#     while word == True:
#         clsSplits = []
#         for i in range(nCls):
#             clsSplits.append(random.randrange(kMin - 1, kMax))
#         print sum(clsSplits), nVar
#         if sum(clsSplits) == nVar:
#             break
#     print clsSplits

#     print  'nCls: ', nCls, 'nVar: ', nVar
    
#     for i in range(nVar):
#         variables.append(Variable(i))
        
#     for var in variables:
#         possLevelVarPicks.append(var)
        
#     varSplitCount = 0
#     clsSplitCount = 0
#     while clsSplitCount < nVar - 3:
#     # init 1st clause
#         clauses.append(Clause(0,[],[]))
#         for clause in clauses:
#             curClauses.append(clause)

       
#         nClsLeft = nCls - 1
#         nLevelVars = []
#         print 'should be empty', nLevelVars

#         # first clause 
#         if clsSplitCount == 0:
#             nLevelVars.append(random.randrange(kMin,kMax+1))
#             clsSplitCount +=1

#         else:
#             for clause in curClauses: 
#                 nLevelVars.append(clsSplits[clsSplitCount - 1])
#                 clsSplitCount += 1

#         curVars = []

#         for i in range(len(curClauses)):
#             clauseVars = []
#             print 'i', i

#             print 'curclause', curClauses[i].name

#             for n in range(nLevelVars[i]):
#                 print 'n', n

#                 curClauses[i].vars.append(possLevelVarPicks[i])
#                 curVars.append(possLevelVarPicks[i])
#                 print 'appended', possLevelVarPicks[i].name, 'to', curClauses[i].name
#                 possLevelVarPicks.remove(possLevelVarPicks[i])
#                 curClauses[i].edges.append(random.randrange(-1,2,2))

#         # update clauses
#         for curclause in curClauses:
            
#             for clause in clauses:
                
#                 if clause.name == curclause.name:
#                     clause.vars = curclause.vars
#                     clause.edges = curclause.edges
                    
#         print 'curvars'
#         for i in curVars:
#             print i.name
            
#         curClauses = []
#         nLevelClsTot = 0
#         nLevelCls = []
        
#         print 'should be empty', nLevelCls

#         for var in curVars:
#             nLevelCls.append(varSplits[varSplitCount])
#             varSplitCount +=1
            
#         print 'nLevelClsTot'
#         for i in nLevelCls:
#             print i
#         print 'nLevelCls', nLevelCls


#         for i in range(len(curVars)):
#             varsCls = []
#             print 'i', i
#             print 'curVar', curVars[i].name


#             for n in range(nLevelCls[i]):

#                 print 'n ', n
#                 print 'clsSplitCount', clsSplitCount
#                 print 'clauses'
#                 for clause in clauses:
#                     print clause.name

#                 clauses.append(Clause(clsSplitCount, [],[])) #new generate clauses
#                 print 'clause generated', clauses[clsSplitCount].name

#                 clauses[clsSplitCount].vars.append(curVars[i])
#                 print 'appended', curVars[i].name, 'to', clauses[clsSplitCount].name

#                 curClauses.append(clauses[clsSplitCount])
#                 clauses[clsSplitCount].edges.append(random.randrange(-1,2,2))
#                 clsSplitCount += 1 
#     return clauses, variables
