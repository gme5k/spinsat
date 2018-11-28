import itertools
import random




class clause:
# input:
#     string                       name
#     list of variable objects     vars
#     list of integers {-1, 1}     edges
    
    def __init__(self, name, vars, edges):

        for edge in edges:
            
            assert edge == 1 or edge == -1, 'edge value has to be be 1 or -1'
            
        assert len(vars) == len(edges), 'no equal amount of variables & edges'
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
        
        # works if variables have values
        try:
            
            # calculate edge * value
            for var in self.vars:
                edgeValProducts.append(var.value * self.getEdge(var))
            sat = 1

            # sat = 0 if at least one variable satisfies clause, else sat = 2
            # [mezard K-SAT paper eq. 5]
            for i in edgeValProducts:
                sat *= (1 + i) / 2.0

                # if one variable satisfies, do not calculate others
                if sat == 0:
                    break
               
            return int(2 * sat)
        
        except:
            return 2

        
    def generateSATtable(self):
    # tries all combinations of var. values and prints sat. table
        
        table = []
        n = len(self.vars)
        
        # list of all combinations (also lists),  map() casts tuple to list
        valGrid =  map(list, itertools.product([-1, 1], repeat = n))
        
        for valSet in valGrid:

            # set var. values to generated values
            for i in range(len(valSet)):
                self.vars[i].value = valSet[i]
                
            
            table.append([valSet, self.checkSAT()])
       
        # return '0 = sat, 2 = unsat'
        print '0 = SAT, 2 = UNSAT'
        
        for entry in table:
            
            print entry
            
        return None


    
    
class variable:
# input
#     int     name
    
    def __init__(self, name):
        self.name = name
        self.val = None


def wid(fig, tmax):
    varsDone = []
    locFields = {}
    conNumbs = {}
    varWarns = warnProp(fig, tmax)
    
    
    edges = varWarns.keys()
    if varWarns == 'UN-CONVERGED':
        return 'UN-CONVERGED'
    
    else:
        
        for i in varWarns:
            print i[0].name, i[1].name, varWarns[i]

        # for every variable calculate local field and contradiction number
        for edge in edges:
           
            i = edge[1]
            a = edge[0]

            # to iterate over every variable, instead of  every edge
            if i not in varsDone:
                varsDone.append(i)
                
                print '\ncurVar: ', i.name
                
                locField = 0
                posEdgeVarWarnSum = 0
                negEdgeVarWarnSum = 0
                
                for edge in edges:
                    
                    if edge[1] == i and edge[0] != a:
                        b = edge[0]
                        edgeVal = b.getEdge(i)
                        locField += edgeVal * varWarns[(b, i)]
                        
                        print '    curClause', b.name
                        print '    cur locfield: ', locField
                        
                        if edgeVal == -1:
                            posEdgeVarWarnSum += varWarns[(b, i)]
                                    
                            print '     edgeVal: ', edgeVal, ' posEdgeVarWarn: '\
                                , varWarns[(b,i)]

                        elif edgeVal == 1:
                            negEdgeVarWarnSum += varWarns[(b, i)]
       
                            print '    edgeVal: ', edgeVal, ' posEdgeVarWarn: '\
                                , varWarns[(b,i)]

                    
                locFields[i] = -1 * locField
                
                print 'resulting locField: ', locFields[i]
                print 'pEVWS: ', posEdgeVarWarnSum, 'nEVWS: ', negEdgeVarWarnSum
                print 'product of posEVWS and negEVWS: ',\
                    posEdgeVarWarnSum * negEdgeVarWarnSum
             
                if posEdgeVarWarnSum * negEdgeVarWarnSum > 0:      
                    conNum = 1
                    
                else:
                    conNum = 0
                conNumbs[i] = conNum
                
                print 'resulting contradiction number: ', conNum
                
        print '\nlocal fields: '
        for i in locFields:
            print i.name, locFields[i]
        print '\ncontradiction numbers: '
        for i in conNumbs:
            print i.name, conNumbs[i]
        print '\n'

        for var in conNumbs:

            if conNumbs[var] != 0:
                return 'UNSAT'
            else:
                pass

        locFieldPresent = 0
        for var in varsDone:
                
            if locFields[var] > 0:
                locFieldPresnt = 1
                var.val = 1

            elif locFields[var] < 0:
                locFieldPresent = 1
                var.val = 0

            else:
                pass
            
        print 'checkSat: '

        if locFieldPresent == 1:
            
            for clause in fig:

                print clause.name, clause.checkSAT()

                if clause.checkSAT() == 0:
                    fig.remove(clause)

            for clause in fig:
                for var in clause.vars:
                    print 'clause', clause.name, 'varVal', var.val
                    if var.val != None:
                         print 'variable', var.name, 'removed from', clause.name
                         clause.vars.remove(var)
                       
        # else:
        #     for var in varsDone:
                

                
        print 'clauses left'
        for clause in fig:
            print clause.name
        print 'variable values: '
        for var in varsDone:
            print var.name, var.val
                
            
     #   if locFieldPresent == 0:
            
                
                

        
def wpUpdate(edges, varWarns, a, i):
    newVarWarn = 1
    cavFields = {}
    
    # find (j) element of V(a)\i, i.e. the other variables attached to (a)
    for edge in edges:

        # if any (j) exists, set sums of warnings u_b -> j to 0
        if edge[0] == a and edge[1] != i:

            print '    var (j) with matching clause to (a): ',edge[0].name,\
                edge[1].name
            
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
                    
                    print '        clause (b) with matching var to (j): ',\
                        edge[0].name, edge[1].name

                    # if edge value = -1 (solid line), add u_b -> j to
                    # sum of warnings from un-negated variables
                    if edgeVal == -1:
                        posEdgeVarWarnSum += varWarns[(b,j)]
                        
                        print '        edgeVal: ', edgeVal, ' posEdgeVarWarn: '\
                            , varWarns[(b,j)]

                    # else if edge value = 1 (dotted line), add u_b > j to
                    # sum of warnings from negated variables
                    elif edgeVal == 1:
                        
                        print  '        edgeVal: ', edgeVal, 'negEdgeVarWarn: ',\
                            varWarns[(b,j)]
                        
                        negEdgeVarWarnSum += varWarns[(b,j)]
            
            cavFields[(j,a)] = posEdgeVarWarnSum - negEdgeVarWarnSum
            newVarWarn *=  theta(cavFields[(j,a)] * a.getEdge(j))
        
            print '    sum of positive edge warnings: ', posEdgeVarWarnSum
            print '    sum of negative edge warnings: ', negEdgeVarWarnSum
            print '    resulting cavity field: ', cavFields[(j,a)]
            print '    current resulting cavity fields: \n'
            print '    variable (j), clause (a), cavity field (h_j -> a), J^a_j'
            for cavField in cavFields:
                print '   ', cavField[0].name, cavField[1].name,\
                    cavFields[cavField], cavField[1].getEdge(cavField[0])
            print '\n    current newVarWarn: ', newVarWarn
            
    print 'resulting newVarWarn: ', newVarWarn, '\n'
    
    return newVarWarn
 



def warnProp(clauses, tmax):
    varWarns = {}
    oldVarWarns = {}
    vars = []
    t = 0

    # generate random warnings u_a -> i, messages from clauses to variables AKA
    # varWarns
    for a in clauses:

        for i in a.vars:
            varWarns[(a, i)] = random.randint(0,1)
            
    print 'initial varWarns: \nclause (a), variable (i), warning (u_a -> i):'
    for varWarn in varWarns:
        print varWarn[0].name, varWarn[1].name, varWarns[varWarn]
      
    edges = varWarns.keys()
    
    while t < tmax:
        t += 1
        random.shuffle(edges)
        
        print '\nt = ', t
        print '\nedges order: '
        for edge in edges:
            print edge[0].name, edge[1].name
        print '\n'

        for edge in edges:
            i = edge[1]
            a = edge[0]
            
            print 'current edge (a) (i): ', edge[0].name, edge[1].name
            print 'varWarn: ', varWarns[(a,i)]
            
            oldVarWarns[(a,i)] = varWarns[(a,i)]
            varWarns[(a,i)] = wpUpdate(edges, varWarns, a, i)

        convergence = 1
        
        print 'oldVarWarns, varWarns'
        for varWarn in varWarns:
            print oldVarWarns[varWarn], varWarns[varWarn]
            
            if varWarns[varWarn] != oldVarWarns[varWarn]:
                
                print 'nope'
                
                convergence = 0
                
        if convergence == 1:
            
            print '\nconverged in  t = ', t, '\nfinal varWarns: '
            
            return varWarns
        
        elif t == tmax:
            return 'UNCONVERGED'

            


def theta(x):
    if x <= 0:
        return 0
    if x > 0:
        return 1



    
# Braunstein survey propogation paper Fig. 3
x1 = variable(1)
x2 = variable(2)
x3 = variable(3)
x4 = variable(4)
x5 = variable(5)
x6 = variable(6)
x7 = variable(7)
x8 = variable(8)
c_a = clause('a', [x1], [1])
c_b = clause('b', [x2], [-1])
c_c = clause('c', [x1, x2, x3], [-1, 1, 1])
c_d = clause('d', [x3, x4], [-1, 1])
c_e = clause('e', [x3, x5], [1, 1])
c_f = clause('f', [x4], [1])
c_g = clause('g', [x4, x7], [1, -1])
c_h = clause('h', [x5, x8], [1, 1])
c_i = clause('i', [x5, x6], [-1, 1])
fig3 = [c_a, c_b, c_c, c_d, c_e, c_f, c_g, c_h, c_i]

c_z = clause('z', [x1, x2, x3, x4, x5, x6, x7], [-1,-1, -1, -1, -1, -1, -1])




print 'clause z SAT-table: \n', c_z.generateSATtable(), '\n'
print 'fig. 3: '
for clause in fig3:
    print clause.info(), '\n'
print '\n', wid(fig3, 100)
