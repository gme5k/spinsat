import os
import itertools
import random
import networkx
import matplotlib.pyplot as plt
import subprocess
import glob


  
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
        self.edges = edges
        self.name = name
        self.vars = vars
        self.K = len(vars)
        self.edgeDict = {}

        # combine variable objects and edges into key-value pairs
        for i in range(len(vars)):
            self.edgeDict[self.vars[i]] = self.edges[i]

            
    def info(self):
        info = []
        
        print self.name
        print 'var, edge, val'
        
        for var in self.vars:
            info.append([var.name, self.edgeDict[var], var.val])         
        return info

    
    def getEdge(self, var):
        return self.edgeDict[var]


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
    
    def __init__(self, name):
        self.type = 'v'
        self.name = name
        self.val = None


def WID(clauses, variables, tmax):
    
    WIDvars = []
    locFieldCount = {}

    # initialize the list containing all variables
    for var in variables:
        WIDvars.append(var)
    unfixedCount = len(WIDvars)
    WIDcycle = 0
   
   
    # plotGraph(clauses, variables, '0init')
    while unfixedCount > 0:
        
        locFieldCount[WIDcycle] = 0
        messages = warnProp(clauses, tmax)
        
        if messages == 'UN-CONVERGED':
            return 'UN-CONVERGED'

        # only run if warnProp converges
        else:
            edges = messages.keys()
            print >>f, '\nu*_a -> i'
        
            for i in messages:
                print >>f, i[0].name, i[1].name, messages[i]
    
            locFields = {}
            conNumbs = {}
            curVars = []

            # make list of variables contained in warnings
            for var in WIDvars:
                if var.val == None:
                    curVars.append(var)
                    
            print >>f, '\nusing these variables this WIDcycle: '
            for var in curVars:
                print >>f, var.name
            print >>f, '\nWIDcycle = ', WIDcycle, '\nN unfixed variables: '\
                , unfixedCount

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
        plotGraph(clauses, variables, WIDcycle)
        
    print >>f, '\nall variables assigned in: ', WIDcycle, 'cycles. \n'
    print >>f, 'local fields processed: '
    for entry in locFieldCount:
        print >>f, entry, locFieldCount[entry]
   
    return WIDvars




# input: shuffled order of edges, warnings, edge a i
# output: updated warning for edge a i
def wpUpdate(edges, messages, a, i):
    newVarWarn = 1
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
            newVarWarn *=  theta(cavFields[(j,a)] * a.getEdge(j))
    
    return newVarWarn
 



# input CNF graph and tmax
# output u*_a -> i
def warnProp(clauses, tmax):
    messages = {}
    oldVarWarns = {}
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
            oldVarWarns[(a,i)] = messages[(a,i)]
            
            # update varwarns with wpUpdate
       
            messages[(a,i)] = wpUpdate(edges, messages, a, i)
        convergence = 1
        
    
        for i in messages:
            print >>f,  "c_"+str(i[0].name), "v_"+str(i[1].name), messages[i]
        # check for convergence
        for message in messages:
            

            
            if messages[message] != oldVarWarns[message]:
                convergence = 0
       
        # if converged return warnings
        if convergence == 1:
            
            print >>f, '\nconverged in  t = ', t
            
            return messages

        # if not, and time is up, return uncovnerged
        elif t == tmax:
            return 'UNCONVERGED'
        t += 1
            


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
        clsVars = []
        possVarPicks = []
        edgeVals = []
        
        for var in variables:
            possVarPicks.append(var) 
       
        for j in range(random.randrange(kMin, kMax+1)):
            ranVar = random.choice(possVarPicks)
            clsVars.append(ranVar)
            possVarPicks.remove(ranVar)
            edgeVals.append(random.randrange(-1,2,2))
        clauses.append(Clause(clause, clsVars, edgeVals))
    return clauses, variables



def ranTree(kMin, kMax, cMin, cMax, vMin, vMax):
    print 'tree'
    clauses = []
    variables = []
  
    nVar = random.randint(vMin,vMax)
    nCls = random.randint(cMin,cMax)
    
    print  'nCls: ', nCls, 'nVar: ', nVar

    for i in range(nVar):
        variables.append(Variable(i))
   
    for clause in range(nCls):
    
        possVarPicks = []
        edgeVals = []
        x =  random.randrange(0, len(variables) + 1)
        print 'new clause, sampling x amount: ', x 
        clsVars = random.sample(variables, x)
        for i in clsVars:
            print i.name

        for i in clsVars:
            variables.remove(i)
       
        print 'vars left \n'
        for i in variables:
            print i.name


        
def plotGraph(clauses, variables, filename):
  
    G = networkx.Graph()
    
    G.clear()
    labels = {}
    
    for v in variables:
        G.add_node(v, s = 'o')
        labels[v] = 'V_'+str(v.name)+'\n'+str(v.val)

    for c in clauses:
        G.add_node(c, s = 's')
        labels[c] = 'C_'+str(c.name)
               
        for i in range(len(c.vars)):
            
            if c.edges[i] == -1:
                G.add_edge(c, c.vars[i], color = 'blue')
            
            else:  
                G.add_edge(c, c.vars[i], color = 'red')      
    colors = [G[u][v]['color'] for u,v in G.edges]
    nodeShapes = set((aShape[1]["s"] for aShape in G.nodes(data=True)))
    nodePos = networkx.shell_layout(G)

    for aShape in nodeShapes:
        networkx.draw_networkx_nodes(
            G, 
            nodePos,
            labels = labels,
            with_labels = True, 
            node_shape = aShape, 
            node_color = 'white',
            linewidths = 1,
            node_size = 200, 
            nodelist = [sNode[0] for sNode \
                        in filter(lambda x: x[1]["s"] == aShape, G.nodes(data=True))]
        )
    networkx.draw_networkx_edges(G, nodePos, edge_color = colors, width = 1, alpha = 0.5)
    networkx.draw_networkx_labels(G, nodePos, labels = labels, font_size = 5)
    plt.savefig('out/'+str(filename)+'.png', bbox_inches='tight', dpi = 100)
    plt.clf()
    
if __name__== "__main__":
    if os.path.exists("out/slideshow.avi"):
        os.remove("out/slideshow.avi")
        os.remove("out/output.txt")




    for pic in glob.glob("out\\*.png"):
        os.remove(pic)
    for pic in glob.glob("out\\resized\\*.png"):
        os.remove(pic)
    # subprocess.call(["rm","-f","out/*.png", ])
    # subprocess.call(["rm","-f","out/resized/*.png", ])
    f = open('out/output.txt','w')
    clauses, variables = ranGraph(3, 3, 20, 20, 5, 5 )   
    print >>f, WID(clauses, variables, 100)
    subprocess.call(["mogrify", "-path", "out/resized", "-resize", "1398x1060!", "out/*.png"])
    subprocess.call(["ffmpeg", "-r", "0.75", "-pattern_type", "glob", "-i", "out/resized/*.png", "-c:v", "copy", "out/slideshow.avi"])
    subprocess.call(["vlc","out/slideshow.avi"])
    
    




























    # Braunstein survey propogation paper Fig. 3
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
# fig3 = [c_a, c_b, c_c, c_d, c_e, c_f, c_g, c_h, c_i]
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
