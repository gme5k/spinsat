import itertools





class clause:
# input:
#     string                       name
#     list of variable objects     vars
#     list of integers {-1, 1}     edges
    
    def __init__(self, name, vars, edges):

        for edge in edges:
            assert edge == 1 or edge == -1, 'edge value can be 1 or -1'
            
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
            info.append([var.num, self.edgeDict[var], var.val])
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
            raise ValueError('At least one of the variables has no value.')

        

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
#     string     name
    
    def __init__(self, number):
        self.num = number
        self.val = None
        






x1 = variable(1)
x2 = variable(2)
x3 = variable(3)
x4 = variable(4)
x5 = variable(5)
x6 = variable(6)
x7 = variable(7)
x8 = variable(8)

c_z = clause('z', [x1, x2, x3, x4, x5, x6, x7], [-1,-1, -1, -1, -1, -1, -1])

#demonstrates classes functionality
print 'clause z SAT-table: \n', c_z.generateSATtable(), '\n'
# print 'clause z Variables: ', c_z.showVars(), '\n'
# print 'clause z Variable names: ', c_z.showVarNames(), '\n'
# print 'clause z Variable values: ', c_z.showVarVals(), '\n'
# print 'clause z K: ', c_z.showK(), '\n'
# print 'clause z edges: ', c_z.showEdges(), '\n'
# print 'clause z edge of variable x3: ', c_z.getEdge(x3)

# print 'name of variable x1: ', x1.showName()
# print 'value of variable x1: ', x1.showVal()



# Braunstein survey propogation paper Fig. 3
c_a = clause('a', [x1], [1])
c_b = clause('b', [x2], [-1])
c_c = clause('c', [x1, x2, x3], [-1, 1, 1])
c_d = clause('d', [x3, x4], [-1, 1])
c_e = clause('e', [x3, x5], [1, 1])
c_f = clause('f', [x4], [1])
c_g = clause('g', [x4, x7], [1, -1])
c_h = clause('h', [x5, x8], [1, 1])
c_i = clause('i', [x5, x6], [-1, 1])

clauses = [c_a, c_b, c_c, c_d, c_e, c_f, c_g, c_h, c_i]




for clause in clauses:
    print clause.info()
