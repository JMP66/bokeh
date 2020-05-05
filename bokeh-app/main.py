#!/usr/bin/env python
# coding: utf-8

# In[8]:


import pandas as pd
from os.path import dirname, join
from bokeh.io import show, output_notebook
from bokeh.plotting import figure, output_file, show,save
from bokeh.models.widgets import Panel, Tabs
from bokeh.models import ColumnDataSource, HoverTool, LinearColorMapper,TextInput,Label,LabelSet,Title
from bokeh.layouts import column, row, widgetbox
from bokeh.models import CustomJS, Slider, Div,RangeSlider, Button,RadioGroup,LinearAxis, Range1d, ColumnDataSource, Paragraph,Select
import numpy as np
from bokeh.plotting import figure, output_file, show
#from bokeh.tile_providers import CARTODBPOSITRON, get_provider,OSM, STAMEN_TERRAIN
#import math
from bokeh.io import output_file, show, save, curdoc, output_notebook, export_png

#Load data
mid_dyn = pd.read_csv(join(dirname(__file__), "data/MiddleSchools_2006-2018_clean.csv"))
high_dyn = pd.read_csv(join(dirname(__file__), "data/HighSchools_2006-2018_clean.csv"))

mid_stat = pd.read_csv(join(dirname(__file__), "data/MiddleSchools_2018_clean.csv"))
high_stat = pd.read_csv(join(dirname(__file__), "data/HighSchools_2018_clean.csv"))


# In[9]:


#Get data from csv to lists
def get_data(level, school):
    
    #load the school level data
    if level == 'Middle':
        school_data = mid_dyn[mid_dyn['dbn']==school]
    elif level == 'High':
        school_data =  high_dyn[high_dyn['dbn']==school]
        
    # Convert dataframe to column data source
    source = ColumnDataSource(school_data)
    
    return source, school_data


# In[10]:


def create_slider(plot, startYear, endYear):
    callback = CustomJS(args=dict(plot=plot), code="""
    var a = cb_obj.value;
    plot.x_range.start = a[0];
    plot.x_range.end = a[1];
    """)

    range_slider = RangeSlider(start=startYear, end=endYear,value=(startYear, endYear), step=1, width= 600, title="Year Range")
    range_slider.js_on_change('value', callback)

    layout = column(plot,column(range_slider))
    return layout


# In[11]:


def geographic_to_web_mercator(x_lon, y_lat):     
    if abs(x_lon) <= 180 and abs(y_lat) < 90:          
        num = x_lon * 0.017453292519943295         
        x = 6378137.0 * num         
        a = y_lat * 0.017453292519943295          
        x_mercator = x         
        y_mercator = 3189068.5 * np.log((1.0 + np.sin(a)) / (1.0 - np.sin(a)))         
        
        return x_mercator, y_mercator   


# In[12]:


def create_plot():
    colors=['midnightblue','slateblue','dodgerblue','royalblue','cornflowerblue']
    radio_idx = radio_group.active
    school = text_input.value
    
    variables = ['Etnicities','Gender','Mean Score (only for middle school)','Graduation/Dropout (only for high shool)']
   
    if school in mid_stat.dbn.unique():
        level='Middle'
        text = mid_stat[mid_stat['dbn']==school]['overview'].iloc[0]
        data =  mid_stat[mid_stat['dbn']==school]
    elif school in high_stat.dbn.unique():
        level = 'High'
        text = high_stat[high_stat['dbn']==school]['overview'].iloc[0]
        data = high_stat[high_stat['dbn']==school]
           
    src, school_data = get_data(level, school)
          
    if radio_idx == 0:     
        plot = figure(plot_width = 600, plot_height = 500, 
         toolbar_location=None,
        x_axis_label = 'Year', y_axis_label = '% Etnicity')

        races = ['asian_rate', 'black_rate', 'hispanic_rate', 'other_rate', 'white_rate','diversity_index']
        race_title =['Asian', 'Black', 'Hispanic', 'Other', 'White','Diversity Index']
        colors = colors+['gray']
        for (race,tit,color) in zip(races,race_title,colors):
            line=plot.line('year', race, line_width=2, line_color=color, source=src,legend_label=tit)
            plot.circle('year', race, fill_color=color, line_color=color, size=8, source=src)
            hover = HoverTool(renderers=[line])
            hover.tooltips=[
            ('Date', '@year'),
            (tit, '@'+race)
            ]
            plot.add_tools(hover)
            
        plot.legend.location ='top_left' 
        plot.add_layout(Title(text= '{} School \n'.format(level), text_font_style="italic",text_font_size="14pt", align='center'), 'above')
        plot.add_layout(Title(text=school_data['school_name'].unique()[0], text_font_size="16pt",align='center'), 'above',)
        
        #plot.title.align ='center'
        #plot.title.text_font_size = "18px"
        
    elif radio_idx == 1:
        
        plot = figure(plot_width = 600, plot_height = 500, 
        toolbar_location=None,
        x_axis_label = 'Year', y_axis_label = '% Gender')

        genders = ['female_rate','male_rate']
        gender_title =['Female','Male']
        colors = colors[:2]
        for (gender,tit,color) in zip(genders,gender_title,colors):
            line=plot.line('year', gender, line_width=2, line_color=color, source=src,legend_label=tit)
            plot.circle('year', gender, fill_color=color, line_color=color, size=8, source=src)
            hover = HoverTool(renderers=[line])
            hover.tooltips=[
            ('Date', '@year'),
            (tit, '@'+gender)
            ]
            plot.add_tools(hover)
       
        plot.legend.location ='top_left' 
        plot.add_layout(Title(text= '{} School \n'.format(level), text_font_style="italic",text_font_size="14pt", align='center'), 'above')
        plot.add_layout(Title(text=school_data['school_name'].unique()[0], text_font_size="16pt",align='center'), 'above',)
        

        
    elif radio_idx == 2 and level == 'Middle':
        
        plot = figure(plot_width = 600, plot_height = 500, 
       toolbar_location=None, 
        x_axis_label = 'Year', y_axis_label = 'Mean Score')
        cols = ['mean_score_math', 'mean_score_ela']
        cols_tit =  ['Mean Math Score', 'Mean ELA Score']
        colors = colors[:2]

        for (col,tit,color) in zip(cols,cols_tit,colors):
            line=plot.line('year', col, line_width=2, line_color=color, source=src,legend_label=tit)
            plot.circle('year', col, fill_color=color, line_color=color, size=8, source=src)
            hover = HoverTool(renderers=[line])
            hover.tooltips=[
                ('Date', '@year'),
                (tit, '@'+col)
            ]
            plot.add_tools(hover)
        
        plot.legend.location ='top_left' 
        plot.add_layout(Title(text= '{} School \n'.format(level), text_font_style="italic",text_font_size="14pt", align='center'), 'above')
        plot.add_layout(Title(text=school_data['school_name'].unique()[0], text_font_size="16pt",align='center'), 'above',)
        

    elif radio_idx == 3 and level=='High':
        
        plot = figure(plot_width = 600, plot_height = 500, 
       toolbar_location=None, 
        x_axis_label = 'Year', y_axis_label = 'Graduation/Dropout')
        cols = ['dropout_rate', 'graduation_rate']
        cols_tit =  ['Dropout Rate', 'Graduation Rate']
        colors = colors[:2]

        for (col,tit,color) in zip(cols,cols_tit,colors):
            line=plot.line('year', col, line_width=2, line_color=color, source=src,legend_label=tit)
            plot.circle('year', col, fill_color=color, line_color=color, size=8, source=src)
            hover = HoverTool(renderers=[line])
            hover.tooltips=[
                ('Date', '@year'),
                (tit, '@'+col)
            ]
            plot.add_tools(hover)
        
        plot.legend.location ='top_left' 
        plot.add_layout(Title(text= '{} School \n'.format(level), text_font_style="italic",text_font_size="14pt", align='center'), 'above')
        plot.add_layout(Title(text=school_data['school_name'].unique()[0], text_font_size="16pt",align='center'), 'above',)
        

        
    elif (radio_idx == 3 and level != 'High') or (radio_idx == 2 and level != 'Middle'):
        
        plot = figure(plot_width = 600, plot_height = 500, 
       toolbar_location=None, 
        x_axis_label = '', y_axis_label = '')
        
        if level=='High':
            l = 'Middle'
        elif level=='Middle':
            l = 'High'
        
        
        citation = Label(x=170, y=250, x_units='screen', y_units='screen',
                 text='Only available for {} Schools'.format(l), render_mode='css',
                 background_fill_color='white', background_fill_alpha=1.0,text_font_size='20px')
        
        plot.add_layout(citation)
        
        #plot.legend.location ='top_left' 
        #plot.add_layout(Title(text= '{} School \n'.format(level), text_font_style="italic",text_font_size="14pt", align='center'), 'above')
        plot.add_layout(Title(text=school_data['school_name'].unique()[0], text_font_size="16pt",align='center'), 'above',)
        

   
    #Add overview paragraph
    para = Div(text="<h2>Overview</h2>"+text,
    width=300, height=100)
    
    #Get map
    x,y = geographic_to_web_mercator(data['lon'].iloc[0],data['lat'].iloc[0])
    #tile_provider = get_provider(CARTODBPOSITRON)
    # range bounds supplied in web mercator coordinates
    m = figure(x_range=(x-500, x+500), y_range=(y-500, y+500),height=300,width=300, 
               x_axis_location=None, y_axis_location=None,toolbar_location='below',tools="pan,wheel_zoom,reset",active_scroll='auto')
    #m.add_tile(tile_provider)
    square=m.circle(x=x,y=y,size=12, fill_color="midnightblue", fill_alpha=1)
    tooltips = [('Name', data['school_name'].iloc[0]),('Address', data['address'].iloc[0])]
    m.add_tools(HoverTool(renderers=[square],tooltips=tooltips))


    return plot, para, m


# In[13]:



def update1(attr, old, new):
    plot,para,m = create_plot()
    layout.children[1] = create_slider(plot, 2006, 2018)
    

def update2(attr, old, new):
    plot,para,m = create_plot()
    layout.children[2] =  para
    layout.children[0].children[5] =  m
    
text_input = TextInput(value='01M140')
text_input.on_change('value',update1,update2)


div1 = Div(text="<b> Write School DBN </b>")

variables = ['Etnicities','Gender','Mean Score (only middle schools)','Graduation/Dropout (only high shools)']

div2 = Div(text="<b> Choose variable </b>")              
radio_group = RadioGroup(labels=variables, active=3)
radio_group.on_change('active',update1,update2)

div3 =Div(text="<b> School Location </b>") 

plot,para,m = create_plot()
layout = create_slider(plot, 2006, 2018)


#Combine all controls to get in column
controls = column(div1,text_input,div2,radio_group,div3,m, width=300)


#Layout
layout = row(controls,layout,para)


curdoc().add_root(layout)
curdoc().title = "NYC_map"

#output_file("details.html")
#save(layout)

#output_notebook()
show(layout)


# In[14]:


#from bokeh.embed import server_document
#script = server_document("http://localhost:5006/DetailsApp")
#script


# In[ ]:




