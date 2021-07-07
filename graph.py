import pandas as pd
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
from experiment import Clause
from experiment import Variable
from experiment import sat_loader
import scipy
import graphviz
import dot2tex
import scipy.optimize as opt
import math


def test_func(x, a, b, c,d):
    return a * np.tanh(-b * x + c) + d

def poly(x, a, b, c, d):
    return a*x**3 + b*x**2 + c*x + d

def poly2(x, a, b, c):
    return a*x**2 + b*x + c
    

    
def color (r, g, b):
    r, g, b = r / 255. , g / 255. , b / 255.
    return (r, g, b)

G_RAT = (5**.5 - 1) / 2
PURPLE_B = color(144, 103, 167)
BLUE = color(57, 106, 177)
ORANGE = color(218, 124, 48)
GREEN = color(62, 150, 81)
RED = color(204,37,41)
BLUE_B = color(114, 147, 203)
ORANGE_B = color(225,151,76)
GREEN_B = color(132,186,91)
RED_B = color(211, 94, 96)
GRAY_B = color(128, 133, 133)
WIDTH = 433.69681
COLORS = [BLUE, ORANGE, GREEN, RED]
COLORS_B = [BLUE_B, ORANGE_B, GREEN_B, RED_B]
BRIGHT_GREEN = color(102, 255, 0)

BWIDTH = 0.01
BWIDTH_B = 0.5

COL_WIDTH = 236.84843

nice_fonts = {
        # Use LaTeX to write all text
        "text.usetex": True,
        "font.family": "serif",
        # Use 10pt font in plots, to match 10pt font in document
        "axes.labelsize": 10,
        "font.size": 10,
        # Make the legend/label fonts a little smaller
        "legend.fontsize": 8,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
}
mpl.rcParams.update(nice_fonts)

def time():
    with open("/home/timothy/spinsat/results/18-03_copy/50/merged/total.csv","r") as f:
        df = pd.read_csv(f, sep = ";")
    
    # use tex
        plt.rc('text', usetex=True)
        plt.rc('font', family='serif')

        sc_fig, (ax1) = plt.subplots(1, 1, sharex=True, sharey=True,
                                figsize = set_size(WIDTH))

        ax1.set_ylabel(r'$t(\mathrm{s})$')
        ax1.set_xlabel(r'$\alpha$')


        y1 = [df['t_sim'].loc[(df['alpha'] == x) & (df['n_v']==125)].sum() / df['id'].loc[(df['alpha'] == x) & (df['n_v']==125)].count() for x in pd.unique(df['alpha'])]
        y2 = [df['t_sim'].loc[(df['alpha'] == x) & (df['n_v']==250)].sum() / df['id'].loc[(df['alpha'] == x) & (df['n_v']==250)].count() for x in pd.unique(df['alpha'])]
        y3 = [df['t_sim'].loc[(df['alpha'] == x) & (df['n_v']==500)].sum() / df['id'].loc[(df['alpha'] == x) & (df['n_v']==500)].count() for x in pd.unique(df['alpha'])]
        y4 = [df['t_sim'].loc[(df['alpha'] == x) & (df['n_v']==1000)].sum() / df['id'].loc[(df['alpha'] == x) & (df['n_v']==1000)].count() for x in pd.unique(df['alpha'])]
        r1 = pd.unique(df['alpha'])

        ax1.scatter(r1, y1,marker= ".",
                color = BLUE,
                label = r'$N=125$')

        ax1.scatter(r1, y2,marker= ".",
                color = ORANGE,
                     label = r'$N=250$')

        ax1.scatter(r1, y3,marker= ".",
                color = GREEN,
                label = r'$N=500$')

        ax1.scatter(r1, y4,marker= ".",
                color = RED, 
                label = r'$N=1000$')
        y5 = y4[:37]
        y6 = y4[37:]
        r5= r1[:37]
        r6 = r1[37:]
        print r6
        params_125, params_covariance_125 = opt.curve_fit(poly, r1, y1)
        params_250,  params_covariance_250 = opt.curve_fit(poly, r1, y2)
        params_500, params_covariance_500 = opt.curve_fit(poly, r1, y3)
        params_1000a, params_covariance_1000a = opt.curve_fit(poly, r5, y5)
        params_1000b, params_covariance_1000b = opt.curve_fit(poly, r6, y6)

        ax1.plot(r1, poly(r1, params_125[0], params_125[1],params_125[2],params_125[3]), color=BLUE)
        ax1.plot(r1, poly(r1, params_250[0], params_250[1],params_250[2],params_250[3]), color=ORANGE)
        ax1.plot(r1, poly(r1, params_500[0], params_500[1],params_500[2],params_500[3]), color=GREEN)
        ax1.plot(r5, poly(r5, params_1000a[0], params_1000a[1],params_1000a[2],params_1000a[3]), color=RED)
        ax1.plot(r6, poly(r6, params_1000b[0], params_1000b[1],params_1000b[2],params_1000b[3]), color=RED)
        sc_fig_handles, sc_fig_labels = ax1.get_legend_handles_labels()
        sc_fig.legend(sc_fig_handles, sc_fig_labels, loc='upper right')
        sc_fig.savefig('figs/time.pdf', format='pdf', bbox_inches='tight')

def iters():
    with open("/home/timothy/spinsat/results/18-03_copy/50/merged/total.csv","r") as f:
        df = pd.read_csv(f, sep = ";")
    
    # use tex
        plt.rc('text', usetex=True)
        plt.rc('font', family='serif')

        sc_fig, (ax1) = plt.subplots(1, 1, sharex=True, sharey=True,
                                figsize = set_size(WIDTH))

        ax1.set_ylabel(r'$iterations$')
        ax1.set_xlabel(r'$\alpha$')


        y1 = [df['sur_prop_iters'].loc[(df['alpha'] == x) & (df['n_v']==125)].sum() / df['id'].loc[(df['alpha'] == x) & (df['n_v']==125)].count() for x in pd.unique(df['alpha'])]
        y2 = [df['sur_prop_iters'].loc[(df['alpha'] == x) & (df['n_v']==250)].sum() / df['id'].loc[(df['alpha'] == x) & (df['n_v']==250)].count() for x in pd.unique(df['alpha'])]
        y3 = [df['sur_prop_iters'].loc[(df['alpha'] == x) & (df['n_v']==500)].sum() / df['id'].loc[(df['alpha'] == x) & (df['n_v']==500)].count() for x in pd.unique(df['alpha'])]
        y4 = [df['sur_prop_iters'].loc[(df['alpha'] == x) & (df['n_v']==1000)].sum() / df['id'].loc[(df['alpha'] == x) & (df['n_v']==1000)].count() for x in pd.unique(df['alpha'])]
        r1 = pd.unique(df['alpha'])

        ax1.scatter(r1, y1,marker= ".",
                color = BLUE,
                label = r'$N=125$')

        ax1.scatter(r1, y2,marker= ".",
                color = ORANGE,
                     label = r'$N=250$')

        ax1.scatter(r1, y3,marker= ".",
                color = GREEN,
                label = r'$N=500$')

        ax1.scatter(r1, y4,marker= ".",
                color = RED, 
                label = r'$N=1000$')

        params_125, params_covariance_125 = opt.curve_fit(poly, r1, y1)
        params_250,  params_covariance_250 = opt.curve_fit(poly, r1, y2)
        params_500, params_covariance_500 = opt.curve_fit(poly, r1, y3)
        params_1000, params_covariance_1000 = opt.curve_fit(poly, r1, y4)

        ax1.plot(r1, poly(r1, params_125[0], params_125[1],params_125[2],params_125[3]), color=BLUE)
        ax1.plot(r1, poly(r1, params_250[0], params_250[1],params_250[2],params_250[3]), color=ORANGE)
        ax1.plot(r1, poly(r1, params_500[0], params_500[1],params_500[2],params_500[3]), color=GREEN)
        ax1.plot(r1, poly(r1, params_1000[0], params_1000[1],params_1000[2],params_1000[3]), color=RED)

        sc_fig_handles, sc_fig_labels = ax1.get_legend_handles_labels()
        sc_fig.legend(sc_fig_handles, sc_fig_labels, loc='upper right')
        sc_fig.savefig('figs/iters.pdf', format='pdf', bbox_inches='tight')


    
def sc_sim():        
    with open("/home/timothy/spinsat/results/18-03_copy/50/merged/total.csv","r") as f:
        df = pd.read_csv(f, sep = ";")
    
    # use tex
        plt.rc('text', usetex=True)
        plt.rc('font', family='serif')

        sc_fig, (ax1) = plt.subplots(1, 1, sharex=True, sharey=True,
                                figsize = set_size(WIDTH))

        ax1.set_ylabel(r'$f_{solved}$')
        ax1.set_xlabel(r'$\alpha$')

        sid125 = [df['id'].loc[(df['alpha'] == x) &
                              (df['result_sim']=='succesful')
                               & (df['n_v']==125)].count() 
                 / float(df['id'].loc[(df['alpha'] == x) & (df['n_v']==125)].count()) for x in pd.unique(df['alpha'])]
        sid250 = [df['id'].loc[(df['alpha'] == x) &
                              (df['result_sim']=='succesful')
                               & (df['n_v']==250)].count() 
                 / float(df['id'].loc[(df['alpha'] == x) & (df['n_v']==250)].count()) for x in pd.unique(df['alpha'])]
        sid500 = [df['id'].loc[(df['alpha'] == x) &
                              (df['result_sim']=='succesful')
                               & (df['n_v']==500)].count() 
                 / float(df['id'].loc[(df['alpha'] == x) & (df['n_v']==500)].count()) for x in pd.unique(df['alpha'])]
        sid1k = [df['id'].loc[(df['alpha'] == x) &
                              (df['result_sim']=='succesful')
                               & (df['n_v']==1000)].count() 
                 / float(df['id'].loc[(df['alpha'] == x) & (df['n_v']==1000)].count()) for x in pd.unique(df['alpha'])]

        r1 = pd.unique(df['alpha'])

        ax1.scatter(r1, sid125,marker= ".",
                color = BLUE,
                label = r'$N=125$')

        ax1.scatter(r1, sid250,marker= ".",
                color = ORANGE,
                     label = r'$N=250$')

        ax1.scatter(r1, sid500,marker= ".",
                color = GREEN,
                label = r'$N=500$')

        ax1.scatter(r1, sid1k,marker= ".",
                color = RED, 
                label = r'$N=1000$')

        sc_fig_handles, sc_fig_labels = ax1.get_legend_handles_labels()
        sc_fig.legend(sc_fig_handles, sc_fig_labels, loc='upper right')
        sc_fig.savefig('figs/sc_sim.pdf', format='pdf', bbox_inches='tight')

def sim_c():        
    with open("/home/timothy/spinsat/results/18-03_copy/50/merged/total.csv","r") as f:
        df = pd.read_csv(f, sep = ";")
    
    # use tex
        plt.rc('text', usetex=True)
        plt.rc('font', family='serif')

        c_fig, (ax1) = plt.subplots(1, 1, sharex=True, sharey=True,
                                figsize = set_size(WIDTH))

        ax1.set_ylabel(r'${M_{sat}}/M$')
        ax1.set_xlabel(r'$\alpha$')

        c_125=  [df['n_c_solved_sim'].loc[(df['alpha'] == x) & (df['n_v']==125)].sum() / float(df['n_c'].loc[(df['alpha'] == x) & (df['n_v']==125)].sum()) for x in pd.unique(df['alpha'])]
        c_250 = [df['n_c_solved_sim'].loc[(df['alpha'] == x) & (df['n_v']==250)].sum() / float(df['n_c'].loc[(df['alpha'] == x) & (df['n_v']==250)].sum()) for x in pd.unique(df['alpha'])]
        c_500 = [df['n_c_solved_sim'].loc[(df['alpha'] == x) & (df['n_v']==500)].sum() / float(df['n_c'].loc[(df['alpha'] == x) & (df['n_v']==500)].sum()) for x in pd.unique(df['alpha'])]
        c_1000= [df['n_c_solved_sim'].loc[(df['alpha'] == x) & (df['n_v']==1000)].sum() / float(df['n_c'].loc[(df['alpha'] == x) & (df['n_v']==1000)].sum()) for x in pd.unique(df['alpha'])]


        x_data = pd.unique(df['alpha'])

        ax1.scatter(x_data, c_125,marker= ".",
                color = BLUE,
                label = r'$N=125$')

        ax1.scatter(x_data, c_250,marker= ".",
                color = ORANGE,
                     label = r'$N=250$')

        ax1.scatter(x_data, c_500,marker= ".",
                color = GREEN,
                label = r'$N=500$')

        ax1.scatter(x_data, c_1000,marker= ".",
                color = RED, 
                label = r'$N=1000$')



        params_125, params_covariance_125 = opt.curve_fit(poly, x_data, c_125)
        params_250,  params_covariance_250 = opt.curve_fit(poly, x_data, c_250)
        params_500, params_covariance_500 = opt.curve_fit(poly, x_data, c_500)
        params_1000, params_covariance_1000 = opt.curve_fit(poly, x_data, c_1000)

        ax1.plot(x_data, poly(x_data, params_125[0], params_125[1],params_125[2],params_125[3]), color=BLUE)
        ax1.plot(x_data, poly(x_data, params_250[0], params_250[1],params_250[2],params_250[3]), color=ORANGE)
        ax1.plot(x_data, poly(x_data, params_500[0], params_500[1],params_500[2],params_500[3]), color=GREEN)
        ax1.plot(x_data, poly(x_data, params_1000[0], params_1000[1],params_1000[2],params_1000[3]), color=RED)


        c_fig_handles, c_fig_labels = ax1.get_legend_handles_labels()
        c_fig.legend(c_fig_handles, c_fig_labels, loc='upper right')
        c_fig.savefig('figs/c_sim.pdf', format='pdf', bbox_inches='tight')



def sc_sid():        
    with open("/home/timothy/spinsat/results/18-03_copy/50/merged/total.csv","r") as f:
        df = pd.read_csv(f, sep = ";")
    
    # use tex
        plt.rc('text', usetex=True)
        plt.rc('font', family='serif')

        sc_fig, (ax1) = plt.subplots(1, 1, sharex=True, sharey=True,
                                figsize = set_size(WIDTH))

        ax1.set_ylabel(r'$f_{solved}$')
        ax1.set_xlabel(r'$\alpha$')

        x_data = pd.unique(df['alpha'])


        y_125= [df['id'].loc[(df['alpha'] == x) &
                              (df['result_sid']=='succesful')
                               & (df['n_v']==125)].count() 
                 / float(df['id'].loc[(df['alpha'] == x) & (df['n_v']==125)].count()) for x in pd.unique(df['alpha'])]

        y_250 = [df['id'].loc[(df['alpha'] == x) &
                              (df['result_sid']=='succesful')
                               & (df['n_v']==250)].count() 
                 / float(df['id'].loc[(df['alpha'] == x) & (df['n_v']==250)].count()) for x in pd.unique(df['alpha'])]
        
        y_500 = [df['id'].loc[(df['alpha'] == x) &
                              (df['result_sid']=='succesful')
                               & (df['n_v']==500)].count() 
                 / float(df['id'].loc[(df['alpha'] == x) & (df['n_v']==500)].count()) for x in pd.unique(df['alpha'])]

        
        y_1000 = [df['id'].loc[(df['alpha'] == x) &
                              (df['result_sid']=='succesful')
                               & (df['n_v']==1000)].count() 
                 / float(df['id'].loc[(df['alpha'] == x) & (df['n_v']==1000)].count()) for x in pd.unique(df['alpha'])]
        
        x_data=pd.unique(df['alpha'])
    
        params_125, params_covariance_125 = opt.curve_fit(test_func, x_data, y_125)
        params_250,  params_covariance_250 = opt.curve_fit(test_func, x_data, y_250)
        params_500, params_covariance_500 = opt.curve_fit(test_func, x_data, y_500)
        params_1000, params_covariance_1000 = opt.curve_fit(test_func, x_data, y_1000)
        print params_1000


        ax1.scatter(x_data, y_125,marker= ".",
                color = BLUE,
                label = r'$N=125$')

        ax1.scatter(x_data, y_250,marker= ".",
                color = ORANGE,
                     label = r'$N=250$')

        ax1.scatter(x_data, y_500,marker= ".",
                color = GREEN,
                label = r'$N=500$')

        ax1.scatter(x_data, y_1000,marker= ".",
                color = RED, 
                label = r'$N=1000$')

        ax1.plot(x_data, test_func(x_data, params_125[0], params_125[1],params_125[2],params_125[3]), color=BLUE)
        ax1.plot(x_data, test_func(x_data, params_250[0], params_250[1],params_250[2],params_250[3]), color=ORANGE)
        ax1.plot(x_data, test_func(x_data, params_500[0], params_500[1],params_500[2],params_500[3]), color=GREEN)
        ax1.plot(x_data, test_func(x_data, params_1000[0], params_1000[1],params_1000[2],params_1000[3]), color=RED)

        sc_fig_handles, sc_fig_labels = ax1.get_legend_handles_labels()
        sc_fig.legend(sc_fig_handles, sc_fig_labels, loc='upper right')
        sc_fig.savefig('figs/sc_sid.pdf', format='pdf', bbox_inches='tight')


def con():        
    with open("/home/timothy/spinsat/results/18-03_copy/50/merged/total.csv","r") as f:
        df = pd.read_csv(f, sep = ";")
    
    # use tex
        plt.rc('text', usetex=True)
        plt.rc('font', family='serif')

        sc_fig, (ax1) = plt.subplots(1, 1, sharex=True, sharey=True,
                                figsize = set_size(WIDTH))

        ax1.set_ylabel(r'$f_{solved}$')
        ax1.set_xlabel(r'$\alpha$')

        x_data = pd.unique(df['alpha'])


        y_125= [df['id'].loc[(df['alpha'] == x) &
                              (df['result_sid']=='contradiction')
                               & (df['n_v']==125)].count() 
                 / float(df['id'].loc[(df['alpha'] == x) & (df['n_v']==125)].count()) for x in pd.unique(df['alpha'])]

        y_250 = [df['id'].loc[(df['alpha'] == x) &
                              (df['result_sid']=='contradiction')
                               & (df['n_v']==250)].count() 
                 / float(df['id'].loc[(df['alpha'] == x) & (df['n_v']==250)].count()) for x in pd.unique(df['alpha'])]
        
        y_500 = [df['id'].loc[(df['alpha'] == x) &
                              (df['result_sid']=='contradiction')
                               & (df['n_v']==500)].count() 
                 / float(df['id'].loc[(df['alpha'] == x) & (df['n_v']==500)].count()) for x in pd.unique(df['alpha'])]

        
        y_1000 = [df['id'].loc[(df['alpha'] == x) &
                              (df['result_sid']=='contradiction')
                               & (df['n_v']==1000)].count() 
                 / float(df['id'].loc[(df['alpha'] == x) & (df['n_v']==1000)].count()) for x in pd.unique(df['alpha'])]
        
        x_data=pd.unique(df['alpha'])
    
        params_125, params_covariance_125 = opt.curve_fit(test_func, x_data, y_125)
        params_250,  params_covariance_250 = opt.curve_fit(test_func, x_data, y_250)
        params_500, params_covariance_500 = opt.curve_fit(test_func, x_data, y_500)
        params_1000, params_covariance_1000 = opt.curve_fit(test_func, x_data, y_1000)
        print params_1000


        ax1.scatter(x_data, y_125,marker= ".",
                color = BLUE,
                label = r'$N=125$')

        ax1.scatter(x_data, y_250,marker= ".",
                color = ORANGE,
                     label = r'$N=250$')

        ax1.scatter(x_data, y_500,marker= ".",
                color = GREEN,
                label = r'$N=500$')

        ax1.scatter(x_data, y_1000,marker= ".",
                color = RED, 
                label = r'$N=1000$')

        ax1.plot(x_data, test_func(x_data, params_125[0], params_125[1],params_125[2],params_125[3]), color=BLUE)
        ax1.plot(x_data, test_func(x_data, params_250[0], params_250[1],params_250[2],params_250[3]), color=ORANGE)
        ax1.plot(x_data, test_func(x_data, params_500[0], params_500[1],params_500[2],params_500[3]), color=GREEN)
        ax1.plot(x_data, test_func(x_data, params_1000[0], params_1000[1],params_1000[2],params_1000[3]), color=RED)

        sc_fig_handles, sc_fig_labels = ax1.get_legend_handles_labels()
        sc_fig.legend(sc_fig_handles, sc_fig_labels, loc='upper right')
        sc_fig.savefig('figs/sc_sid.pdf', format='pdf', bbox_inches='tight')
def sim_an():
    with open("/home/timothy/spinsat/sim_an_data.csv", "r") as sim:
        plt.rc('text', usetex=True)
        plt.rc('font', family='serif')


        # # sim an exaple
        # df = pd.read_csv(sim, sep = ";")
         

        sim_fig, (ax1) =  plt.subplots(1, 1, sharex=True, sharey=True,
                            figsize = set_size(WIDTH / 2))
        ax1.set_ylabel(r'$P(T,\epsilon)$')
        ax1.set_xlabel(r'$T(t)$')


        def prob(x,  T):
            return (T/x)
        

        def lin_eq(x, b):
            return (b - x) / float(b)

        def expeq(x, T):
            if T !=0:
                return math.exp(-x/T)
            else:
                return 0
            
        
        T = [lin_eq(t, 100) for t in range(101)]
        y = [prob(1,  i) for i in T]
        y2 = [prob(3,  i) for i in T]
        y3 = [expeq(1, i) for i in T]
        y4 = [expeq(3, i) for i in T]
        


        ax1.plot(T,y, color=BLUE, label=r'$P_1,\quad \epsilon=1$')
        ax1.plot(T,y2,  color=ORANGE, label=r'$P_1,\quad \epsilon=3$')
        ax1.plot(T,y3, color=GREEN, label=r'$P_0,\quad  \epsilon=1$')
        ax1.plot(T,y4, color=RED, label=r'$P_0,\quad \epsilon=3$')
        sim_fig_handles, sim_fig_labels = ax1.get_legend_handles_labels()
        sim_fig.legend(sim_fig_handles, sim_fig_labels, loc=4, bbox_to_anchor=(0.5,0.7))
        sim_fig.savefig('figs/sim_an.pdf', format='pdf', bbox_inches='tight')

def main():
   
        

    with open("/home/timothy/spinsat/results/18-03_copy/50/merged/total.csv",\
              "r") as f:
   
        # show duplicates
        df = pd.read_csv(f, sep = ";")
       
        # dup = df[df.duplicated(subset='prob')]
        # print 'duplicates', dup

        # # show progesss
        # prog125 =  [(x, 125,  df['id'].loc[(df['alpha'] == x)
        #                                    & (df['n_v'] == 125)].count())
        #          for x in pd.unique(df['alpha'])]
        # prog250 =  [(x, 250, df['id'].loc[(df['alpha'] == x)
        #                                   & (df['n_v'] == 250)].count())
        #          for x in pd.unique(df['alpha'])]
        # prog500 =  [(x, 500, df['id'].loc[(df['alpha'] == x)
        #                                   & (df['n_v'] == 500)].count())
        #          for x in pd.unique(df['alpha'])]
        # prog1k =   [(x, 1000, df['id'].loc[(df['alpha'] == x)
        #                                    & (df['n_v'] == 1000)].count())
        #          for x in pd.unique(df['alpha'])]
        
        # inc = [x for x in prog125 + prog250 + prog500 + prog1k if x[2] != 50]
        # print 'inc', inc

    # use tex
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')



 
    # barchart
    bar_fig, (ax1) = plt.subplots(1, 1, sharex=True, sharey=True,
                            figsize = set_size(WIDTH))
    
    ax1.set_ylabel(r'$solved$ / $total$')
    ax1.set_xlabel(r'$\alpha$')
   
   
    
    # SID
    # sim_u =  [df['id'].loc[(df['alpha'] == x) &\
    #                       (df['result_sim']=='unsuccesful')].count() \
    #          / float(df['id'].loc[(df['alpha'] == x)].count())\
             # for x in pd.unique(df['alpha'])]
    # sim = [df['id'].loc[(df['alpha'] == x) &\
    #                       (df['result_sim']=='succesful')].count() \
    #          / float(df['id'].loc[(df['alpha'] == x)].count())\
    #          for x in pd.unique(df['alpha'])]
    sid125 = [df['id'].loc[(df['alpha'] == x) &
                          (df['result_sid']=='succesful')
                           & (df['n_v']==125)].count() 
             / float(df['id'].loc[(df['alpha'] == x) & (df['n_v']==125)].count()) for x in pd.unique(df['alpha'])]
    sid250 = [df['id'].loc[(df['alpha'] == x) &
                          (df['result_sid']=='succesful')
                           & (df['n_v']==250)].count() 
             / float(df['id'].loc[(df['alpha'] == x) & (df['n_v']==250)].count()) for x in pd.unique(df['alpha'])]
    sid500 = [df['id'].loc[(df['alpha'] == x) &
                          (df['result_sid']=='succesful')
                           & (df['n_v']==500)].count() 
             / float(df['id'].loc[(df['alpha'] == x) & (df['n_v']==500)].count()) for x in pd.unique(df['alpha'])]
    sid1k = [df['id'].loc[(df['alpha'] == x) &
                          (df['result_sid']=='succesful')
                           & (df['n_v']==1000)].count() 
             / float(df['id'].loc[(df['alpha'] == x) & (df['n_v']==1000)].count()) for x in pd.unique(df['alpha'])]
    #          for x in pd.unique(df['alpha'])]
    # sid_u = [df['id'].loc[(df['alpha'] == x) &
    #                       (df['result_sid']=='unconverged')].count() 
    #          / float(df['id'].loc[(df['alpha'] == x)].count())
    #          for x in pd.unique(df['alpha'])]
    # sid_c = [df['id'].loc[(df['alpha'] == x) &
    #                       (df['result_sid']=='contradiction')].count() 
    #          / float(df['id'].loc[(df['alpha'] == x)].count())
    #          for x in pd.unique(df['alpha'])]

    # sid_o = [df['id'].loc[(df['alpha'] == x) &
    #                       (df['result_sid']=='out of vars')].count() 
    #          / float(df['id'].loc[(df['alpha'] == x)].count())
    #          for x in pd.unique(df['alpha'])]

    every_nth = 5
    
   
    
    r1 = pd.unique(df['alpha'])
    r3 = [x  - 1 * BWIDTH for x in r1]
    # optimizedParameters, pcov = opt.curve_fit(func, r1, sid125);
    # optimizedParameters2, pcov2 = opt.curve_fit(func, r1, sid250);
    # optimizedParameters3, pcov3 = opt.curve_fit(func, r1, sid500);
    # optimizedParameters4, pcov4 = opt.curve_fit(func, r1, sid1k);
    ax1.set_xticks(r1)
    for n, label in enumerate(ax1.xaxis.get_ticklabels()):
        if n % every_nth != 0:
            label.set_visible(False)
    ax1.scatter(r1, sid125,marker= ".",
            color = BLUE,
            label = 'N=125')
    # ax1.plot(r1, func(r1, *optimizedParameters), label='fit')
    ax1.scatter(r1, sid250,marker= ".",
            color = ORANGE,
                 label = 'N=250')
    ax1.scatter(r1, sid500,marker= ".",
            color = GREEN,
            label = 'N=500')
    ax1.scatter(r1, sid1k,marker= ".",
            color = RED, 
            label = 'N=1000')
    # ax1.bar(r1, sim_u,
    #         color = GRAY_B, width = BWIDTH, linewidth = 0, label = 'SA unsuccesful', bottom = sim)


   
    # bar_sa_fig, (ax2) = plt.subplots(1, 1, sharex=True, sharey=True,
    #                         figsize = set_size(WIDTH))

    # ax2.bar(r1, sim,
    #         color = ORANGE_B, width = BWIDTH, linewidth = 0, label = 'SA succesful')
    
    # ax2.set_ylabel(r'$N_{solved}$ / ${N_{total}}$')
    # ax2.set_xlabel(r'$\alpha$')
    # SA
    # ax1.bar(pd.unique(df['alpha']),\
    #         [df['id'].loc[(df['alpha'] == x) &\
    #                       (df['result_sim']=='succesful')].count() \
    #          / float(df['id'].loc[(df['alpha'] == x)].count())\
    #          for x in pd.unique(df['alpha'])],\
    #         color = ORANGE, width = 0.01, linewidth = 0, label = 'SA')
    
    # legend
    bar_fig_handles, bar_fig_labels = ax1.get_legend_handles_labels()
    bar_fig.legend(bar_fig_handles, bar_fig_labels, loc='upper center')

    # alpha box plot 
    a_box, a_box_ax = plt.subplots(1, 1, figsize = set_size(WIDTH))
   
    # ax.scatter(pd.unique(df['alpha']),\
    #            [float(sum(df['n_c_solved_sim'].loc[(df['alpha'] == x)])) /
    #             sum(df['n_c'].loc[(df['alpha'] == x)])\
    #             for x in pd.unique(df['alpha'])], color = 'black')
    a_box_data  = [df['n_c_solved_sim'].loc[(df['alpha'] == x)] /
                df['n_c'].loc[(df['alpha'] == x)]
                   for x in pd.unique(df['alpha'])]
    a_box_plot = a_box_ax.boxplot(a_box_data, patch_artist=True)
    a_box_ax.set(xlabel = r'$\alpha$', ylabel = r'${M_{sat}}$ / $M$',
                 xticklabels = [round(x, 3) for x in pd.unique(df['alpha'])])
    for i, box in enumerate(a_box_plot['boxes']):
       
        # change outline color
        box.set( color= 'black')
        # change fill color
        box.set( facecolor = 'white')

    # change color and linewidth of the whiskers
    for whisker in a_box_plot['whiskers']:
       
        whisker.set(color = 'black')

    # change color and linewidth of the caps
    for cap in  a_box_plot['caps']:
        cap.set(color= 'black')

    # change color and linewidth of the medians
    for median in a_box_plot['medians']:
        median.set(color= 'black')

   
    for n, label in enumerate(a_box_ax.xaxis.get_ticklabels()):
        if n % 4 != 0:
            label.set_visible(False)
   

    
    # V boxplot
    box_fig, box_ax = plt.subplots(1, 1, figsize = set_size(WIDTH))
    box_data= [df['n_c_solved_sim'].loc[(df['n_v'] == x)] /\
               df['n_c'].loc[(df['n_v'] == x)] for x in [125, 250, 500, 1000]]
    box_plot =  box_ax.boxplot(box_data, patch_artist=True)
    box_ax.set(ylabel=r'$M_{sat}$ / $M$',
               xlabel=r'$N$',
               xticklabels = [r'$N = 125$',r'$N = 250$',r'$N = 500$',
                              r'$N = 1000$'])
    for i, box in enumerate(box_plot['boxes']):
       
        # change outline color
        box.set( color= 'black')
        # change fill color
        box.set( facecolor = 'white')

    # change color and linewidth of the whiskers
    for whisker in box_plot['whiskers']:
       
        whisker.set(color = 'black')

    # change color and linewidth of the caps
    for cap in  box_plot['caps']:
        cap.set(color= 'black')

    # change color and linewidth of the medians
    for median in box_plot['medians']:
        median.set(color= 'black')


def stack():

   

    with open("/home/timothy/spinsat/results/18-03_copy/50/merged/total.csv",\
              "r") as f:
        df = pd.read_csv(f, sep = ";")

        ind = pd.unique(df['alpha'])
        # V solved barchart 
        v_bar, v_ax = plt.subplots(1, 1, figsize = set_size(WIDTH))
    
        # ind2 = [x - BWIDTH_B for x in ind]
      
        sid_s = [df['id'].loc[(df['alpha'] == x)
                                 & (df['result_sid'] == 'succesful')].count()
                    / float(df['id'].loc[(df['alpha'] == x)].count())
                    for x in pd.unique(df['alpha'])]
        sid_u = [df['id'].loc[(df['alpha'] == x)
                                 & (df['result_sid'] == 'unconverged')].count()
                    / float(df['id'].loc[(df['alpha'] == x)].count())
                    for x in pd.unique(df['alpha'])]
        sid_c = [df['id'].loc[(df['alpha'] == x)
                                 & (df['result_sid'] == 'contradiction')].count()
                    / float(df['id'].loc[(df['alpha'] == x)].count())
                 for x in pd.unique(df['alpha'])]
        sid_o = [df['id'].loc[(df['alpha'] == x)
                                 & (df['result_sid'] == 'trivial')].count()
                    / float(df['id'].loc[(df['alpha'] == x)].count())
                    for x in pd.unique(df['alpha'])]


        v_ax.bar(ind, sid_s, color = GREEN_B, label = 'SID succesful', width = 0.01, linewidth = 0)
        v_ax.bar(ind, sid_u, color = ORANGE_B, label = 'Unconverged', width = 0.01, linewidth = 0, bottom = sid_s)
        v_ax.bar(ind, sid_c, color = RED_B, label = 'Contradiction', width = 0.01, linewidth = 0, bottom = [i+j for i,j in zip(sid_s, sid_u)])
        v_ax.bar(ind, sid_o, color = PURPLE_B, label = 'Trivial Messages', width = 0.01, linewidth = 0, bottom = [i+j+k for i,j,k in zip(sid_s, sid_u, sid_c)])

        v_ax.set_ylabel(r'$f_{result}$')
        v_ax.set_xlabel(r'$\alpha$')
        
        # v_ax.set(ylabel = r'$solved$ / $total$',
        #          xticks=ind , xticklabels=[r'$N=125$', r'$N=250$',
        #                                              r'$N=500$', r'$N=1000$'])



        v_bar_handles, v_bar_labels = v_ax.get_legend_handles_labels()
        v_bar.legend(v_bar_handles, v_bar_labels, loc='lower left22')
        v_bar.savefig('figs/stack.pdf', format='pdf', bbox_inches='tight')

        # bar_fig.savefig('figs/fig.pdf', format='pdf', bbox_inches='tight')
        # a_box.savefig('figs/fig2.pdf', format='pdf', bbox_inches='tight')
        # box_fig.savefig('figs/box.pdf', format='pdf', bbox_inches='tight')
        # v_bar.savefig('figs/sid.pdf', format='pdf', bbox_inches='tight')

def poop():
    # iterations/alpha barchart
    ita_bar, ita_ax = plt.subplots(1, 1, figsize = set_size(WIDTH))

    # succesful
    ita_s_data = [z_div(sum(df['sur_prop_iters']
                            .loc[(df['alpha'] == x)
                                 &(df['result_sid']=='succesful')]),
                        df['id'].loc[(df['alpha'] == x)
                                           & (df['result_sid'] == 'succesful')]
                              .count())
                  for x in [x for x in pd.unique(df['alpha'])]]

    # unconverged
    ita_u_data = [z_div(sum(df['sur_prop_iters']
                            .loc[(df['alpha'] == x)
                                 & (df['result_sid'] == 'unconverged')]),
                        df['id'].loc[(df['alpha'] == x)
                                           & (df['result_sid'] ==
                                              'unconverged')].count())
                  for x in  [x for x in pd.unique(df['alpha'])]]

    # contradiction
    ita_c_data = [z_div(sum(df['sur_prop_iters']
                            .loc[(df['alpha'] == x)
                                 & (df['result_sid']=='contradiction')]),
                        df['id']
                              .loc[(df['alpha'] == x)
                                   & (df['result_sid'] == 'contradiction')]
                              .count())
                  for x in  [x for x in pd.unique(df['alpha'])]]

    ita_t_data = [z_div(sum(df['sur_prop_iters']
                            .loc[(df['alpha'] == x)]),
                        df['id']
                              .loc[(df['alpha'] == x)]
                              .count())
                   for x in [x for x in pd.unique(df['alpha'])]]

    
    ita_ax.bar(pd.unique(df['alpha']), ita_u_data,  color = ORANGE_B,
               width = 0.01, linewidth = 0, label = 'unconverged'  )
    ita_ax.bar(pd.unique(df['alpha']), ita_c_data,  color = GREEN_B,
               width = 0.01, linewidth = 0,  label = 'contradiction')
    ita_ax.bar(pd.unique(df['alpha']), ita_s_data,  color = BLUE_B,
               width = 0.01, linewidth = 0, label = 'succesful')
    ita_ax.bar(pd.unique(df['alpha']), ita_t_data,  color = RED_B,
               width = 0.01, linewidth = 0, label = 'total')
   
    # ita_ax.bar(ind, sim_data, color = ORA, label = 'SA')

    ita_ax.set(ylabel = r'$iterations$', xlabel=r'$\alpha$')
    ita_bar_handles, ita_bar_labels = ita_ax.get_legend_handles_labels()
    ita_bar.legend(ita_bar_handles, ita_bar_labels, loc='upper center')


    # iterations/V barchart
    itv_bar, itv_ax = plt.subplots(1, 1, figsize = set_size(WIDTH))
    itv_s_data = [z_div(sum(df['sur_prop_iters']
                            .loc[(df['n_v'] == x)
                                 & (df['result_sid'] == 'succesful')]),
                        df['id']
                              .loc[(df['n_v'] == x)
                                   & (df['result_sid'] == 'succesful')].count())
                  for x in  [x for x in pd.unique(df['n_v'])]]
    itv_u_data = [z_div(sum(df['sur_prop_iters']
                            .loc[(df['n_v'] == x)
                                 & (df['result_sid'] == 'unconverged')]),
                        df['id'].loc[(df['n_v'] == x)
                                           & (df['result_sid'] == 'unconverged')]
                              .count())
                  for x in  [x for x in pd.unique(df['n_v'])]]
    
    itv_c_data = [z_div(sum(df['sur_prop_iters']
                            .loc[(df['n_v'] == x)
                                 & (df['result_sid'] == 'contradiction')]),
                       df['id']
                              .loc[(df['n_v'] == x)
                                   & (df['result_sid'] == 'contradiction')]
                              .count())
                  for x in  [x for x in pd.unique(df['n_v'])]]
    itv_t_data = [z_div(sum(df['sur_prop_iters']
                            .loc[(df['n_v'] == x)]),
                        df['id']
                              .loc[(df['n_v'] == x)]
                              .count())
                  for x in  [x for x in pd.unique(df['n_v'])]]


   
    itv_ax.bar(ind, itv_u_data,  color = ORANGE_B, width = .5, linewidth = 0,
               label = 'unconverged')
    itv_ax.bar(ind, itv_c_data,  color = GREEN_B, width = .5, linewidth = 0,
               label = 'contradiction')
    itv_ax.bar(ind, itv_s_data,  color = BLUE_B, width = .5, linewidth = 0,
               label='succesful')
    itv_ax.bar(ind, itv_t_data,  color = RED_B, width = .5, linewidth = 0,
                label='total')
    
    # itv_ax.bar(ind, itv_data,  color = 'black', width = .5, linewidth = 0)
    # itv_ax.bar(ind, sim_data, color = ORA, label = 'SA')

    itv_ax.set(ylabel = r'$iterations$', xlabel=r'$N$',
               xticks=[x + 0.5 * v_ax.patches[0].get_width() for x in ind],
               xticklabels=[r'$N=125$' , r'$N=250$', r'$N=500$', r'$N=1000$'])

    itv_bar_handles, itv_bar_labels = itv_ax.get_legend_handles_labels()
    itv_bar.legend(itv_bar_handles, itv_bar_labels, loc='upper center')
    # v_bar_handles, v_bar_labels = v_ax.get_legend_handles_labels()
    # v_bar.legend(v_bar_handles, v_bar_labels, loc='upper center')



    
    ita_bar.savefig('figs/ita.pdf', format='pdf', bbox_inches='tight')
    itv_bar.savefig('figs/itv.pdf', format='pdf', bbox_inches='tight')
    bar_fig.savefig('figs/fig.pdf', format='pdf', bbox_inches='tight')
    # bar_sa_fig.savefig('figs/fig3.pdf', format='pdf', bbox_inches='tight')
    a_box.savefig('figs/fig2.pdf', format='pdf', bbox_inches='tight')
    box_fig.savefig('figs/box.pdf', format='pdf', bbox_inches='tight')
    v_bar.savefig('figs/sid.pdf', format='pdf', bbox_inches='tight')


def set_size(width, fraction=1, subplots=(1, 1)):
    """ Set figure dimensions to avoid scaling in LaTeX.

    Parameters
    ----------
    width: float or string
            Document width in points, or string of predined document type
    fraction: float, optional
            Fraction of the width which you wish the figure to occupy
    subplots: array-like, optional
            The number of rows and columns of subplots.
    Returns
    -------
    fig_dim: tuple
            Dimensions of figure in inches
    """
    if width == 'thesis':
        width_pt = 426.79135
    elif width == 'beamer':
        width_pt = 307.28987
    elif width == 'pnas':
        width_pt = 246.09686
        
    else:
        width_pt = width

    # Width of figure (in pts)
    fig_width_pt = width_pt * fraction
    # Convert from pt to inches
    inches_per_pt = 1 / 72.27

    # Golden ratio to set aesthetic figure height
    # https://disq.us/p/2940ij3
    golden_ratio = (5**.5 - 1) / 2

    # Figure width in inches
    fig_width_in = fig_width_pt * inches_per_pt
    # Figure height in inches
   
    fig_height_in = fig_width_in * golden_ratio * (subplots[0] / subplots[1])
    print fig_width_in, fig_height_in
    return (fig_width_in, fig_height_in)

def z_div(n, d):
    return n / d if n else 0








def pretty_val(var):
    return "x_{" + str(var.name) + "}" if var.val == None  else "0" if var.val == -1 else  str(var.val)

    
def plotGraph(clauses, variables, img):
    # print 'plotgraph: printing cavity fields G'
    
    # for i in cavFieldsG:
        
        # print 'cavFieldsG entry: ', i[1].name, i[0].name, cavFieldsG[i]
        
   
        
    # print 'plotgraph: messages'
    
    # for key in messages:
        
    #     print key[0].name, key[1].name, messages[key]

    g = graphviz.Graph('G', filename='./figs/' + img + '.gv', engine='neato', format='pdf')
    # g.graph_attr.update(ranksep='equal')
    g.graph_attr.update(ratio=str(G_RAT))
    g.node_attr.update(fontsize='10')
    # g.node_attr.update(width='10', height = '102')
    g.graph_attr.update(size=str(set_size(WIDTH / 2)[0]))
    # +','+str(set_size(WIDTH / 2 - 50)[1 # 

    for v in sorted(list(variables), key= lambda x:x.name):
        g.node('v '+str(v.name), (pretty_val(v)),shape= 'circle')
    # print 'plotgraph: cavity fields'
    for c in sorted(list(clauses), key= lambda x:x.name):
        if c.checkSAT() == 2:
            
            g.node('c_{ ' + str(c.name) + '}'  , shape= 'square', color='black')
        else:
            
            g.node('c_{ ' + str(c.name) + '}'  , shape= 'square', color = gv_clr(BRIGHT_GREEN))
        
        # if c.checkSAT() == 2:
        for var in c.vars:

                # if  cavFieldsG.get((var, c)) != None:

                    # print 'c',c.name,'v', var.name, cavFieldsG[(var,c)]
          

            if var.val == None or c.getEdge(var) * var.val != -1:
                if c.getEdge(var) == -1:
                    # print 'c', c.name, 'v', var.name, 'e', c.getEdge(var), 'val', var.val, 'blue' # 23
                    g.edge('c_{ ' + str(c.name) + '}', 'v '+str(var.name) ,color='black')


                elif c.getEdge(var) == 1:
                    # print 'c', c.name, 'v', var.name, 'e', c.getEdge(var),'val', var.val, 'red'
                    g.edge('c_{ ' + str(c.name) + '}', 'v '+str(var.name), style = 'dashed', color = 'black')
                    
            else:
                if c.getEdge(var) == -1:
                    # print 'c', c.name, 'v', var.name, 'e', c.getEdge(var),'val', var.val, 'purple
                    
                    g.edge('c_{ ' + str(c.name) + '}', 'v '+str(var.name), color = gv_clr(BRIGHT_GREEN))
                   
                elif c.getEdge(var) == 1:
                      # print 'c', c.name, 'v', var.name, 'e', c.getEdge(var),'val', var.val, 'orange'
                  
                      g.edge('c_{ ' + str(c.name) + '}', 'v '+str(var.name),style = 'dashed' ,color = gv_clr(BRIGHT_GREEN))

                        
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
              

    
    g.render()
    # texcode = dot2tex.dot2tex(g, format='tikz', crop=True, usepdflatex=True, prog='neato', texmode='math', autosize=True, output='./thesis-stuff/testimg.tex')

def example_graph4(img):
    # print 'plotgraph: printing cavity fields G'
    
    # for i in cavFieldsG:
        
        # print 'cavFieldsG entry: ', i[1].name, i[0].name, cavFieldsG[i]
        
   
        
    # print 'plotgraph: messages'
    
    # for key in messages:
        
    #     print key[0].name, key[1].name, messages[key]

    g = graphviz.Digraph('G', filename='./figs/' + img + '.gv', engine='neato', format='pdf')
    # g.graph_attr.update(ranksep='equal')
   
    g.node_attr.update(fontsize='10')
    # g.node_attr.update(width='1012', height = '102')
    g.graph_attr.update(ratio=str(G_RAT), size=str(set_size(WIDTH/2)[0]) + ',' + str(set_size(WIDTH/2)[1]), orientation= 'landscape')
    g.graph_attr.update(orientation= 'landscape')
    # +','+str(set_size(WIDTH / 2 - 50)[1 # 

   
    g.node('j' ,shape= 'circle')
   
    # print 'plotgraph: cavity fields'
   
            
    g.node('a'  , shape= 'square', color='black')
    g.node('b'  , shape= 'square', color='black', label='abs')
    g.node('c'  , shape= 'square', color='black', label='abs')
    g.node('d'  , shape= 'square', color='black', label='abu')
    g.node('e'  , shape= 'square', color='black', label='abu')

    g.edge('a','j', color='black')

    g.edge('j','b', color='black')
    g.edge('j','c', color='black')
    g.edge('j','d', color='black', style = 'dashed')
    g.edge('j','e', color='black', style = 'dashed')

    g.render()


def example_graph6(img):
    # print 'plotgraph: printing cavity fields G'
    
    # for i in cavFieldsG:
        
        # print 'cavFieldsG entry: ', i[1].name, i[0].name, cavFieldsG[i]
        
   
        
    # print 'plotgraph: messages'
    
    # for key in messages:
        
    #     print key[0].name, key[1].name, messages[key]

    g = graphviz.Digraph('G', filename='./figs/' + img + '.gv', engine='neato', format='pdf')
    # g.graph_attr.update(ranksep='equal')
   
    g.node_attr.update(fontsize='10')
    # g.node_attr.update(width='1012', height = '102')
    g.graph_attr.update(ratio=str(G_RAT), size=str(set_size(WIDTH/2)[0]) + ',' + str(set_size(WIDTH/2)[1]), orientation= 'landscape')
    g.graph_attr.update(orientation= 'landscape')
    # +','+str(set_size(WIDTH / 2 - 50)[1 # 

    g.node('1' ,shape= 'circle', label='1')
    
   
    # print 'plotgraph: cavity fields'
   
            
    g.node('a'  , shape= 'square', color='black', label='a')
    g.node('b'  , shape= 'square', color='black', label='b')
    g.node('c'  , shape= 'square', color='black', label='c')
    g.edge('a','1', color='black', label='u_{a r 1}')
    g.edge('b','1', color='black', label='u_{b r 1}')
    g.edge('c','1', color='black', label='u_{c r 1}')
   

    g.render()
def example_graph3(img):
    # print 'plotgraph: printing cavity fields G'
    
    # for i in cavFieldsG:
        
        # print 'cavFieldsG entry: ', i[1].name, i[0].name, cavFieldsG[i]
        
   
        
    # print 'plotgraph: messages'
    
    # for key in messages:
        
    #     print key[0].name, key[1].name, messages[key]

    g = graphviz.Graph('G', filename='./figs/' + img + '.gv', engine='neato', format='pdf')
    # g.graph_attr.update(ranksep='equal')
   
    g.node_attr.update(fontsize='10')
    # g.node_attr.update(width='1012', height = '102')
    # g.graph_attr.update(ratio=str(G_RAT), size=str(set_size(WIDTH/1.5)[0]) + ',' + str(set_size(WIDTH/1.5)[1]), orientation= 'landscape')
    g.graph_attr.update(orientation= 'landscape')
    # +','+str(set_size(WIDTH / 2 - 50)[1 # 

    g.node('i' ,shape= 'circle')
    g.node('j' ,shape= 'circle')
   
    # print 'plotgraph: cavity fields'
   
            
    g.node('a'  , shape= 'square', color='black')
    g.node('b'  , shape= 'square', color='black', label='nV_a^s(j)')
    g.node('c'  , shape= 'square', color='black', label='nV_a^s(j)')
    g.node('d'  , shape= 'square', color='black', label='nV_a^u(j)')
    g.node('e'  , shape= 'square', color='black', label='nV_a^u(j)')

    g.edge('i','a', color='black')
    g.edge('a','j', color='black')

    g.edge('j','b', color='black')
    g.edge('j','c', color='black')
    g.edge('j','d', color='black', style = 'dashed')
    g.edge('j','e', color='black', style = 'dashed')

    g.render()
def example_graph2(img):
    # print 'plotgraph: printing cavity fields G'
    
    # for i in cavFieldsG:
        
        # print 'cavFieldsG entry: ', i[1].name, i[0].name, cavFieldsG[i]
        
   
        
    # print 'plotgraph: messages'
    
    # for key in messages:
        
    #     print key[0].name, key[1].name, messages[key]

    g = graphviz.Graph('G', filename='./figs/' + img + '.gv', engine='neato', format='pdf')
    # g.graph_attr.update(ranksep='equal')
   
    g.node_attr.update(fontsize='10')
    # g.node_attr.update(width='1012', height = '102')
    # g.graph_attr.update(ratio=str(G_RAT), size=str(set_size(WIDTH/1.5)[0]) + ',' + str(set_size(WIDTH/1.5)[1]), orientation= 'landscape')
    g.graph_attr.update(orientation= 'landscape')
    # +','+str(set_size(WIDTH / 2 - 50)[1 # 

    g.node('i' ,shape= 'circle')
    g.node('j_1' ,shape= 'circle')
    g.node('j_2' ,shape= 'circle')
    # print 'plotgraph: cavity fields'
   
            
    g.node('a'  , shape= 'square', color='black')
    g.node('b_1'  , shape= 'square', color='black')
    g.node('b_2'  , shape= 'square', color='black')
    g.node('b_3'  , shape= 'square', color='black')
    g.node('b_4'  , shape= 'square', color='black')

    g.edge('j_1','a', color='black', label = 'u_{h1a}')
    g.edge('j_2','a' ,style='dashed',color='black', label = 'h_{2a}' )
    g.edge('a','i', color='black', label = 'u_{abc}')
    
    g.edge('b_1','j_1' ,color='black',style='dashed', label='1')
    g.edge('b_2','j_1' ,color='black', label='1')
    g.edge('b_3','j_2' ,color='black', label='0')
    g.edge('b_4','j_2' ,color='black', label='1')

    g.render()


def example_graph(img):
    # print 'plotgraph: printing cavity fields G'
    
    # for i in cavFieldsG:
        
        # print 'cavFieldsG entry: ', i[1].name, i[0].name, cavFieldsG[i]
        
   
        
    # print 'plotgraph: messages'
    
    # for key in messages:
        
    #     print key[0].name, key[1].name, messages[key]

    g = graphviz.Digraph('G', filename='./figs/' + img + '.gv', engine='neato', format='pdf')
    # g.graph_attr.update(ranksep='equal')
   
    g.node_attr.update(fontsize='10')
    # g.node_attr.update(width='1012', height = '102')
    # g.graph_attr.update(ratio=str(G_RAT), size=str(set_size(WIDTH/2)[0]) + ',' + str(set_size(WIDTH/2)[1]), orientation= 'landscape')
    g.graph_attr.update(orientation= 'landscape')
    # +','+str(set_size(WIDTH / 2 - 50)[1 # 

    g.node('s_0' ,shape= 'circle')
    g.node('s_a^1' ,shape= 'circle')
    g.node('s_a^2' ,shape= 'circle')
    # print 'plotgraph: cavity fields'
   
            
    g.node('a'  , shape= 'square', color='black')
    g.node('b'  , shape= 'square', color='black')
    g.node('c'  , shape= 'square', color='black')
    g.node('d'  , shape= 'square', color='black')
    g.node('e'  , shape= 'square', color='black')


    
    g.edge('s_a^1','a', color='black', label='h_{s_a^1 r a}')
    g.edge('s_a^2','a', color='black', label='h_{s_a^2 r a}')
    g.edge('a','s_0', color='black', label='u_{a r s_0}')
    
    g.edge('b','s_a^1' ,color='black', label=r'u_{b r i}')
    g.edge('c','s_a^1' ,color='black', label=r'u_{c r i}')
    g.edge('d','s_a^2' ,color='black', label=r'u_{d r i}')
    g.edge('e','s_a^2' ,color='black', label=r'u_{e r i}')

    g.render()
   
# braun_edgs = {
#     (1, 1) : 1, (1, 2) : -1, (1, 3) : -1,
#     (2, 1) : -1, (2, 2) : 1, (2, 3) : -1,
#      (3, 1) : -1, (3, 2) : -1, (3, 3) : 1,
# (4, 1) : 1, (4, 2) : 1, (4, 3) : 1
# }

# clauses, variables = sat_loader(braun_edgs)
# for c in sorted(list(clauses), key= lambda x:x.name):
#     print c.name

# def gv_clr(clr):
#     return '#{:02x}{:02x}{:02x}'.format(int(clr[0] * 255), int(clr[1] * 255), int(clr[2] * 255))



# plotGraph(clauses, variables, 'a_graph')

# for v in sorted(list(variables), key= lambda x:x.name):
#     if v.name == 1:
#         v.val = 1
#     if v.name == 3:
#         v.val = 1
#     if v.name == 2:
#         v.val = -1
# plotGraph(clauses, variables, 'b_graph')


# plotGraph
# # main()
# # sc_sim()
# sc_sid()
# sc_sim()
# sim_c()
# iters()
# time()
# stack()
example_graph6('loc')
