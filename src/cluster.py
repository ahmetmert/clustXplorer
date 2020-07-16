class Cluster():
    def __init__(self):
        self.ClusterIndex = None
        self.ParentIndex = None
        self.SampleIndices = None
        self.ClusterSize = None
        self.ClusterWeight = None
        self.ClusterTightness = None
        self.LeftChild = None
        self.RightChild = None
        self.SplitTightness = "N/A"
        self.SplitGain = "N/A"
        self.NormalizedSplitGain = "N/A"
        self.NormalizedClusterTightness = "N/A"
        self.Component1Mean = None
        self.Component2Mean = None
        
    def __str__(self):
        return "ClusterIndex=" + str(self.ClusterIndex) + " - " \
        "ParentIndex=" + str(self.ParentIndex) + " - " \
        "ClusterSize=" + str(self.ClusterSize) + " - " \
        "ClusterTightness=" + "{:.2f}".format(self.ClusterTightness) + " - " \
        "LeftChild=" + str(self.LeftChild) + " - " \
        "RightChild=" + str(self.RightChild)