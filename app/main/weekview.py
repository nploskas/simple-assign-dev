from flask_admin import BaseView, expose, helpers
from flask_login import current_user
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.transform import dodge
from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.models import CustomJS, MultiSelect
from bokeh.layouts import layout
import pandas as pd

class WeekView(BaseView):

    def is_accessible(self):
        return current_user.is_authenticated

    @expose('/')
    def index(self):

        xls = pd.ExcelFile('out_completed_tasks_w.xls')
        completed_tasks_df = pd.read_excel(xls)
        xls = pd.ExcelFile('out_incoming_tasks_w.xls')
        incoming_tasks_df = pd.read_excel(xls)
        xls = pd.ExcelFile('out_backlog_tasks_w.xls')
        backlog_tasks_df = pd.read_excel(xls)

        central_offices = list(dict.fromkeys(completed_tasks_df['central_office']))
        if 0 in central_offices:
            central_offices.remove(0)
        central_offices.sort()

        organisations = list(dict.fromkeys(completed_tasks_df['organisation']))
        if 0 in organisations:
            organisations.remove(0)
        organisations.sort()

        users = list(dict.fromkeys(completed_tasks_df['user']))
        if 0 in users:
            users.remove(0)
        users.sort()

        categories = list(dict.fromkeys(completed_tasks_df['category']))
        if 0 in categories:
            categories.remove(0)
        for i in range(len(categories)):
            categories[i] = categories[i][14:]
        categories.sort()

        # completed_tasks_df.to_excel('before_groupby.xls')
        weeks = list(dict.fromkeys('w' + completed_tasks_df['Week'].astype(str)))

        completed_tasks_df_g = completed_tasks_df.groupby(['Year', 'Week', 'Task_Type_Ref'], as_index=False, sort=False).sum()
        incoming_tasks_df_g = incoming_tasks_df.groupby(['Year', 'Week', 'Task_Type_Ref'], as_index=False, sort=False).sum()
        backlog_tasks_df_g = backlog_tasks_df.groupby(['Year', 'Backlog_Week', 'Task_Type_Ref']).sum()

        source_completed_tasks_df = ColumnDataSource(completed_tasks_df)
        source_incoming_tasks_df = ColumnDataSource(incoming_tasks_df)
        source_backlog_tasks_df = ColumnDataSource(backlog_tasks_df)

        data01 = {'weeks': weeks,
                'Site_Surveys': list(completed_tasks_df_g[completed_tasks_df_g['Task_Type_Ref'] == 'Site_Survey']['Count']),
                'Infrastructure_Constructions': list(completed_tasks_df_g[completed_tasks_df_g['Task_Type_Ref'] == 'Infrastructure_Construction']['Count']),
                'Opt_Network_Constructions': list(completed_tasks_df_g[completed_tasks_df_g['Task_Type_Ref'] == 'Opt_Network_Construction']['Count']),
                'Customer_Connections': list(completed_tasks_df_g[completed_tasks_df_g['Task_Type_Ref'] == 'Customer_Connection']['Count']),
                'Incoming_Orders': list(incoming_tasks_df_g[incoming_tasks_df_g['Task_Type_Ref'] == 'Site_Survey']['Count']),
                'Backlog_Orders': list(backlog_tasks_df_g['Count'])
                }

        source01 = ColumnDataSource(data=data01)

        multi_select_co = MultiSelect(title='Central Offices', default_size=200, value=central_offices, options=central_offices, margin=(5, 5, 5, 30))
        multi_select_org = MultiSelect(title='Contractor Organisations', default_size=200, value=organisations, options=organisations)
        multi_select_users = MultiSelect(title='Contractor Users', default_size=200, value=users, options=users)
        multi_select_categories = MultiSelect(title='Order Categories', default_size=200, value=categories, options=categories)

        callback_co = CustomJS(args={'source01': source01, 'source_completed_tasks_df': source_completed_tasks_df, 'source_incoming_tasks_df': source_incoming_tasks_df, 'source_backlog_tasks_df': source_backlog_tasks_df,
                                     #'multi_select_co': multi_select_co,
                                     'multi_select_org': multi_select_org,
                                     'multi_select_users': multi_select_users,
                                     'multi_select_categories': multi_select_categories}, code="""
            //console.log('multi_select_cos: value=' + this.value, this.toString());
            var completed_tasks = source_completed_tasks_df.data;
            var incoming_tasks = source_incoming_tasks_df.data;
            var backlog_tasks = source_backlog_tasks_df.data;
            var weeks = source01.data.weeks;
            //var co_options = [];
            var org_options = [];
            var user_options = [];
            var cat_options = [];            
            var site_surveys = source01.data.Site_Surveys;
            var infrastructure_constructions = source01.data.Infrastructure_Constructions; 
            var opt_network_constructions = source01.data.Opt_Network_Constructions;
            var customer_connections = source01.data.Customer_Connections;
            var incoming_orders = source01.data.Incoming_Orders;
            var backlog_orders = source01.data.Backlog_Orders;            
            for (var i = 0; i < weeks.length; i++){
                var week_no = weeks[i].substring(1);
                site_surveys[i] = 0;
                infrastructure_constructions[i] = 0; 
                opt_network_constructions[i] = 0;
                customer_connections[i] = 0;
                incoming_orders[i] = 0;
                backlog_orders[i] = 0;
                for (var j = 0; j < completed_tasks.central_office.length; j++) {
                    if ( (completed_tasks.Week[j] == week_no) && (this.value.includes(completed_tasks.central_office[j])) ) {
                        //if (!co_options.includes(completed_tasks.central_office[j])) {
                        //    co_options.push(completed_tasks.central_office[j]);
                        //}
                        if (!org_options.includes(completed_tasks.organisation[j])) {
                            org_options.push(completed_tasks.organisation[j]);
                        }
                        if (!user_options.includes(completed_tasks.user[j])) {
                            user_options.push(completed_tasks.user[j]);
                        }
                        if (!cat_options.includes(completed_tasks.category[j].substring(14))) {
                            cat_options.push(completed_tasks.category[j].substring(14));
                        }                        
                        //if ( (multi_select_co.value.includes(completed_tasks.central_office[j])) && (multi_select_org.value.includes(completed_tasks.organisation[j])) && (multi_select_users.value.includes(completed_tasks.user[j])) && (multi_select_categories.value.includes(completed_tasks.category[j].substring(14))) )  ) {
                        if ( (this.value.includes(completed_tasks.central_office[j])) && (multi_select_org.value.includes(completed_tasks.organisation[j])) && (multi_select_users.value.includes(completed_tasks.user[j])) && (multi_select_categories.value.includes(completed_tasks.category[j].substring(14))) ) {
                            switch (completed_tasks.Task_Type_Ref[j]) {
                                case "Site_Survey":
                                    site_surveys[i] += 1;
                                    break;
                                case "Infrastructure_Construction":
                                    infrastructure_constructions[i] += 1;
                                    break;
                                case "Opt_Network_Construction":
                                    opt_network_constructions[i] += 1;
                                    break;
                                case "Customer_Connection":
                                    customer_connections[i] += 1;
                                    break;
                            }
                        }
                    }
                }        
                for (var j = 0; j < incoming_tasks.central_office.length; j++) {
                    if ( (incoming_tasks.Week[j] == week_no) && (this.value.includes(incoming_tasks.central_office[j])) ) {
                        if (!org_options.includes(incoming_tasks.organisation[j])) {
                            org_options.push(incoming_tasks.organisation[j]);
                        }
                        if (!user_options.includes(incoming_tasks.user[j])) {
                            user_options.push(incoming_tasks.user[j]);
                        }
                        if (!cat_options.includes(incoming_tasks.category[j].substring(14))) {
                            cat_options.push(incoming_tasks.category[j].substring(14));
                        }                        
                        if ( (this.value.includes(incoming_tasks.central_office[j])) && (multi_select_org.value.includes(incoming_tasks.organisation[j])) && (multi_select_users.value.includes(incoming_tasks.user[j])) && (multi_select_categories.value.includes(incoming_tasks.category[j].substring(14))) ) {
                            switch (incoming_tasks.Task_Type_Ref[j]) {
                                case "Site_Survey":
                                    incoming_orders[i] += 1;
                                    break;
                            }
                        }
                    }
                }        
                for (var j = 0; j < backlog_tasks.central_office.length; j++) {
                    if ( (backlog_tasks.Backlog_Week[j] == week_no) && (this.value.includes(backlog_tasks.central_office[j])) ) {
                        if (!org_options.includes(backlog_tasks.organisation[j])) {
                            org_options.push(backlog_tasks.organisation[j]);
                        }
                        if (!user_options.includes(backlog_tasks.user[j])) {
                            user_options.push(backlog_tasks.user[j]);
                        }
                        if (!cat_options.includes(backlog_tasks.category[j].substring(14))) {
                            cat_options.push(backlog_tasks.category[j].substring(14));
                        }                        
                        if ( (this.value.includes(backlog_tasks.central_office[j])) && (multi_select_org.value.includes(backlog_tasks.organisation[j])) && (multi_select_users.value.includes(backlog_tasks.user[j])) && (multi_select_categories.value.includes(backlog_tasks.category[j].substring(14))) ) {
                            switch (backlog_tasks.Task_Type_Ref[j]) {
                                case "Site_Survey":
                                    backlog_orders[i] += 1;
                                    break;
                            }
                        }
                    }
                }        
            }            
            source01.change.emit();
            //multi_select_co.options = co_options.sort();
            multi_select_org.options = org_options.sort();
            multi_select_users.options = user_options.sort();
            multi_select_categories.options = cat_options.sort();            
        """)
        multi_select_co.js_on_change("value", callback_co)

        callback_org = CustomJS(args={'source01': source01, 'source_completed_tasks_df': source_completed_tasks_df, 'source_incoming_tasks_df': source_incoming_tasks_df, 'source_backlog_tasks_df': source_backlog_tasks_df,
                                     'multi_select_co': multi_select_co,
                                     #'multi_select_org': multi_select_org,
                                     'multi_select_users': multi_select_users,
                                     'multi_select_categories': multi_select_categories}, code="""
            //console.log('multi_select_cos: value=' + this.value, this.toString());
            var completed_tasks = source_completed_tasks_df.data;
            var incoming_tasks = source_incoming_tasks_df.data;
            var backlog_tasks = source_backlog_tasks_df.data;
            var weeks = source01.data.weeks;
            var co_options = [];
            // var org_options = [];
            var user_options = [];
            var cat_options = [];            
            var site_surveys = source01.data.Site_Surveys;
            var infrastructure_constructions = source01.data.Infrastructure_Constructions; 
            var opt_network_constructions = source01.data.Opt_Network_Constructions;
            var customer_connections = source01.data.Customer_Connections;            
            var incoming_orders = source01.data.Incoming_Orders;
            var backlog_orders = source01.data.Backlog_Orders;
            for (var i = 0; i < weeks.length; i++){
                var week_no = weeks[i].substring(1);
                site_surveys[i] = 0;
                infrastructure_constructions[i] = 0; 
                opt_network_constructions[i] = 0;
                customer_connections[i] = 0;            
                incoming_orders[i] = 0;
                backlog_orders[i] = 0;
                for (var j = 0; j < completed_tasks.organisation.length; j++) {
                    if ( (completed_tasks.Week[j] == week_no) && (this.value.includes(completed_tasks.organisation[j])) ) {
                        if (!co_options.includes(completed_tasks.central_office[j])) {
                            co_options.push(completed_tasks.central_office[j]);
                        }
                        //if (!org_options.includes(completed_tasks.organisation[j])) {
                        //    org_options.push(completed_tasks.organisation[j]);
                        //}
                        if (!user_options.includes(completed_tasks.user[j])) {
                            user_options.push(completed_tasks.user[j]);
                        }
                        if (!cat_options.includes(completed_tasks.category[j].substring(14))) {
                            cat_options.push(completed_tasks.category[j].substring(14));
                        }
                        if ( (multi_select_co.value.includes(completed_tasks.central_office[j])) && (this.value.includes(completed_tasks.organisation[j])) && (multi_select_users.value.includes(completed_tasks.user[j])) && (multi_select_categories.value.includes(completed_tasks.category[j].substring(14))) ) {
                            switch (completed_tasks.Task_Type_Ref[j]) {
                                case "Site_Survey":
                                    site_surveys[i] += 1;
                                    break;
                                case "Infrastructure_Construction":
                                    infrastructure_constructions[i] += 1;
                                    break;
                                case "Opt_Network_Construction":
                                    opt_network_constructions[i] += 1;
                                    break;
                                case "Customer_Connection":
                                    customer_connections[i] += 1;
                                    break;
                            }
                        }
                    }
                }        
                for (var j = 0; j < incoming_tasks.organisation.length; j++) {
                    if ( (incoming_tasks.Week[j] == week_no) && (this.value.includes(incoming_tasks.organisation[j])) ) {
                        if (!co_options.includes(incoming_tasks.central_office[j])) {
                            co_options.push(incoming_tasks.central_office[j]);
                        }
                        if (!user_options.includes(incoming_tasks.user[j])) {
                            user_options.push(incoming_tasks.user[j]);
                        }
                        if (!cat_options.includes(incoming_tasks.category[j].substring(14))) {
                            cat_options.push(incoming_tasks.category[j].substring(14));
                        }
                        if ( (multi_select_co.value.includes(incoming_tasks.central_office[j])) && (this.value.includes(incoming_tasks.organisation[j])) && (multi_select_users.value.includes(incoming_tasks.user[j])) && (multi_select_categories.value.includes(incoming_tasks.category[j].substring(14))) ) {
                            switch (incoming_tasks.Task_Type_Ref[j]) {
                                case "Site_Survey":
                                    incoming_orders[i] += 1;
                                    break;
                            }
                        }
                    }
                }        
                for (var j = 0; j < backlog_tasks.organisation.length; j++) {
                    if ( (backlog_tasks.Backlog_Week[j] == week_no) && (this.value.includes(backlog_tasks.organisation[j])) ) {
                        if (!co_options.includes(backlog_tasks.central_office[j])) {
                            co_options.push(backlog_tasks.central_office[j]);
                        }
                        if (!user_options.includes(backlog_tasks.user[j])) {
                            user_options.push(backlog_tasks.user[j]);
                        }
                        if (!cat_options.includes(backlog_tasks.category[j].substring(14))) {
                            cat_options.push(backlog_tasks.category[j].substring(14));
                        }
                        if ( (multi_select_co.value.includes(backlog_tasks.central_office[j])) && (this.value.includes(backlog_tasks.organisation[j])) && (multi_select_users.value.includes(backlog_tasks.user[j])) && (multi_select_categories.value.includes(backlog_tasks.category[j].substring(14))) ) {
                            switch (backlog_tasks.Task_Type_Ref[j]) {
                                case "Site_Survey":
                                    backlog_orders[i] += 1;
                                    break;
                            }
                        }
                    }
                }        
            }            
            source01.change.emit();
            multi_select_co.options = co_options.sort();
            //multi_select_org.options = org_options.sort();
            multi_select_users.options = user_options.sort();
            multi_select_categories.options = cat_options.sort();            
        """)
        multi_select_org.js_on_change("value", callback_org)

        callback_users = CustomJS(args={'source01': source01, 'source_completed_tasks_df': source_completed_tasks_df, 'source_incoming_tasks_df': source_incoming_tasks_df, 'source_backlog_tasks_df': source_backlog_tasks_df,
                                     'multi_select_co': multi_select_co,
                                     'multi_select_org': multi_select_org,
                                     #'multi_select_users': multi_select_users,
                                     'multi_select_categories': multi_select_categories}, code="""
            //console.log('multi_select_cos: value=' + this.value, this.toString());
            var completed_tasks = source_completed_tasks_df.data;
            var incoming_tasks = source_incoming_tasks_df.data;
            var backlog_tasks = source_backlog_tasks_df.data;
            var weeks = source01.data.weeks;
            var co_options = [];
            var org_options = [];
            // var user_options = [];
            var cat_options = [];            
            var site_surveys = source01.data.Site_Surveys;
            var infrastructure_constructions = source01.data.Infrastructure_Constructions; 
            var opt_network_constructions = source01.data.Opt_Network_Constructions;
            var customer_connections = source01.data.Customer_Connections;            
            var incoming_orders = source01.data.Incoming_Orders;
            var backlog_orders = source01.data.Backlog_Orders;
            for (var i = 0; i < weeks.length; i++){
                var week_no = weeks[i].substring(1);
                site_surveys[i] = 0;
                infrastructure_constructions[i] = 0; 
                opt_network_constructions[i] = 0;
                customer_connections[i] = 0;            
                incoming_orders[i] = 0;
                backlog_orders[i] = 0;
                for (var j = 0; j < completed_tasks.user.length; j++) {
                    if ( (completed_tasks.Week[j] == week_no) && (this.value.includes(completed_tasks.user[j])) ) {
                        if (!co_options.includes(completed_tasks.central_office[j])) {
                            co_options.push(completed_tasks.central_office[j]);
                        }
                        if (!org_options.includes(completed_tasks.organisation[j])) {
                            org_options.push(completed_tasks.organisation[j]);
                        }
                        //if (!user_options.includes(completed_tasks.user[j])) {
                        //    user_options.push(completed_tasks.user[j]);
                        //}
                        if (!cat_options.includes(completed_tasks.category[j].substring(14))) {
                            cat_options.push(completed_tasks.category[j].substring(14));
                        }
                        if ( (multi_select_co.value.includes(completed_tasks.central_office[j])) && (multi_select_org.value.includes(completed_tasks.organisation[j])) && (this.value.includes(completed_tasks.user[j])) && (multi_select_categories.value.includes(completed_tasks.category[j].substring(14))) ) {
                            switch (completed_tasks.Task_Type_Ref[j]) {
                                case "Site_Survey":
                                    site_surveys[i] += 1;
                                    break;
                                case "Infrastructure_Construction":
                                    infrastructure_constructions[i] += 1;
                                    break;
                                case "Opt_Network_Construction":
                                    opt_network_constructions[i] += 1;
                                    break;
                                case "Customer_Connection":
                                    customer_connections[i] += 1;
                                    break;
                            }
                        }
                    }
                }        
                for (var j = 0; j < incoming_tasks.user.length; j++) {
                    if ( (incoming_tasks.Week[j] == week_no) && (this.value.includes(incoming_tasks.user[j])) ) {
                        if (!co_options.includes(incoming_tasks.central_office[j])) {
                            co_options.push(incoming_tasks.central_office[j]);
                        }
                        if (!org_options.includes(incoming_tasks.organisation[j])) {
                            org_options.push(incoming_tasks.organisation[j]);
                        }
                        if (!cat_options.includes(incoming_tasks.category[j].substring(14))) {
                            cat_options.push(incoming_tasks.category[j].substring(14));
                        }
                        if ( (multi_select_co.value.includes(incoming_tasks.central_office[j])) && (multi_select_org.value.includes(incoming_tasks.organisation[j])) && (this.value.includes(incoming_tasks.user[j])) && (multi_select_categories.value.includes(incoming_tasks.category[j].substring(14))) ) {
                            switch (incoming_tasks.Task_Type_Ref[j]) {
                                case "Site_Survey":
                                    incoming_orders[i] += 1;
                                    break;
                            }
                        }
                    }
                }        
                for (var j = 0; j < backlog_tasks.user.length; j++) {
                    if ( (backlog_tasks.Backlog_Week[j] == week_no) && (this.value.includes(backlog_tasks.user[j])) ) {
                        if (!co_options.includes(backlog_tasks.central_office[j])) {
                            co_options.push(backlog_tasks.central_office[j]);
                        }
                        if (!org_options.includes(backlog_tasks.organisation[j])) {
                            org_options.push(backlog_tasks.organisation[j]);
                        }
                        if (!cat_options.includes(backlog_tasks.category[j].substring(14))) {
                            cat_options.push(backlog_tasks.category[j].substring(14));
                        }
                        if ( (multi_select_co.value.includes(backlog_tasks.central_office[j])) && (multi_select_org.value.includes(backlog_tasks.organisation[j])) && (this.value.includes(backlog_tasks.user[j])) && (multi_select_categories.value.includes(backlog_tasks.category[j].substring(14))) ) {
                            switch (backlog_tasks.Task_Type_Ref[j]) {
                                case "Site_Survey":
                                    backlog_orders[i] += 1;
                                    break;
                            }
                        }
                    }
                }        
            }            
            source01.change.emit();
            multi_select_co.options = co_options.sort();
            multi_select_org.options = org_options.sort();
            //multi_select_users.options = user_options.sort();
            multi_select_categories.options = cat_options.sort();            
        """)
        multi_select_users.js_on_change("value", callback_users)

        callback_categories = CustomJS(args={'source01': source01, 'source_completed_tasks_df': source_completed_tasks_df, 'source_incoming_tasks_df': source_incoming_tasks_df, 'source_backlog_tasks_df': source_backlog_tasks_df,
                                     'multi_select_co': multi_select_co,
                                     'multi_select_org': multi_select_org,
                                     'multi_select_users': multi_select_users},
                                     #multi_select_categories': multi_select_categories},
                                     code=""" 
            var completed_tasks = source_completed_tasks_df.data;
            var incoming_tasks = source_incoming_tasks_df.data;
            var backlog_tasks = source_backlog_tasks_df.data;
            var weeks = source01.data.weeks;
            var co_options = [];
            var org_options = [];
            var user_options = [];
            //var cat_options = [];            
            var site_surveys = source01.data.Site_Surveys;
            var infrastructure_constructions = source01.data.Infrastructure_Constructions; 
            var opt_network_constructions = source01.data.Opt_Network_Constructions;
            var customer_connections = source01.data.Customer_Connections;            
            var incoming_orders = source01.data.Incoming_Orders;
            var backlog_orders = source01.data.Backlog_Orders;
            for (var i = 0; i < weeks.length; i++){
                var week_no = weeks[i].substring(1);
                site_surveys[i] = 0;
                infrastructure_constructions[i] = 0; 
                opt_network_constructions[i] = 0;
                customer_connections[i] = 0;            
                incoming_orders[i] = 0;
                backlog_orders[i] = 0;
                for (var j = 0; j < completed_tasks.category.length; j++) {
                    if ( (completed_tasks.Week[j] == week_no) && (completed_tasks.category[j] != 0) && (this.value.includes(completed_tasks.category[j].substring(14))) ) {
                        if (!co_options.includes(completed_tasks.central_office[j])) {
                            co_options.push(completed_tasks.central_office[j]);
                        }
                        if (!org_options.includes(completed_tasks.organisation[j])) {
                            org_options.push(completed_tasks.organisation[j]);
                        }
                        if (!user_options.includes(completed_tasks.user[j])) {
                            user_options.push(completed_tasks.user[j]);
                        }
                        //if (!cat_options.includes(completed_tasks.category[j].substring(14))) {
                        //    cat_options.push(completed_tasks.category[j].substring(14));
                        //}
                        if ( (multi_select_co.value.includes(completed_tasks.central_office[j])) && (multi_select_org.value.includes(completed_tasks.organisation[j])) && (multi_select_users.value.includes(completed_tasks.user[j])) && (this.value.includes(completed_tasks.category[j].substring(14))) ) {
                            switch (completed_tasks.Task_Type_Ref[j]) {
                                case "Site_Survey":
                                    site_surveys[i] += 1;
                                    break;
                                case "Infrastructure_Construction":
                                    infrastructure_constructions[i] += 1;
                                    break;
                                case "Opt_Network_Construction":
                                    opt_network_constructions[i] += 1;
                                    break;
                                case "Customer_Connection":
                                    customer_connections[i] += 1;
                                    break;
                            }
                        }
                    }
                }        
                for (var j = 0; j < incoming_tasks.category.length; j++) {
                    if ( (incoming_tasks.Week[j] == week_no) && (incoming_tasks.category[j] != 0) && (this.value.includes(incoming_tasks.category[j].substring(14))) ) {
                        if (!co_options.includes(incoming_tasks.central_office[j])) {
                            co_options.push(incoming_tasks.central_office[j]);
                        }
                        if (!org_options.includes(incoming_tasks.organisation[j])) {
                            org_options.push(incoming_tasks.organisation[j]);
                        }
                        if (!user_options.includes(incoming_tasks.user[j])) {
                            user_options.push(incoming_tasks.user[j]);
                        }
                        //if (!cat_options.includes(incoming_tasks.category[j].substring(14))) {
                        //    cat_options.push(incoming_tasks.category[j].substring(14));
                        //}
                        if ( (multi_select_co.value.includes(incoming_tasks.central_office[j])) && (multi_select_org.value.includes(incoming_tasks.organisation[j])) && (multi_select_users.value.includes(incoming_tasks.user[j])) && (this.value.includes(incoming_tasks.category[j].substring(14))) ) {
                            switch (incoming_tasks.Task_Type_Ref[j]) {
                                case "Site_Survey":
                                    incoming_orders[i] += 1;
                                    break;
                            }
                        }
                    }
                }        
                for (var j = 0; j < backlog_tasks.category.length; j++) {
                    if ( (backlog_tasks.Backlog_Week[j] == week_no) && (backlog_tasks.category[j] != 0) && (this.value.includes(backlog_tasks.category[j].substring(14))) ) {
                        if (!co_options.includes(backlog_tasks.central_office[j])) {
                            co_options.push(backlog_tasks.central_office[j]);
                        }
                        if (!org_options.includes(backlog_tasks.organisation[j])) {
                            org_options.push(backlog_tasks.organisation[j]);
                        }
                        if (!user_options.includes(backlog_tasks.user[j])) {
                            user_options.push(backlog_tasks.user[j]);
                        }
                        if ( (multi_select_co.value.includes(backlog_tasks.central_office[j])) && (multi_select_org.value.includes(backlog_tasks.organisation[j])) && (multi_select_users.value.includes(backlog_tasks.user[j])) && (this.value.includes(backlog_tasks.category[j].substring(14))) ) {
                            switch (backlog_tasks.Task_Type_Ref[j]) {
                                case "Site_Survey":
                                    backlog_orders[i] += 1;
                                    break;
                            }
                        }
                    }
                }        
            }            
            source01.change.emit();
            multi_select_co.options = co_options.sort();
            multi_select_org.options = org_options.sort();
            multi_select_users.options = user_options.sort();
            //multi_select_categories.options = cat_options.sort();            
        """)
        multi_select_categories.js_on_change("value", callback_categories)


        # tooltips = [
        #     ("week", "@weeks"),
        #     ('$name', "@Site_Surveys")
        # ]

        p1 = figure(x_range=weeks, plot_width=1000, plot_height=500, title="Tasks completed by week",
                   toolbar_location=None, tools="")

        r_ss = p1.vbar(x=dodge('weeks', -0.3, range=p1.x_range), top='Site_Surveys', width=0.18, source=source01,
                      color="#4B0082")

        hover_ss = HoverTool(tooltips="Site Surveys: @Site_Surveys", renderers=[r_ss])

        r_ic = p1.vbar(x=dodge('weeks', -0.1, range=p1.x_range), top='Infrastructure_Constructions', width=0.18,
                      source=source01, color="#718dbf")

        hover_ic = HoverTool(tooltips="Infrastructure Constructions: @Infrastructure_Constructions", renderers=[r_ic])

        r_onc = p1.vbar(x=dodge('weeks', 0.1, range=p1.x_range), top='Opt_Network_Constructions', width=0.18,
                       source=source01, color="#e84d60")

        hover_onc = HoverTool(tooltips="Opt. Network Constructions: @Opt_Network_Constructions", renderers=[r_onc])

        r_cc = p1.vbar(x=dodge('weeks', 0.3, range=p1.x_range), top='Customer_Connections', width=0.18, source=source01,
                      color="#006400")

        hover_cc = HoverTool(tooltips="Customer Connections: @Customer_Connections", renderers=[r_cc])

        # hover1 = HoverTool(tooltips='$name: @$name')
        p1.add_tools(hover_ss, hover_ic, hover_onc, hover_cc)
        p1.x_range.range_padding = 0.05
        p1.xgrid.grid_line_color = None

        from bokeh.models import Legend
        legend1 = Legend(items=[
            ('Site Surveys', [r_ss]),
            ('Infrastructure Constructions', [r_ic]),
            ('Opt. Network Constructions', [r_onc]),
            ('Customer_Connections', [r_cc])],
            location='bottom_left', click_policy="hide")
        p1.add_layout(legend1, 'below')

        # p1.legend.location = "bottom_left"
        # p1.legend.orientation = "vertical"
        # p1.legend.click_policy = "hide"
        # p1.legend.background_fill_alpha = 0.4
        # p1.legend.title_text_font = 'Arial'
        # p1.legend.title_text_font_size = '20pt'

        p2 = figure(x_range=weeks, plot_width=1000, plot_height=420, title="Incoming vs completed orders by week",
                   toolbar_location=None, tools="")

        r_io = p2.vbar(x=dodge('weeks', -0.15, range=p2.x_range), top='Incoming_Orders', width=0.28, source=source01,
                      color="#4B0082")

        hover_io = HoverTool(tooltips="Incoming Orders: @Incoming_Orders", renderers=[r_io])

        r_co = p2.vbar(x=dodge('weeks', 0.15, range=p2.x_range), top='Customer_Connections', width=0.28, source=source01,
                      color="#006400")

        hover_co = HoverTool(tooltips="Completed Orders: @Customer_Connections", renderers=[r_co])

        # hover1 = HoverTool(tooltips='$name: @$name')
        p2.add_tools(hover_io, hover_co)
        p2.x_range.range_padding = 0.05
        p2.xgrid.grid_line_color = None

        legend2 = Legend(items=[
            ('Incoming Orders', [r_io]),
            ('Completed Orders', [r_co])],
            location='bottom_left', click_policy="hide")
        p2.add_layout(legend2, 'below')

        p3 = figure(x_range=weeks, plot_width=1000, plot_height=370, title="Backlog of orders by week", toolbar_location=None, tools="")

        r_bo = p3.vbar(x=dodge('weeks', 0.0, range=p3.x_range), top='Backlog_Orders', width=0.4, source=source01,
                      color="#e84d60")

        hover_bo = HoverTool(tooltips="Orders Backlog: @Backlog_Orders", renderers=[r_bo])

        p3.add_tools(hover_bo)
        p3.x_range.range_padding = 0.05
        p3.xgrid.grid_line_color = None

        legend3 = Legend(items=[
            ('Orders Backlog', [r_bo])],
            location='bottom_left')
        p3.add_layout(legend3, 'below')

        layout_out = layout([multi_select_co, multi_select_org, multi_select_users, multi_select_categories], [p1], [p2], [p3])

        script, div = components(layout_out)
        return self.render(
            'admin/Dashboard.html',
            script_layout=script,
            div_layout=div,
            js_resources=INLINE.render_js(),
            css_resources=INLINE.render_css()
        )

