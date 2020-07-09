from sklearn.cluster import AgglomerativeClustering
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster

from .computeClusterTightness import *
from .cluster import *

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

import numpy as np

class Clustering(object):
    condition = 'New'
    def __init__(self, data):
        self.data = data
    def load_data(self):
        self.condition = 'Used'
    def calculate_pdist(self):
        self.D = squareform(pdist(self.data, nanEucFun))
    def calculate_linkage(self):
        self.li = linkage(self.D, method='ward')
    def calculate_random_tightness(self):
        nRows = D.shape[0]
    def calculate_principal_components(self):
        Dnorm = StandardScaler().fit_transform(self.D)
        pca = PCA(n_components=2)
        self.principalComponents = pca.fit_transform(Dnorm)
    def initiate_clustering(self):
        #dm = pdist(self.data, nanEucFun)
        #li = linkage(dm, method='ward')
        self.calculate_pdist()
        self.calculate_linkage()
        
        clustering = fcluster(self.li, 1, criterion = 'maxclust')

        root = Cluster()
        root.ClusterIndex = 1
        root.ParentIndex = None
        root.SampleIndices = clustering == 1
        root.ClusterTightness = computeClusterTightness(self.D, root.SampleIndices)
        root.ClusterSize = sum(root.SampleIndices)

        self.calculate_principal_components()
        principalComponents = self.principalComponents
        allClusters = []
        allClusters.append(root)
        allClusterSize = 1
        numSplit = 20
        for i in range(2, numSplit+1):
            clustering = fcluster(self.li, i, criterion = 'maxclust')
            clusterIndexing = findRootChildClusters(allClusters, clustering)

            iRoot = clusterIndexing.Root
            iCluster1 = clusterIndexing.Cluster1
            iCluster2 = clusterIndexing.Cluster2

            #print(clusterIndexing)

            C1 = Cluster()
            C1.ClusterIndex = allClusterSize + 1
            C1.ParentIndex = iRoot
            C1.SampleIndices = clustering == iCluster1
            C1.ClusterTightness = computeClusterTightness(self.D, C1.SampleIndices)
            C1.ClusterSize = sum(C1.SampleIndices)

            C2 = Cluster()
            C2.ClusterIndex = allClusterSize + 2
            C2.ParentIndex = iRoot
            C2.SampleIndices = clustering == iCluster2
            C2.ClusterTightness = computeClusterTightness(self.D, C2.SampleIndices)
            C2.ClusterSize = sum(C2.SampleIndices)

            allClusters.append(C1)
            allClusters.append(C2)
            allClusterSize = allClusterSize + 2
            #print(i)
        
       
        leftChildren = np.zeros(len(allClusters), dtype=int)
        rightChildren = np.zeros(len(allClusters), dtype=int)
        
        for iCluster in range(1, len(allClusters)):
            index = allClusters[iCluster].ClusterIndex
            parent = allClusters[iCluster].ParentIndex - 1
            tightness = allClusters[iCluster].ClusterTightness
            if(leftChildren[parent] == 0):
                leftChildren[parent] = index
            else:
                tightnessPrev = allClusters[leftChildren[parent]].ClusterTightness
                if(tightness > tightnessPrev):
                    rightChildren[parent] = leftChildren[parent]
                    leftChildren[parent] = index
                else:
                    rightChildren[parent] = index

        for iCluster in range(0, len(allClusters)):
            allClusters[iCluster].LeftChild = leftChildren[iCluster]
            allClusters[iCluster].RightChild = rightChildren[iCluster]
            allClusters[iCluster].ClusterWeight = \
                100 * allClusters[iCluster].ClusterSize / root.ClusterSize
            allClusters[iCluster].Component1Mean = \
                np.mean(principalComponents[allClusters[iCluster].SampleIndices, 0])
            allClusters[iCluster].Component2Mean = \
                np.mean(principalComponents[allClusters[iCluster].SampleIndices, 1])
            # allClusters[iCluster].ClusterTightness = \
            #     allClusters[iCluster].ClusterTightness * \
            #     allClusters[iCluster].ClusterSize / root.ClusterSize

        for iCluster in range(0, len(allClusters)):
            leftIndex = allClusters[iCluster].LeftChild - 1
            rightIndex = allClusters[iCluster].RightChild - 1
            if(allClusters[iCluster].LeftChild != 0):
                leftChild = allClusters[leftIndex]
                rightChild = allClusters[rightIndex]
                allClusters[iCluster].SplitTightness = \
                    (leftChild.ClusterSize * leftChild.ClusterTightness + \
                    rightChild.ClusterSize * rightChild.ClusterTightness) / \
                    (leftChild.ClusterSize + rightChild.ClusterSize)
                # allClusters[iCluster].SplitTightness = \
                #     leftChild.ClusterTightness + \
                #     rightChild.ClusterTightness
                allClusters[iCluster].SplitGain = \
                    allClusters[iCluster].ClusterTightness - \
                    allClusters[iCluster].SplitTightness
                allClusters[iCluster].NormalizedSplitGain = \
                    allClusters[iCluster].SplitGain * \
                    allClusters[iCluster].ClusterWeight / root.ClusterTightness
                allClusters[iCluster].NormalizedClusterTightness = \
                    allClusters[iCluster].ClusterTightness * \
                    allClusters[iCluster].ClusterWeight / root.ClusterTightness
        
        self.allClusters = allClusters
        
        
def nanEucFun(u, v):
    d = (u - v) ** 2
    nNonNan = np.sum(~np.isnan(d), axis=0)
    D2squared = np.true_divide(np.nansum(d, axis = 0), nNonNan)
    D = np.sqrt(D2squared)
    return D
    
    
def findRootChildClusters(allClusters, clusterIndices):
    nAllCluster = len(allClusters)
    nCurrentCluster = np.max(clusterIndices)
    isNewCluster = np.ones(nCurrentCluster, dtype=bool)
    for i in range(0, nAllCluster):
        indices = allClusters[i].SampleIndices
        for j in range(0, nCurrentCluster):
            if(np.array_equal(indices, clusterIndices == (j+1))):
                isNewCluster[j] = False
                break
    #iNewC = [i for (i, val) in enumerate(isNewCluster) if val > 0]
    iNewC = np.where(isNewCluster)[0]
    # print(isNewCluster)
    # print("afkjfjs")
    # print(iNewC)
    # print(iNewC[0])
    # print(nAllCluster)
    indicesNew1 = clusterIndices == (iNewC[0] + 1)
    indicesNew2 = clusterIndices == (iNewC[1] + 1)
    indicesCombined = np.logical_or(indicesNew1, indicesNew2)
    # print(sum(indicesCombined))
    for i in range(0, nAllCluster):
        indices = allClusters[i].SampleIndices
        # print(sum(indicesNew1))
        # print(sum(indicesNew2))
        # print(sum(indicesCombined))
        if(np.array_equal(indices, indicesCombined)):
            iRootCluster = allClusters[i].ClusterIndex
    C = ClusterIndexing()
    C.Index = (len(allClusters) + 3) / 2
    C.Root = iRootCluster
    C.Cluster1 = iNewC[0] + 1
    C.Cluster2 = iNewC[1] + 1 
    return C
    
    
class ClusterIndexing():
    def __init__(self):
        self.Index = None
        self.Root = None
        self.Cluster1 = None
        self.Cluster2 = None
    def __str__(self):
        return  "Index=" + str(self.Index) + " - " \
        "Root=" + str(self.Root) + " - " \
        "Cluster1=" + str(self.Cluster1) + " - " \
        "Cluster2=" + str(self.Cluster2)
        
        
        
        
        
        
