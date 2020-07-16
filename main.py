#%%
# Pandas for data management
import numpy as np
import pandas as pd

# os methods for manipulating paths
from os.path import dirname, join

# Bokeh basics 
from bokeh.io import curdoc, output_file, show
from bokeh.models.widgets import Tabs,Panel
from sklearn.datasets import load_boston
from bokeh.models.widgets import (CheckboxGroup, Slider, RangeSlider, 
                                  Tabs, CheckboxButtonGroup, 
                                  TableColumn, DataTable, Select, Button)
from bokeh.models import ColumnDataSource                   
from bokeh.layouts import column, row, WidgetBox

# Using included state data from Bokeh for map
from bokeh.sampledata.us_states import data as states


from src.perm_tab import perm_tab
from src.clustering import Clustering
from src.clusterController import ClusterController

def getAllClusterSubset(allClusters, subsetsize):
    clusters = allClusters[0:subsetsize]
    return clusters

#cst_data = pd.read_csv(join(dirname(__file__), 'data', 'CTSData.csv'))
#cst_data = pd.read_csv(join(dirname(__file__), 'data', 'CTSData.csv')).dropna()

clustCont = ClusterController();
tab_perm = clustCont.tab;

b1 = Button(label="Run")
s1 = Select(title="Option:", value="fd", options=["fd", "bar", "baz", "quux"])
controls = column(b1,s1)

src = ColumnDataSource(data = {'x':[3, 5], 'y': [8, -1]})

columns = [
TableColumn(field="x", title="x"),
TableColumn(field="y", title="y"),
]

datatable = DataTable(
    source=src,
    columns = columns,
    width = 800,
    height = 300,
    editable=False,
    reorderable=True,
    disabled=False,
)
dataview = row(controls, datatable)
tab = Panel(child=dataview, title = 'Select Data')

def on_click_data_run():
    print("Data run button is clicked.")
    B = load_boston(return_X_y=False)
    X = B.data
    
    d = dict(zip(B.feature_names, X.transpose()))
    
    #d = dict(X, B.feature_names)
    
    #X, y = load_boston(return_X_y=True)
    clust = Clustering(X)
    clust.initiate_clustering()
    allClusters = clust.allClusters
    principalComponents = clust.principalComponents
    clusters = getAllClusterSubset(allClusters, 20)
    
    print(type(X))
    
    print(X.shape)
    
    print(X[0].shape)
    
    src.data = {'x': [0,3,8], 'jd': [329, 1, 99]}
    
    columns = []
    for key in d:
        columns.append(TableColumn(field=key, title=key))
        print(len(d[key]))
        
        
    
    src.data = d
    datatable.columns = columns
    
    #src.data = dict(np.ndenumerate(X))
    
    for i in range(0, len(clusters)):
        print(clusters[i])
        
    clustCont.update_clustering(allClusters, principalComponents);

b1.on_click(on_click_data_run)

tabs = Tabs(tabs=[tab, tab_perm], name="tabs")
curdoc().add_root(tabs)
curdoc().title = "ClustXplorer"











