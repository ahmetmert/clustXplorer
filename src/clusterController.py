# pandas and numpy for data manipulation
import pandas as pd
import numpy as np
import random

from bokeh.plotting import figure
from bokeh.models import (CategoricalColorMapper, HoverTool, 
                          ColumnDataSource, Panel, 
                          FuncTickFormatter, SingleIntervalTicker, LinearAxis)
from bokeh.models.widgets import (CheckboxGroup, Slider, RangeSlider, 
                                  Tabs, CheckboxButtonGroup, 
                                  TableColumn, DataTable, Select, Button)
from bokeh.layouts import column, row, WidgetBox, Spacer
from bokeh.models import Band, ColumnDataSource
from bokeh.palettes import Category20_16
from bokeh import plotting
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from .cluster import Cluster

class ClusterController():
    def __init__(self):
        self.source_data = PermPlotData([]);
        self.nodeSource = ColumnDataSource(self.source_data.data)
        self.edgeSource = ColumnDataSource(self.source_data.links)
    
        self.perm_plot = figure(tools = "tap", x_axis_type="log", plot_width=600, plot_height=400)
        self.perm_plot.x_range.start = 10
        #self.perm_plot.x_range.start = 10
        self.sr = self.perm_plot.segment(x0='x0', y0='y0', x1='x1', y1='y1', color= "#1f77b4", alpha=0.6, source=self.edgeSource, line_width=3)
        self.cr = self.perm_plot.circle(x='x',y = 'y',color = 'color', line_width = 'linewidth', alpha = 'visible', source = self.nodeSource, size='size', line_color = 'black')
        self.cr.nonselection_glyph = None
        self.sr.nonselection_glyph = None
        
        hover_tool = HoverTool(renderers = [self.cr], tooltips=hover_tooltips())
        self.perm_plot.add_tools(hover_tool)
        
        self.perm_plot.xaxis.axis_label = "Number of samples"
        self.perm_plot.xaxis.axis_label_text_font_size = '14pt'
        self.perm_plot.xaxis.major_label_text_font_size = '8pt'

        self.perm_plot.yaxis.axis_label = "Mean Pairwise Distance"
        self.perm_plot.yaxis.axis_label_text_font_size = '14pt'
        self.perm_plot.yaxis.major_label_text_font_size = '8pt'
        
        b1 = Button(label="Change Colors")
        def circle_click_handle(attr, old, new):
            if(len(new) != 0):
                self.circle_click_behavior(new)
                #source_data.updatePCAdata()
                #pca_square_data.data = source_data.pca_data
        self.nodeSource.selected.on_change('indices', circle_click_handle)
        
        def color_button_click_handle():
            self.assign_random_colors()
        b1.on_click(color_button_click_handle)
        
        self.pca_plot = plotting.figure(plot_width=500, plot_height=400)
        self.pca_plot.xaxis.visible = False
        self.pca_plot.xgrid.visible = False
        self.pca_plot.yaxis.visible = False
        self.pca_plot.ygrid.visible = False
        
        self.pcaCircleSource = ColumnDataSource(data=dict(x=[], y=[], color=[]))
        self.pcaSquareSource = ColumnDataSource(data=self.source_data.pca_data)
        
        pca_circle = self.pca_plot.circle('x','y',color = 'color', source = self.pcaCircleSource, size = 9, line_width = 1, line_color = 'black')
        pca_square = self.pca_plot.square('x','y',color = 'color', alpha = 'visible', source = self.pcaSquareSource, size = 20, line_width = 3.25, line_color = 'black')
        
        layout = row(Spacer(width=10), column(b1, self.perm_plot), self.pca_plot)
        self.tab = Panel(child=layout, title = 'Analysis')
        
    def assign_random_colors(self):
        for i in range(0, self.source_data.n):
            random_number = random.randint(0, 16777215)
            hex_number = str(hex(random_number))
            hex_number ='#'+ hex_number[2:]
            self.source_data.data['color'][i] = hex_number
        self.source_data.updatePCAdata()
        self.flush_pca_squares()
        self.flush_clustering_plot_nodes()
        
    def circle_click_behavior(self, new):
        if(len(new) == 0):
            return
        selection = new[0]
        print("call back fired")
        print(selection)
        
        random_number = random.randint(0, 16777215)
        hex_number = str(hex(random_number))
        hex_number ='#'+ hex_number[2:]
        #source_data.data['color'][selection] = hex_number
        
        self.source_data.updateNode(selection)
        self.source_data.updatePCAdata()
        self.flush_clustering_plot()        
        self.flush_pca_squares()
        self.nodeSource.selected.indices = []
        print("call back terminated")          
        
    def update_pca(self, principalComponents):
        pca_x = principalComponents[:,0]
        pca_y = principalComponents[:,1]
        color = ["black"] * len(pca_x)
        self.pcaCircleSource.data = dict(x=pca_x, y=pca_y, color=color)
        
    def update_clustering(self, allClusters, principalComponents):
        self.source_data.update_clustering(allClusters);
        self.update_pca(principalComponents);
        self.assign_random_colors();
        self.flush_clustering_plot();
    
    def flush_pca_squares(self):
        self.pcaSquareSource.data = self.source_data.pca_data;
    
    def flush_clustering_plot(self):
        self.flush_clustering_plot_nodes();
        self.flush_clustering_plot_edges();
       
    def flush_clustering_plot_nodes(self):
        self.nodeSource.data = self.source_data.data;
           
    def flush_clustering_plot_edges(self):
        self.edgeSource.data = self.source_data.links;

def toArrayFormat(allClusters, field):
    lst = []
    for i in range(0, len(allClusters)):
        lst.append(getattr(allClusters[i], field))
    return lst

def toArrayFormatChildren(allClusters, field):
    lst = []
    for i in range(0, len(allClusters)):
        lst.append(getattr(allClusters[i], field) - 1)
    return lst

class PermPlotData(object):
    
    def __init__(self, allClusters):
        self.update_clustering(allClusters);
        
    def update_clustering(self, allClusters):
        clusterIndex = toArrayFormat(allClusters, "ClusterIndex")
        clusterSize = toArrayFormat(allClusters, "ClusterSize")
        clusterTightness = toArrayFormat(allClusters, "ClusterTightness")
        leftIndex = toArrayFormatChildren(allClusters, "LeftChild")
        rightIndex = toArrayFormatChildren(allClusters, "RightChild")
        splitGain = toArrayFormat(allClusters, "SplitGain")
        normalizedSplitGain = toArrayFormat(allClusters, "NormalizedSplitGain")
        component1Mean = toArrayFormat(allClusters, "Component1Mean")
        component2Mean = toArrayFormat(allClusters, "Component2Mean")
        n = len(clusterSize)
        
        color = ["#1f77b4"] * n
        visible = [0] * n
        if(n > 0):
            visible[0] = 1
        toggled = [0] * n
        linewidth = [1] * n
        size = [1] * n
        for i in range(0, len(clusterSize)):
            if(leftIndex[i] >= 0 or rightIndex[i] >= 0):
                linewidth[i] = 3
            else:
                linewidth[i] = 1
        
        self.n = n
        self.data = dict(\
        index = clusterIndex, \
        x = clusterSize, \
        y = clusterTightness, \
        left = leftIndex, \
        right = rightIndex, \
        splitgain = splitGain, \
        normgain = normalizedSplitGain, \
        component1Mean = component1Mean, \
        component2Mean = component2Mean, \
        color = color, \
        visible = visible, \
        toggled = toggled, \
        linewidth = linewidth, \
        size = size, \
        )
        self.updateCircles()
        self.updateLinks()
        self.updatePCAdata()
        
    def updateCircles(self):
        for i in range(0, self.n):
            if(self.data['visible'][i] == 0):
                self.data['size'][i] = 0
            else:
                self.data['size'][i] = 25
            
        
    def updateLinks(self):
        links = {'x0': [], 'y0': [], 'x1': [], 'y1': []};
        
        # root node
        if(self.n > 0):
            stack = [0];
        else:
            stack = [];
        
        # as long as stack has any node in it
        while len(stack) > 0:
            val = stack.pop();
            
            #if current node is not toggled on 
            if(self.data['toggled'][val] == 0):
                continue;

            # parent coordinates
            parentX = self.data['x'][val];
            parentY = self.data['y'][val];
            
            # generate edge from parent to left child if any
            left = self.data['left'][val]
            if(left >= 0):
                leftX = self.data['x'][left];
                leftY = self.data['y'][left];
                links['x0'].append(parentX);
                links['y0'].append(parentY);
                links['x1'].append(leftX);
                links['y1'].append(leftY);
                stack.append(left);
                
            # generate edge from parent to left child if any
            right = self.data['right'][val]
            if(right >= 0):
                rightX = self.data['x'][right];
                rightY = self.data['y'][right];
                links['x0'].append(parentX);
                links['y0'].append(parentY);
                links['x1'].append(rightX);
                links['y1'].append(rightY);
                stack.append(right);
        
        self.links = links
        
    def updateNode(self, index):
        if(self.data['toggled'][index] == 0):
            self.toggleNode(index)
        else: 
            self.untoggleNode(index)
        self.updateCircles()
        self.updateLinks()
        
    def toggleNode(self, index):
        self.data['toggled'][index] = 1
        left = self.data['left'][index]
        right = self.data['right'][index]
        if(left >= 0):
            self.data['visible'][left] = 1
        if(right >= 0):
            self.data['visible'][right] = 1
        self.updatePCAdata()
    
    def untoggleNode(self, index):
        self.data['toggled'][index] = 0
        left = self.data['left'][index]
        right = self.data['right'][index]
        if(left >= 0 and self.data['visible'][left] == 1):
            self.data['visible'][left] = 0
            self.untoggleNode(left)
        if(right >= 0 and self.data['visible'][right] == 1):
            self.data['visible'][right] = 0
            self.untoggleNode(right)
        self.updatePCAdata()

    def updatePCAdata(self):
        visible = self.data['visible']
        toggled = self.data['toggled']
        pca_sqr_x = self.data['component1Mean']
        pca_sqr_y = self.data['component2Mean']
        pca_visible = []
        for i in range(0, len(visible)):
            pca_visible.append(visible[i] and (not toggled[i]))
        self.pca_data = dict(x=pca_sqr_x, y=pca_sqr_y, \
            color=self.data['color'], visible = pca_visible)
        
def hover_tooltips():
    TOOLTIPS = """
        <div>
         <!--   <div>
                <img
                    src="@imgs" height="90" alt="@imgs" width="85"
                    style="float: left; margin: 0px 15px 15px 0px;"
                    border="2"
                ></img>
            </div> -->
            <div>
                <span style="font-size: 17px; font-weight: bold;">Cluster: @index</span>
            </div>
            
            <div>
                <span style="font-size: 11px;">Cluster size: @x</span>
            </div>
            <div>
                <span style="font-size: 11px;">Cluster tightness: @y</span>
            </div>
            <div>
                <span style="font-size: 11px;">Split gain: @splitgain (@normgain%)</span>
            </div>
            
        </div>
    """
    return TOOLTIPS
        
        
