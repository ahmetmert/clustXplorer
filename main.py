#%%
# Pandas for data management
import pandas as pd

# os methods for manipulating paths
from os.path import dirname, join

# Bokeh basics 
from bokeh.io import curdoc, output_file, show
from bokeh.models.widgets import Tabs,Panel
from sklearn.datasets import load_boston


# Each tab is drawn by one script
#from scripts.histogram import histogram_tab
#from scripts.density import density_tab
#from scripts.table import table_tab
#from scripts.draw_map import map_tab
#from scripts.routes import route_tab

# Using included state data from Bokeh for map
from bokeh.sampledata.us_states import data as states

from src.perm_tab import perm_tab
from src.clustering import Clustering

def getAllClusterSubset(allClusters, subsetsize):
    clusters = allClusters[0:subsetsize]
    return clusters

#cst_data = pd.read_csv(join(dirname(__file__), 'data', 'CTSData.csv'))
#cst_data = pd.read_csv(join(dirname(__file__), 'data', 'CTSData.csv')).dropna()

X, y = load_boston(return_X_y=True)
# processed_data = pre_process(data)
            
clust = Clustering(X)
clust.initiate_clustering()

allClusters = clust.allClusters

clusters = getAllClusterSubset(allClusters, 20)

for i in range(0, len(clusters)):
    print(clusters[i])

                


# dist_matrix = calculate_pdist(processed_data, )

# li = linkage(dm, method='ward')




# Create each of the tabs
tab_perm = perm_tab(allClusters)
#tab2 = density_tab(flights)
#tab3 = table_tab(flights)
#tab4 = map_tab(map_data, states)
#tab5 = route_tab(flights)

#tab_sub1 = Panel()
#tab_sub2 = Panel()

# Put all the tabs into one application
#tabs = Tabs(tabs = [tab1, tab2, tab3, tab4, tab5])

# Put the tabs in the current document for display

#curdoc().add_root(tab_perm)
tabs = Tabs(tabs=[tab_perm])
#output_file("main.html")
#show(tabs)
curdoc().add_root(tabs)

# %%
#This is a test change
