import numpy as np

def computeTightness(Ds):
    #print(Ds.shape)

    sumD = np.nansum(np.nansum(np.abs(Ds)))
    nPair = np.sum(np.sum(~np.isnan(Ds))) - np.trace(~np.isnan(Ds))
    if(nPair == 0):
        tightness = 0
    else:
        tightness = np.true_divide(sumD, nPair)
        
    return tightness

def computeClusterTightness(D, index):
    Ds = D[np.ix_(index, index)]
    tightness = computeTightness(Ds)
    return tightness