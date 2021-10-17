
from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.transform import dodge
import pandas as pd

xls = pd.ExcelFile('out.xls')
tasks_df = pd.read_excel(xls)

output_file("bars.html")

weeks = list(dict.fromkeys('w'+tasks_df['Week'].astype(str)))
task_types = list(dict.fromkeys(tasks_df['Task_Type_Ref']))

data = {'weeks': weeks,
        'Site_Surveys': list(tasks_df[tasks_df['Task_Type_Ref']=='Site_Survey']['id']),
        'Infrastructure_Constructions': list(tasks_df[tasks_df['Task_Type_Ref']=='Infrastructure_Construction']['id']),
        'Opt_Network_Constructions': list(tasks_df[tasks_df['Task_Type_Ref']=='Opt_Network_Construction']['id']),
        'Customer_Connections': list(tasks_df[tasks_df['Task_Type_Ref']=='Customer_Connection']['id'])}

print(data['Site_Surveys'])
print(data['Customer_Connections'])

source = ColumnDataSource(data=data)

tooltips = [
    ("week", "@weeks"),
    ('$name', "@Site_Surveys")
    ]

p = figure(x_range=weeks, plot_width=1000, plot_height=500, title="Tasks completed by week",
           toolbar_location=None, tools="")


r_ss = p.vbar(x=dodge('weeks', -0.4, range=p.x_range), top='Site_Surveys', width=0.18, source=source,
       color="#4B0082", legend_label="Site Surveys")

hover_ss = HoverTool(tooltips="Site Surveys: @Site_Surveys", renderers=[r_ss])

r_ic = p.vbar(x=dodge('weeks',  -0.2,  range=p.x_range), top='Infrastructure_Constructions', width=0.18, source=source,
       color="#718dbf", legend_label="Infrastructure Constructions")

hover_ic = HoverTool(tooltips="Infrastructure Constructions: @Infrastructure_Constructions", renderers=[r_ic])

r_onc = p.vbar(x=dodge('weeks',  0.0, range=p.x_range), top='Opt_Network_Constructions', width=0.18, source=source,
       color="#e84d60", legend_label="Opt. Network Constructions")

hover_onc = HoverTool(tooltips="Opt. Network Constructions: @Opt_Network_Constructions", renderers=[r_onc])

r_cc = p.vbar(x=dodge('weeks',  0.2, range=p.x_range), top='Customer_Connections', width=0.18, source=source,
       color="#006400", legend_label="Customer Connections")

hover_cc = HoverTool(tooltips="Customer Connections: @Customer_Connections", renderers=[r_cc])


# hover1 = HoverTool(tooltips='$name: @$name')
p.add_tools(hover_ss, hover_ic, hover_onc, hover_cc)


p.x_range.range_padding = 0.05
p.xgrid.grid_line_color = None
p.legend.location = "top_left"
p.legend.orientation = "vertical"
p.legend.click_policy="hide"
p.legend.background_fill_alpha = 0.4

p.legend.title_text_font = 'Arial'
p.legend.title_text_font_size = '20pt'

show(p)

# fruits = ['Apples', 'Pears', 'Nectarines', 'Plums', 'Grapes', 'Strawberries']
# years = ['2015', '2016', '2017']
#
# data = {'fruits' : fruits,
#         '2015'   : [2, 1, 4, 3, 2, 4],
#         '2016'   : [5, 3, 3, 2, 4, 6],
#         '2017'   : [3, 2, 4, 4, 5, 3]}
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# x = list(zip('w'+tasks_df['Week'].astype(str), tasks_df['Task_Type_Ref']))
#
# counts = tasks_df['id']
#
# source = ColumnDataSource(data=dict(x=x, counts=counts))
#
# p = figure(x_range=FactorRange(*x), plot_height=500, title="Tasks completed by Week",
#            toolbar_location=None, tools="")
#
# p.vbar(x='x', top='counts', width=0.9, source=source)
#
# p.y_range.start = 0
# p.x_range.range_padding = 0.1
# p.xaxis.major_label_orientation = 1
# p.xgrid.grid_line_color = None
#
# show(p)
