
import pandas as pd
from datetime import datetime

def add_year_month_week(in_df, date_column_name):
    in_df['Year'] = in_df[date_column_name].dt.isocalendar().year
    in_df['Month'] = in_df[date_column_name].dt.month
    in_df['Week'] = in_df[date_column_name].dt.isocalendar().week
    return in_df

dates = pd.date_range('2020-01-01', '2020-12-31')

dates_list = []
task_types_list = []

for date in dates:
    for i in range(0, 4):
        dates_list.append(date)
    task_types_list.append('Site_Survey')
    task_types_list.append('Infrastructure_Construction')
    task_types_list.append('Opt_Network_Construction')
    task_types_list.append('Customer_Connection')

dates_task_types_df = pd.DataFrame({'Date': dates_list, 'Task_Type_Ref': task_types_list},
                                   columns=['Date', 'Task_Type_Ref'])
t_xls = pd.ExcelFile('try.xls')

tasks_df = pd.read_excel(t_xls)

tasks_df['Count'] = 1

completed_tasks_df = pd.merge(dates_task_types_df, tasks_df, left_on=['Date', 'Task_Type_Ref'], right_on=['planned_date', 'task_type'], how='left')
completed_tasks_df = completed_tasks_df.fillna(0)
completed_tasks_df = add_year_month_week(completed_tasks_df, 'Date')
completed_tasks_df = completed_tasks_df[['Date', 'Year', 'Month', 'Week', 'order_id', 'task_id', 'Task_Type_Ref', 'category', 'central_office', 'user', 'organisation', 'Count']]
completed_tasks_df['Date'] = completed_tasks_df['Date']

incoming_tasks_df = pd.merge(dates_task_types_df, tasks_df, left_on=['Date', 'Task_Type_Ref'], right_on=['insertion_date', 'task_type'], how='left')
incoming_tasks_df = incoming_tasks_df.fillna(0)
incoming_tasks_df = add_year_month_week(incoming_tasks_df, 'Date')
incoming_tasks_df = incoming_tasks_df[['Date', 'Year', 'Month', 'Week', 'order_id', 'task_id', 'Task_Type_Ref', 'category', 'central_office', 'user', 'organisation', 'Count']]


#################### Weekly #########################

completed_tasks_df_w = completed_tasks_df
incoming_tasks_df_w = incoming_tasks_df

first_week = 35
last_week = 44

names = [x for x in incoming_tasks_df_w.columns] + ['Completed', 'Backlog_Week']
backlog_tasks_df_w = pd.DataFrame(columns=names)

for i in range(first_week, last_week + 1):
    completed_tasks_df_tmp_w = completed_tasks_df_w[completed_tasks_df_w['Week'] <= i]
    completed_tasks_df_tmp_w = completed_tasks_df_tmp_w[completed_tasks_df_tmp_w['Task_Type_Ref'] == 'Customer_Connection']
    completed_tasks_df_tmp_w = completed_tasks_df_tmp_w.reset_index()
    incoming_tasks_df_tmp_w = incoming_tasks_df_w[incoming_tasks_df_w['Week'] <= i]
    incoming_tasks_df_tmp_w = incoming_tasks_df_tmp_w[incoming_tasks_df_tmp_w['Task_Type_Ref'] == 'Site_Survey']
    incoming_tasks_df_tmp_w = incoming_tasks_df_tmp_w.reset_index(drop=True)
    incoming_tasks_df_tmp_w['Completed'] = ''
    incoming_tasks_df_tmp_w['Backlog_Week'] = ''
    for j in range(incoming_tasks_df_tmp_w['Week'].size):
        if incoming_tasks_df_tmp_w.loc[j, 'order_id'] in list(completed_tasks_df_tmp_w['order_id']):
            incoming_tasks_df_tmp_w.loc[j, 'Completed'] = 'OK'
    incoming_tasks_df_tmp_w = incoming_tasks_df_tmp_w[incoming_tasks_df_tmp_w['Completed'] != 'OK']
    incoming_tasks_df_tmp_w['Backlog_Week'] = i
    backlog_tasks_df_w = pd.concat([backlog_tasks_df_w, incoming_tasks_df_tmp_w])

completed_tasks_df_w = completed_tasks_df_w[completed_tasks_df_w['Week'] >= first_week]
completed_tasks_df_w = completed_tasks_df_w[completed_tasks_df_w['Week'] <= last_week]
incoming_tasks_df_w = incoming_tasks_df_w[incoming_tasks_df_w['Week'] >= first_week]
incoming_tasks_df_w = incoming_tasks_df_w[incoming_tasks_df_w['Week'] <= last_week]

backlog_tasks_df_w.to_excel('out_backlog_tasks_w.xls')
completed_tasks_df_w.to_excel('out_completed_tasks_w.xls')
incoming_tasks_df_w.to_excel('out_incoming_tasks_w.xls')


#################### Monthly ###########################

completed_tasks_df_m = completed_tasks_df
incoming_tasks_df_m = incoming_tasks_df

first_month = 1
last_month = 10

names = [x for x in incoming_tasks_df_m.columns] + ['Completed', 'Backlog_Month']
backlog_tasks_df_m = pd.DataFrame(columns=names)

for i in range(first_month, last_month + 1):
    completed_tasks_df_tmp_m = completed_tasks_df_m[completed_tasks_df_m['Month'] <= i]
    completed_tasks_df_tmp_m = completed_tasks_df_tmp_m[completed_tasks_df_tmp_m['Task_Type_Ref'] == 'Customer_Connection']
    completed_tasks_df_tmp_m = completed_tasks_df_tmp_m.reset_index()
    incoming_tasks_df_tmp_m = incoming_tasks_df_m[incoming_tasks_df_m['Month'] <= i]
    incoming_tasks_df_tmp_m = incoming_tasks_df_tmp_m[incoming_tasks_df_tmp_m['Task_Type_Ref'] == 'Site_Survey']
    incoming_tasks_df_tmp_m = incoming_tasks_df_tmp_m.reset_index(drop=True)
    incoming_tasks_df_tmp_m['Completed'] = ''
    incoming_tasks_df_tmp_m['Backlog_Month'] = ''
    for j in range(incoming_tasks_df_tmp_m['Month'].size):
        if incoming_tasks_df_tmp_m.loc[j, 'order_id'] in list(completed_tasks_df_tmp_m['order_id']):
            incoming_tasks_df_tmp_m.loc[j, 'Completed'] = 'OK'
    incoming_tasks_df_tmp_m = incoming_tasks_df_tmp_m[incoming_tasks_df_tmp_m['Completed'] != 'OK']
    incoming_tasks_df_tmp_m['Backlog_Month'] = i
    backlog_tasks_df_m = pd.concat([backlog_tasks_df_m, incoming_tasks_df_tmp_m])

completed_tasks_df_m = completed_tasks_df_m[completed_tasks_df_m['Month'] >= first_month]
completed_tasks_df_m = completed_tasks_df_m[completed_tasks_df_m['Month'] <= last_month]
incoming_tasks_df_m = incoming_tasks_df_m[incoming_tasks_df_m['Month'] >= first_month]
incoming_tasks_df_m = incoming_tasks_df_m[incoming_tasks_df_m['Month'] <= last_month]

backlog_tasks_df_m.to_excel('out_backlog_tasks_m.xls')
completed_tasks_df_m.to_excel('out_completed_tasks_m.xls')
incoming_tasks_df_m.to_excel('out_incoming_tasks_m.xls')

#################### Daily #########################

completed_tasks_df_d = completed_tasks_df.reset_index(drop=True)
incoming_tasks_df_d = incoming_tasks_df.reset_index(drop=True)

dates_range = pd.date_range('2020-10-21', '2020-10-30')

names = [x for x in incoming_tasks_df_d.columns] + ['In_Range', 'Completed', 'Backlog_Date']
backlog_tasks_df_d = pd.DataFrame(columns=names)

for date in dates_range:

    completed_tasks_df_tmp_d = completed_tasks_df_d.reset_index(drop=True)
    for j in range(completed_tasks_df_tmp_d['Date'].size):
        if completed_tasks_df_tmp_d.loc[j, 'Date'] < date:
            completed_tasks_df_tmp_d.loc[j, 'In_Range'] = 'OK'
    completed_tasks_df_tmp_d = completed_tasks_df_tmp_d[completed_tasks_df_tmp_d['In_Range'] == 'OK']
    completed_tasks_df_tmp_d = completed_tasks_df_tmp_d[completed_tasks_df_tmp_d['Task_Type_Ref'] == 'Customer_Connection']
    completed_tasks_df_tmp_d = completed_tasks_df_tmp_d.reset_index(drop=True)

    incoming_tasks_df_tmp_d = incoming_tasks_df_d.reset_index(drop=True)
    for j in range(incoming_tasks_df_tmp_d['Date'].size):
        if incoming_tasks_df_tmp_d.loc[j, 'Date'] < date:
            incoming_tasks_df_tmp_d.loc[j, 'In_Range'] = 'OK'
    incoming_tasks_df_tmp_d = incoming_tasks_df_tmp_d[incoming_tasks_df_tmp_d['In_Range'] == 'OK']
    incoming_tasks_df_tmp_d = incoming_tasks_df_tmp_d[incoming_tasks_df_tmp_d['Task_Type_Ref'] == 'Site_Survey']
    incoming_tasks_df_tmp_d = incoming_tasks_df_tmp_d.reset_index(drop=True)

    incoming_tasks_df_tmp_d['Completed'] = ''
    incoming_tasks_df_tmp_d['Backlog_Date'] = ''

    for j in range(incoming_tasks_df_tmp_d['Date'].size):
        if incoming_tasks_df_tmp_d.loc[j, 'order_id'] in list(completed_tasks_df_tmp_d['order_id']):
            incoming_tasks_df_tmp_d.loc[j, 'Completed'] = 'OK'
    incoming_tasks_df_tmp_d = incoming_tasks_df_tmp_d[incoming_tasks_df_tmp_d['Completed'] != 'OK']
    incoming_tasks_df_tmp_d['Backlog_Date'] = date
    backlog_tasks_df_d = pd.concat([backlog_tasks_df_d, incoming_tasks_df_tmp_d])

completed_tasks_df_d['In_Range'] = ''
incoming_tasks_df_d['In_Range'] = ''

for j in range(completed_tasks_df_d['Date'].size):
    if completed_tasks_df_d.loc[j, 'Date'] in list(dates_range):
        completed_tasks_df_d.loc[j, 'In_Range'] = 'OK'
completed_tasks_df_d = completed_tasks_df_d[completed_tasks_df_d['In_Range'] == 'OK']

for j in range(incoming_tasks_df_d['Date'].size):
    if incoming_tasks_df_d.loc[j, 'Date'] in list(dates_range):
        incoming_tasks_df_d.loc[j, 'In_Range'] = 'OK'
incoming_tasks_df_d = incoming_tasks_df_d[incoming_tasks_df_d['In_Range'] == 'OK']

backlog_tasks_df_d['Backlog_Date'] = backlog_tasks_df_d['Backlog_Date'].astype(str).str.slice(stop=11)
completed_tasks_df_d['Date'] = completed_tasks_df_d['Date'].astype(str).str.slice(stop=11)
incoming_tasks_df_d['Date'] = incoming_tasks_df_d['Date'].astype(str).str.slice(stop=11)

backlog_tasks_df_d.to_excel('out_backlog_tasks_d.xls')
completed_tasks_df_d.to_excel('out_completed_tasks_d.xls')
incoming_tasks_df_d.to_excel('out_incoming_tasks_d.xls')


