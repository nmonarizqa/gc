'''
    File name: dicesimulation.py
    Author: Nurvirta Monarizqa
    Date created: 10/30/2016
    Python Version: 2.7
'''

import pandas as pd
import numpy as np
from math import factorial

def main():
    dice_sum = 24
    n = 8
    Z = pd.DataFrame(dist(dice_sum,n))
    expctd_val,std = calc(Z,n)
    print "Expected value N=%i M=%i is %f" %(n,dice_sum,expctd_val)
    print "Standard deviation N=%i M=%i is %f" %(n,dice_sum,std)

def dist(dice_sum,n):
    bound = [6]*n
    if not dice_sum:
        pass
    elif len(bound) == 1:
        if bound[0] >= dice_sum:
            yield (dice_sum,)
    else:
        for first_die in range(min(dice_sum, bound[0]), -1, -1):
            sum_other = dice_sum - first_die
            for dist_other in dist(sum_other, n-1):
                if dist_other[0] <= first_die:
                    yield (first_die,) + dist_other

def calc(df,nx):
    df['prod'] = df.product(axis=1)
    df['mat'] = pd.Series()
    for i in range(len(df)):
        div = 1
        buff = df.ix[i][0]
        ct = 1
        for j in range(1,nx):
            if df.ix[i][j]==buff:
                ct +=1
            else:
                div *= factorial(ct)
                buff = df.ix[i][j]
                ct = 1
        div *= factorial(ct)
        df['mat'][i] = div
    df['ncomb'] = factorial(nx)/df['mat']
    df['sigma'] = df['prod']*df.ncomb
    expctd_val = df.sigma.sum()/df.ncomb.sum()
    df['chi'] = ((df['prod']-expctd_val)**2 * df.ncomb)/df.ncomb.sum()
    prod_std = np.sqrt(df.chi.sum())
    return expctd_val,prod_std

if __name__ == '__main__':
    main()
