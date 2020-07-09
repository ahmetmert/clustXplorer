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

from bokeh.models import Band, ColumnDataSource
from bokeh.layouts import column, row, WidgetBox
from bokeh.palettes import Category20_16
from bokeh import plotting

from .cluster import Cluster

# Make plot with histogram and return tab
def perm_tab(allClusters):
    #global source_data
    #global dataS
    #global segmentSource
    #global locked
    #locked = 0
    
    #mean_sd = pd.read_excel('Data/mean-sd.xlsx')
    #xAxis = mean_sd['x']
    #mean = mean_sd['mean']
    #std = mean_sd['std']

    #perm_gray_source = ColumnDataSource(data=dict(
    #    x = xAxis ,
    #    lower = mean - (2 * std),
    #    upper = mean + (2 * std),
    #))	
	
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
    

    
    
    #p = figure()
    #perm_plot = figure(tools = "tap", x_axis_type="log", plot_width=600, plot_height=400 ,x_range=(10,700), y_range=(0, 14))
    perm_plot = figure(tools = "tap", x_axis_type="log", plot_width=600, plot_height=400 ,x_range=(10,700))
    
    #source_data = dict(x = [-1, 300,200,100],y = [-1, 6, 8, 4], color = ["#1f77b4", "#1f77b4","#1f77b4","#1f77b4"] )

    source_data = PermPlotData(allClusters)
    dataS = ColumnDataSource(source_data.data)
    segmentSource = ColumnDataSource(source_data.links)
    # color= 'olive'
    sr = perm_plot.segment(x0='x0', y0='y0', x1='x1', y1='y1', color= "#1f77b4", alpha=0.6, source=segmentSource, line_width=3)
    cr = perm_plot.circle(x='x',y = 'y',color = 'color', line_width = 'linewidth', alpha = 'visible', source = dataS, size='size', line_color = 'black')
    
    def circle_click_handle(attr, old, new):
        if(len(new) != 0):
            circle_click_behavior(new, source_data, dataS, segmentSource)
    
    dataS.selected.on_change('indices', circle_click_handle)
    cr.nonselection_glyph = None
    sr.nonselection_glyph = None
    
    hover_tool = HoverTool(renderers = [cr], tooltips=TOOLTIPS)
    perm_plot.add_tools(hover_tool)
    
    perm_plot.xaxis.axis_label = "Number of participants"
    perm_plot.xaxis.axis_label_text_font_size = '20pt'
    perm_plot.xaxis.major_label_text_font_size = '8pt'

    perm_plot.yaxis.axis_label = "Mean pairwise distance"
    perm_plot.yaxis.axis_label_text_font_size = '20pt'
    perm_plot.yaxis.major_label_text_font_size = '8pt'
    
    #perm_plot.line(xAxis, mean, line_width = 0.5, line_alpha = 0.7, line_color = 'black')
    #band = Band(base='x', lower='lower', upper='upper', level='underlay', source=perm_gray_source,
    #            fill_alpha=0.5, line_width=2, line_color='black')

    #perm_plot.add_layout(band)
    #calculate_shade(cts_data)

    pca_plot = figure(plot_width=400, plot_height=400 ,x_range=(0,700), y_range=(0, 14))

    # Put controls in a single element
    b1 = Button(label="Foo")
    s1 = Select(title="Option:", value="foo", options=["foo", "bar", "baz", "quux"])
    controls = WidgetBox(b1,s1)
    # Create a row layout
    layout = row(controls, perm_plot, pca_plot)# , )
    #layout = row(p, p)
    # Make a tab with the layout 
    tab = Panel(child=layout, title = 'Histogram')
    
    return tab
        
def circle_click_behavior(new, source_data, dataS, segmentSource):
    # The index of the selected glyph is : new['1d']['indices'][0]
    
    if(len(new) == 0):
        return
    selection = new[0]
    print("call back fired")
    print(selection)
    
    random_number = random.randint(0, 16777215)
    hex_number = str(hex(random_number))
    hex_number ='#'+ hex_number[2:]
    
    source_data.data['color'][selection] = hex_number
    source_data.updateNode(selection)
    
    dataS.data = source_data.data
    dataS.selected.indices = []
    segmentSource.data = source_data.links
    print("call back terminated")  
        
        

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
    
def getAllClusterSubset(allClusters, subsetsize):
    clusters = allClusters[0:subsetsize]
    return clusters
    
def dummyCluster():
    dummy = Cluster()
    dummy.ClusterIndex = -1
    dummy.ClusterSize = 0
    dummy.ClusterTightness = 0
    return dummy
    
class PermPlotData(object):
    def __init__(self, allClusters):
        #allClusters.insert(0, dummyCluster())
        clusterIndex = toArrayFormat(allClusters, "ClusterIndex")
        clusterSize = toArrayFormat(allClusters, "ClusterSize")
        clusterTightness = toArrayFormat(allClusters, "ClusterTightness")
        leftIndex = toArrayFormatChildren(allClusters, "LeftChild")
        rightIndex = toArrayFormatChildren(allClusters, "RightChild")
        splitGain = toArrayFormat(allClusters, "SplitGain")
        normalizedSplitGain = toArrayFormat(allClusters, "NormalizedSplitGain")
        n = len(clusterSize)
        
        color = ["#1f77b4"] * n
        visible = [0] * n
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
        color = color, \
        visible = visible, \
        toggled = toggled, \
        linewidth = linewidth, \
        size = size, \
        )
        self.updateCircles()
        self.updateLinks()
        
    def updateCircles(self):
        for i in range(0, self.n):
            if(self.data['visible'][i] == 0):
                self.data['size'][i] = 0
            else:
                self.data['size'][i] = 25
            
        
    def updateLinks(self):
        links = {'x0': [], 'y0': [], 'x1': [], 'y1': []};
        
        # root node
        stack = [0];
        
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
    
