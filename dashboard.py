import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dash_table, dcc, callback, Output, Input, State
from dash import dcc
import plotly.express as px
import pandas as pd
import datetime as dt
from datetime import datetime

#############################################
# Check the file paths before running
#############################################
config = {
    'process_table_path': 'datasets/process_table.csv',
    'vendors_dataset_path': 'datasets/vendors_dataset.csv',
    'items_dataset_path': 'datasets/items_dataset.csv'
}

# For the time analysis
def is_weekday_or_weekend(input_date):

    try:

        if input_date.weekday() < 5:
            return "Weekday"
        else:
            return "Weekend"
    except:
        return 'NOT AVAILABLE'

# Which day of week -> for weekday/weekend analysis   
def day_of_week(input_date):
 
    try:
        if input_date.weekday() == 0:
            return "Monday"
        elif input_date.weekday() == 1:
            return "Tuesday"
        elif input_date.weekday() == 2:
            return "Wednesday"
        elif input_date.weekday() == 3:
            return "Thursday"
        elif input_date.weekday() == 4:
            return "Friday"
        elif input_date.weekday() == 5:
            return "Saturday"
        elif input_date.weekday() == 6:
            return "Sunday"
    except:
        return 'NOT AVAILABLE'

# Time str to datetime.time
def str_to_time(input_time):

    if isinstance(input_time, str):
        try:
            return datetime.strptime(input_time, '%H:%M:%S').time()
        except:
            return '<unknown>'
    elif isinstance(input_time, dt.time):
        return input_time
    else:
        return '<unknown>'

# Time str to datetime.date
def str_to_date(input_date):
    return datetime.strptime(input_date, '%Y-%m-%d').date()

# date field cleanser
def time_formatter(input_time):
    try:
        if input_time.count(':') == 1:
            input_time += ':00'
            return datetime.strptime(input_time, '%H:%M:%S').time()
        return datetime.strptime(input_time, '%H:%M:%S').time()
    except:
        return None


# date field cleanser
def date_formatter(input_date):
    try:
        month, day, year = input_date.split('/')

        if len(year) == 2:
            year = f'20{year}'

        input_date = f'{year}-{month}-{day}'

        return datetime.strptime(input_date, '%Y-%m-%d').date()
    except:
        return '<unknown>'

# To filter the dataframe based on the period selected
def df_filterer(start_time, end_time, start_date, end_date, df):
    # Parsing TIME period
    if start_time is None:
        start_time = str_to_time('00:00:00')
    else:
        start_time = str_to_time(start_time)
    if end_time is None:
        end_time = str_to_time('23:59:59')
    else:
        end_time = str_to_time(end_time)
        
    # Parsing DATE period
    if start_date is None:
        start_date = vendors_time_df['Date'].min()
    else:
        start_date = str_to_date(start_date)
    if end_date is None:
        end_date = vendors_time_df['Date'].max()
    else:
        end_date = str_to_date(end_date)
    
    
    filtered_df = df[(df['Time'] >= start_time) & (df['Time'] <= end_time)]
    filtered_df = filtered_df[(filtered_df['Date'] >= start_date) & (filtered_df['Date'] <= end_date)]
    
    return filtered_df

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'Receipts Analysis'

app.config.suppress_callback_exceptions = True
server = app.server

# Incorporating Datasets
receipts_info_df = pd.read_csv(config['process_table_path'])

vendors_df_full = pd.read_csv(config['vendors_dataset_path'])
vendors_df_full['Date'] = vendors_df_full['Date'].apply(lambda x: date_formatter(x))
vendors_df_full['Time'] = vendors_df_full['Time'].apply(lambda x: str_to_time(x))
vendors_df_full = vendors_df_full[vendors_df_full['Date'] != '<unknown>']
vendors_df_full = vendors_df_full[vendors_df_full['Time'] != '<unknown>']
vendors_df = vendors_df_full[['Vendor Name', 'Number of Items', 'Total Price ($)', 'Discount ($)', 'Tax ($)']]

vendors_classification_df_full = vendors_df_full[['Vendor Name', 'Number of Items', 'Total Price ($)', 'Discount ($)', 'Tax ($)', 'Category']]

vendor_name_count = vendors_classification_df_full['Vendor Name'].value_counts()
vendor_name_count_df = vendor_name_count.reset_index()
vendor_name_count_df.columns = ['Vendor Name', 'Number of Receipts']

vendor_category_count = vendors_classification_df_full['Category'].value_counts()
vendor_category_count_df = vendor_category_count.reset_index()
vendor_category_count_df.columns = ['Vendor Category', 'Number of Receipts']

vendors_classification_df = vendors_classification_df_full[['Category', 'Number of Items', 'Total Price ($)', 'Discount ($)', 'Tax ($)']]

vendors_time_df = vendors_df_full[['Vendor Name', 'Number of Items', 'Total Price ($)', 'Discount ($)', 'Tax ($)', 'Date', 'Time', 'Hour']]
vendors_weekday_df = vendors_time_df[['Vendor Name', 'Number of Items', 'Total Price ($)', 'Date', 'Time']]
vendors_weekday_df['Weekday or Weekend'] = vendors_weekday_df['Date'].apply(lambda x: is_weekday_or_weekend(x))

categories_time_df = vendors_df_full[['Category', 'Number of Items', 'Total Price ($)', 'Date', 'Time', 'Hour']]

categories_weekday_df = vendors_df_full[['Category', 'Number of Items', 'Total Price ($)', 'Date', 'Time']]
categories_weekday_df = categories_weekday_df.copy()
categories_weekday_df['Day of Week'] = categories_weekday_df['Date'].apply(lambda x: day_of_week(x))
categories_weekday_df['Weekday or Weekend'] = categories_weekday_df['Date'].apply(lambda x: is_weekday_or_weekend(x))

items_df_full = pd.read_csv(config['items_dataset_path'])
items_df_full['Date'] = items_df_full['Date'].apply(lambda x: date_formatter(x))
items_df_full['Time'] = items_df_full['Time'].apply(lambda x: str_to_time(x))
items_df_full = items_df_full[items_df_full['Date'] != '<unknown>']
items_df_full = items_df_full[items_df_full['Time'] != '<unknown>']

items_df = items_df_full[['Item Name', 'Unit Price ($)', 'Discount ($)']]

items_classification_df = items_df_full[['Item Category', 'Unit Price ($)', 'Discount ($)']]

# Hour Items for the dropdown
hours = [
    dbc.DropdownMenuItem("Hour 0 to 1"),
    dbc.DropdownMenuItem("Hour 1 to 2"),
    dbc.DropdownMenuItem("Hour 2 to 3"),
    dbc.DropdownMenuItem("Hour 3 to 4"),
    dbc.DropdownMenuItem("Hour 4 to 5"),
    dbc.DropdownMenuItem("Hour 5 to 6"),
    dbc.DropdownMenuItem("Hour 6 to 7"),
    dbc.DropdownMenuItem("Hour 7 to 8"),
    dbc.DropdownMenuItem("Hour 8 to 9"),
    dbc.DropdownMenuItem("Hour 9 to 10"),
    dbc.DropdownMenuItem("Hour 10 to 11"),
    dbc.DropdownMenuItem("Hour 11 to 12"),
    dbc.DropdownMenuItem("Hour 12 to 13"),
    dbc.DropdownMenuItem("Hour 13 to 14"),
    dbc.DropdownMenuItem("Hour 14 to 15"),
    dbc.DropdownMenuItem("Hour 15 to 16"),
    dbc.DropdownMenuItem("Hour 16 to 17"),
    dbc.DropdownMenuItem("Hour 17 to 18"),
    dbc.DropdownMenuItem("Hour 18 to 19"),
    dbc.DropdownMenuItem("Hour 19 to 20"),
    dbc.DropdownMenuItem("Hour 20 to 21"),
    dbc.DropdownMenuItem("Hour 21 to 22"),
    dbc.DropdownMenuItem("Hour 22 to 23"),
    dbc.DropdownMenuItem("Hour 23 to 24"),
]

# Receipt Info Section -> Modal Component
receipt_info_modal_body_style = {
    'maxWidth': '2000px',
    'height': 'auto'
}

receipt_info_modal = dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Cell Details")),
                dbc.ModalBody(html.Div(id="modal-body", style=receipt_info_modal_body_style)),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-modal", className="ml-auto")
                ),
            ],
            id="modal",
            is_open=False,
            size="lg"
        )


###########################################################################
###########################################################################
################################# SIDEBAR #################################
###########################################################################
########################################################################### 
# Function to create a collapsible section
def create_collapsible_section(title, subsections):
    return dbc.Card(
        [
            dbc.CardHeader(
                html.H2(
                    dbc.Button(
                        title,
                        color="link",
                        id=f"group-{title}-toggle",
                        style={"color": "inherit", "textDecoration": "none"}
                    )
                )
            ),
            dbc.Collapse(
                dbc.CardBody(subsections),
                id=f"collapse-{title}",
            ),
        ]
    )

# Sidebar Header
sidebar_header = html.Div(
    dcc.Link(
        html.H2("Receipt Data Analytics", className="display-4", style={'fontSize': '1.5rem'}),
        href="/",
        style={"color": "inherit", "textDecoration": "none"}
    )
)

# Receipts Info Section
receipts_analysis = create_collapsible_section(
    "Receipts Analysis",
    dbc.Nav(
            [
                dbc.NavLink("Process Table", href="/receipts-analysis/process-table", id="process-table",
                            style={"color": "inherit"}),
                dbc.NavLink("Vendors Count", href="/receipts-analysis/vendors-count", id="vendors-count",
                            style={"color": "inherit"}),
                dbc.NavLink("Categories Count", href="/receipts-analysis/categories-count", id="categories-count",
                            style={"color": "inherit"}),
                ],
            vertical=True,
            pills=True,
        )
)

# Vendors Analysis Section
vendors_analysis = create_collapsible_section(
    "Vendors Analysis",
    dbc.Nav(
            [
                dbc.NavLink("Vendor Name", href="/vendors-analysis/vendors-names", id="vendors-names",
                            style={"color": "inherit"}),
                dbc.NavLink("Vendor Category", href="/vendors-analysis/vendors-categories", id="vendors-categories",
                            style={"color": "inherit"})            ],
            vertical=True,
            pills=True,
        )
)

# Items Analysis Section
items_analysis = create_collapsible_section(
    "Items Analysis",
    dbc.Nav(
            [
                dbc.NavLink("Item Name", href="/items-analysis/items-names", id="items-names",
                            style={"color": "inherit"}),
                dbc.NavLink("Item Category", href="/items-analysis/items-categories", id="items-categories",
                            style={"color": "inherit"})
            ],
            vertical=True,
            pills=True,
        )
)

# Hourly Purchase Time Analysis
hourly_analysis = create_collapsible_section(
    "Hourly",
    dbc.Nav(
            [
                dbc.NavLink("Vendors", href="/purchase-time-analysis/hourly/vendors-comparison", id="time-analysis-hourly-vendors-comparison",
                            style={"color": "inherit"}),
                dbc.NavLink("Categories", href="/purchase-time-analysis/hourly/categories-comparison", id="time-analysis-hourly-categories-comparison",
                            style={"color": "inherit"}),
                dbc.NavLink("Vendor-Specific", href="/purchase-time-analysis/hourly/individual-vendor", id="time-analysis-hourly-individual-vendor",
                            style={"color": "inherit"}),
                dbc.NavLink("Category-Specific", href="/purchase-time-analysis/hourly/individual-category", id="time-analysis-hourly-individual-category",
                            style={"color": "inherit"})
            ],
            vertical=True,
            pills=True,
        )
)

# Weekday vs Weekend Purchase Time Analysis
weekday_analysis = create_collapsible_section(
    "Weekday/Weekend",
    dbc.Nav(
            [
                dbc.NavLink("Vendors", href="/purchase-time-analysis/weekday/vendors-comparison", id="time-analysis-weekday-vendors-comparison",
                            style={"color": "inherit"}),
                dbc.NavLink("Categories", href="/purchase-time-analysis/weekday/categories-comparison", id="time-analysis-weekday-categories-comparison",
                            style={"color": "inherit"}),
                dbc.NavLink("Vendor-Specific", href="/purchase-time-analysis/weekday/individual-vendor", id="time-analysis-weekday-individual-vendor",
                            style={"color": "inherit"}),
                dbc.NavLink("Category-Specific", href="/purchase-time-analysis/weekday/individual-category", id="time-analysis-weekday-individual-category",
                            style={"color": "inherit"})
            ],
            vertical=True,
            pills=True,
        )
)

# Purchase Time Analysis
purchase_time_analysis = create_collapsible_section(
    "Purchase Time Analysis",
    dbc.Nav(
            [
                hourly_analysis,
                weekday_analysis
            ],
            vertical=True,
            pills=True,
        )
)

# Define the sidebar layout
sidebar = dbc.Col(
    [sidebar_header,
     html.Hr(),
     receipts_analysis,
     vendors_analysis,
     items_analysis,
     purchase_time_analysis
    ],
    width=2,
    style={'margin-top': '30px',
           'position': 'sticky',
           'top': 0,
           'height': '100vh'}
)


###########################################################################
###########################################################################
############################# MAIN BOX CONTENT ############################
###########################################################################
########################################################################### 
receipts_process_table_content = dbc.Container([
    ##############################
    # RECEIPTS INFO
    ##############################

    dbc.Row([
        html.Div('Receipts Process Table', className="text-darkmagenta text-left fs-3 mb-3")
    ], style={'margin-top': '30px', 'margin-bottom': '20px'}),


    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id='receipt_process_table',
                data=receipts_info_df.to_dict('records'),
                page_size=12,
                style_cell={
                    'maxWidth': '50px',
                    'maxHeight': '20px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'whiteSpace': 'nowrap'}
                )
        ]),
    ]),
    receipt_info_modal
])

receipts_vendors_count = dbc.Container([

    dbc.Row([
        html.Div('Receipts Vendors Count Analysis', className="text-darkmagenta text-left fs-3 mb-3")
    ], style={'margin-top': '30px', 'margin-bottom': '20px'}),

    dbc.Row([
        # For the custom date period
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("Start Date"),
                dbc.Input(type="date", id="vendors-count-start-date")
            ], className="mb-3"),
        ], width=3),
        
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("End Date"),
                dbc.Input(type="date", id="vendors-count-end-date")
            ], className="mb-3"),
        ], width=3),
        
        # For the custom hour period
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("Start Time"),
                dbc.Input(type="time", id="vendors-count-start-time")
            ], className="mb-3"),
        ], width=3),
        
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("End Time"),
                dbc.Input(type="time", id="vendors-count-end-time")
            ], className="mb-3"),
        ], width=3),
    ]),
    
    dbc.Row([
        
        dbc.Col([
            dbc.RadioItems(options=[
                            {'label': 'Histogram', 'value': 'hist'},
                            {'label': 'Pie Chart', 'value': 'pie'}
                            ],
                       value='hist',
                       inline=True,
                       id='receipts-vendors-count-chart-radio-buttons')
        ], width=6),
    
        
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(figure={}, id='receipts-vendors-count-chart')
        ]),
        

    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id='vendors-count-table',
                data=vendor_name_count_df.to_dict('records'),
                columns=[{"name": i, "id": i, 'sortable': True} for i in vendor_name_count_df.columns],
                page_size=12,
                style_table={'overflowX': 'auto'},
                filter_action='native',
                sort_action='native',
                sort_mode='multi'
                )
        ]),
    ], style={'margin-bottom': '100px'})

])

receipts_categories_count = dbc.Container([
   
    dbc.Row([
        html.Div('Receipts Categories Count Analysis', className="text-darkmagenta text-left fs-3 mb-3")
    ], style={'margin-top': '30px', 'margin-bottom': '20px'}),

    dbc.Row([
        # For the custom date period
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("Start Date"),
                dbc.Input(type="date", id="categories-count-start-date")
            ], className="mb-3"),
        ], width=3),
        
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("End Date"),
                dbc.Input(type="date", id="categories-count-end-date")
            ], className="mb-3"),
        ], width=3),
        
        # For the custom hour period
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("Start Time"),
                dbc.Input(type="time", id="categories-count-start-time")
            ], className="mb-3"),
        ], width=3),
        
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("End Time"),
                dbc.Input(type="time", id="categories-count-end-time")
            ], className="mb-3"),
        ], width=3),
    ]),
    
    dbc.Row([
        
        dbc.Col([
            dbc.RadioItems(options=[
                            {'label': 'Histogram', 'value': 'hist'},
                            {'label': 'Pie Chart', 'value': 'pie'}
                            ],
                       value='hist',
                       inline=True,
                       id='receipts-categories-count-chart-radio-buttons')
        ])
        
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(figure={}, id='receipts-categories-count-chart')
        ]),
        

    ]),

    html.Hr(),
    
    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id='categories-count-table',
                data=vendor_category_count_df.to_dict('records'),
                columns=[{"name": i, "id": i, 'sortable': True} for i in vendor_category_count_df.columns],
                page_size=12,
                style_table={'overflowX': 'auto'},
                filter_action='native',
                sort_action='native',
                sort_mode='multi'
                )
        ]),
    ], style={'margin-bottom': '100px'})

])

vendors_name_content = dbc.Container([

    ##############################
    # VENDOR INFO
    ##############################
    dbc.Row([
        html.Div('Vendors Names Analysis', className="text-darkmagenta text-left fs-3 mb-3")
    ], style={'margin-top': '30px', 'margin-bottom': '20px'}),
    
    dbc.Row([
        # For the custom date period
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("Start Date"),
                dbc.Input(type="date", id="vendors-names-start-date")
            ], className="mb-3"),
        ], width=3),
        
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("End Date"),
                dbc.Input(type="date", id="vendors-names-end-date")
            ], className="mb-3"),
        ], width=3),
        
        # For the custom hour period
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("Start Time"),
                dbc.Input(type="time", id="vendors-names-start-time")
            ], className="mb-3"),
        ], width=3),
        
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("End Time"),
                dbc.Input(type="time", id="vendors-names-end-time")
            ], className="mb-3"),
        ], width=3),
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.RadioItems(options=[{"label": x, "value": x} for x in ['Number of Items', 'Total Price ($)', 'Discount ($)', 'Tax ($)']],
                       value='Number of Items',
                       inline=True,
                       id='vendors-radio-buttons')
        ], width=6),
        
        dbc.Col([
            dbc.RadioItems(options=[
                            {'label': 'Histogram', 'value': 'hist'},
                            {'label': 'Pie Chart', 'value': 'pie'}
                            ],
                       value='hist',
                       inline=True,
                       id='vendors-info-chart-radio-buttons')
        ], width=6)
        
    ], style={'margin-bottom': '20px'}),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure={}, id='vendors-chart')
        ])
    ]),
    
    html.Hr(),

    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id='vendors-names-table',
                data=vendors_df.to_dict('records'),
                columns=[{"name": i, "id": i, 'sortable': True} for i in vendors_df.columns],
                page_size=12,
                style_table={'overflowX': 'auto'},
                filter_action='native',
                sort_action='native',
                sort_mode='multi'
                )
        ]),
    ], style={'margin-bottom': '100px'}),
])

vendors_category_content = dbc.Container([
    
    ##############################
    # VENDOR CLASSIFICATION
    ##############################
    
    dbc.Row([
        html.Div('Vendors Categories Analysis', className="text-darkmagenta text-left fs-3 mb-3")
    ], style={'margin-top': '30px', 'margin-bottom': '20px'}),
    
    dbc.Row([
        # For the custom date period
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("Start Date"),
                dbc.Input(type="date", id="vendors-categories-start-date")
            ], className="mb-3"),
        ], width=3),
        
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("End Date"),
                dbc.Input(type="date", id="vendors-categories-end-date")
            ], className="mb-3"),
        ], width=3),
        
        # For the custom hour period
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("Start Time"),
                dbc.Input(type="time", id="vendors-categories-start-time")
            ], className="mb-3"),
        ], width=3),
        
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("End Time"),
                dbc.Input(type="time", id="vendors-categories-end-time")
            ], className="mb-3"),
        ], width=3),
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.RadioItems(options=[{"label": x, "value": x} for x in ['Number of Items', 'Total Price ($)', 'Discount ($)', 'Tax ($)']],
                       value='Number of Items',
                       inline=True,
                       id='vendors-classification-radio-buttons')
        ], width=6),
        
        dbc.Col([
            dbc.RadioItems(options=[
                            {'label': 'Histogram', 'value': 'hist'},
                            {'label': 'Pie Chart', 'value': 'pie'}
                            ],
                       value='hist',
                       inline=True,
                       id='vendors-classification-chart-radio-buttons')
        ], width=6)
        
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(figure={}, id='vendors-classification-chart')
        ]),
    ]),
    
    html.Hr(),

    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id='vendors-categories-table',
                data=vendors_classification_df.to_dict('records'),
                columns=[{"name": i, "id": i, 'sortable': True} for i in vendors_classification_df.columns],
                page_size=12,
                style_table={'overflowX': 'auto'},
                filter_action='native',
                sort_action='native',
                sort_mode='multi'
                )
        ]),
    ], style={'margin-bottom': '100px'}),
])

items_name_content = dbc.Container([
    ##############################
    # ITEMS ANALYSIS
    ##############################
    
    dbc.Row([
        html.Div('Items Names Analysis', className="text-darkmagenta text-left fs-3 mb-3")
    ], style={'margin-top': '30px', 'margin-bottom': '20px'}),
    
    dbc.Row([
        # For the custom date period
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("Start Date"),
                dbc.Input(type="date", id="items-names-start-date")
            ], className="mb-3"),
        ], width=3),
        
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("End Date"),
                dbc.Input(type="date", id="items-names-end-date")
            ], className="mb-3"),
        ], width=3),
        
        # For the custom hour period
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("Start Time"),
                dbc.Input(type="time", id="items-names-start-time")
            ], className="mb-3"),
        ], width=3),
        
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("End Time"),
                dbc.Input(type="time", id="items-names-end-time")
            ], className="mb-3"),
        ], width=3),
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.RadioItems(options=[{"label": x, "value": x} for x in ['Unit Price ($)', 'Discount ($)']],
                       value='Unit Price ($)',
                       inline=True,
                       id='items-classification-radio-buttons')
        ], width=6),
        
        dbc.Col([
            dbc.RadioItems(options=[
                            {'label': 'Histogram', 'value': 'hist'},
                            {'label': 'Pie Chart', 'value': 'pie'}
                            ],
                       value='hist',
                       inline=True,
                       id='items-classification-chart-radio-buttons')
        ], width=6)
        
    ]),

    dbc.Row([

        dbc.Col([
            dcc.Graph(figure={}, id='items-classification-chart')
        ]),
    ]),
    
    html.Hr(),

    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id='items-names-table',
                data=items_df.to_dict('records'),
                columns=[{"name": i, "id": i, 'sortable': True} for i in items_df.columns],
                page_size=12,
                style_table={'overflowX': 'auto'},
                filter_action='native',
                sort_action='native',
                sort_mode='multi'
                )
        ]),
    ], style={'margin-bottom': '100px'}),
])

items_category_content = dbc.Container([
    ##############################
    # ITEMS CLASSIFICATION
    ##############################
    
    dbc.Row([
        html.Div('Items Categories Analysis', className="text-darkmagenta text-left fs-3 mb-3")
    ], style={'margin-top': '30px', 'margin-bottom': '20px'}),
    
    dbc.Row([
        # For the custom date period
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("Start Date"),
                dbc.Input(type="date", id="items-categories-start-date")
            ], className="mb-3"),
        ], width=3),
        
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("End Date"),
                dbc.Input(type="date", id="items-categories-end-date")
            ], className="mb-3"),
        ], width=3),
        
        # For the custom hour period
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("Start Time"),
                dbc.Input(type="time", id="items-categories-start-time")
            ], className="mb-3"),
        ], width=3),
        
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("End Time"),
                dbc.Input(type="time", id="items-categories-end-time")
            ], className="mb-3"),
        ], width=3),
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.RadioItems(options=[{"label": x, "value": x} for x in ['Unit Price ($)', 'Discount ($)']],
                       value='Unit Price ($)',
                       inline=True,
                       id='items-categories-classification-radio-buttons')
        ], width=6),
        
        dbc.Col([
            dbc.RadioItems(options=[
                            {'label': 'Histogram', 'value': 'hist'},
                            {'label': 'Pie Chart', 'value': 'pie'}
                            ],
                       value='hist',
                       inline=True,
                       id='items-categories-classification-chart-radio-buttons')
        ], width=6)
        
    ]),

    dbc.Row([

        dbc.Col([
            dcc.Graph(figure={}, id='items-categories-classification-chart')
        ]),
    ]),
    
    html.Hr(),

    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id='items-categories-table',
                data=items_classification_df.to_dict('records'),
                columns=[{"name": i, "id": i, 'sortable': True} for i in items_classification_df.columns],
                page_size=12,
                style_table={'overflowX': 'auto'},
                filter_action='native',
                sort_action='native',
                sort_mode='multi'
                )
        ])
    ], style={'margin-bottom': '100px'}),
])

vendors_comparison_hourly_content = dbc.Container([
    ##########################################
    # PURCHASE TIME for all vendors
    ##########################################
    dbc.Row([
        html.Div('Hourly Purchase Time Analysis - Vendors Comparison', className="text-darkmagenta text-left fs-3 mb-3")
    ], style={'margin-top': '30px', 'margin-bottom': '20px'}),
    
    dbc.Row([
        dbc.Col([
            dcc.RadioItems(
                options=[
                    {'label': 'Number of Items', 'value': 'Number of Items'},
                    {'label': 'Total Price ($)', 'value': 'Total Price ($)'}
                ],
                value='Number of Items',
                inline=True,
                id='vendors-purchase-time-radio-buttons'
            )], width=6),
        
        dbc.Col(
            dcc.Dropdown(
                id='vendors-hour-selector',
                options=[{'label': f'{hour}:00', 'value': hour} for hour in range(24)],
                value=0,
                clearable=False 
            ), width=3)
        
    ]),

    dbc.Row([

        dbc.Col([
            dcc.Graph(figure={}, id='vendors-purchase-time-chart')
        ]),
    ]),
    
    html.Hr(),

    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id='vendors-comparison-hourly-table',
                data=vendors_time_df.to_dict('records'),
                columns=[{"name": i, "id": i, 'sortable': True} for i in vendors_time_df.columns],
                page_size=12,
                style_table={'overflowX': 'auto'},
                filter_action='native',
                sort_action='native',
                sort_mode='multi'
                )
        ]),
    ], style={'margin-bottom': '100px'}),
])

categories_comparison_hourly_content = dbc.Container([
    ##########################################
    # PURCHASE TIME for all categories
    ##########################################
    dbc.Row([
        html.Div('Hourly Purchase Time Analysis - Categories Comparison', className="text-darkmagenta text-left fs-3 mb-3")
    ], style={'margin-top': '30px', 'margin-bottom': '20px'}),
    
    dbc.Row([
        dbc.Col([
            dcc.RadioItems(
                options=[
                    {'label': 'Number of Items', 'value': 'Number of Items'},
                    {'label': 'Total Price ($)', 'value': 'Total Price ($)'}
                ],
                value='Number of Items',
                inline=True,
                id='categories-purchase-time-radio-buttons'
            )], width=6),
        
        dbc.Col(
            dcc.Dropdown(
                id='categories-hour-selector',
                options=[{'label': f'{hour}:00', 'value': hour} for hour in range(24)],
                value=0,
                clearable=False 
            ), width=3)
        
    ]),

    dbc.Row([

        dbc.Col([
            dcc.Graph(figure={}, id='categories-purchase-time-chart')
        ]),
    ]),
    
    html.Hr(),

    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id='categories-comparison-hourly-table',
                data=categories_time_df.to_dict('records'),
                columns=[{"name": i, "id": i, 'sortable': True} for i in categories_time_df.columns],
                page_size=12,
                style_table={'overflowX': 'auto'},
                filter_action='native',
                sort_action='native',
                sort_mode='multi'
                )
        ]),
    ], style={'margin-bottom': '100px'}),
])

individual_vendor_hourly_content = dbc.Container([
    ##########################################
    # PURCHASE TIME for each vendor separately
    ##########################################
    dbc.Row([
        html.Div('Hourly Purchase Time Analysis - Vendor-Specific', className="text-darkmagenta text-left fs-3 mb-3")
    ], style={'margin-top': '30px', 'margin-bottom': '20px'}),
    
    dbc.Row([
        dbc.Col([
            dcc.RadioItems(
                options=[
                    {'label': 'Number of Items', 'value': 'Number of Items'},
                    {'label': 'Total Price ($)', 'value': 'Total Price ($)'}
                ],
                value='Number of Items',
                inline=True,
                id='sep-vendor-purchase-time-radio-buttons'
            )], width=6),
        
        dbc.Col(html.Div([
            dcc.Dropdown(
                id='sep-vendor-hour-selector',
                options=[{'label': vendor, 'value': vendor} for vendor in vendors_time_df['Vendor Name'].unique()],
                value=vendors_time_df['Vendor Name'].unique()[0]  # default to first vendor
            )
        ]))
        
    ]),

    dbc.Row([

        dbc.Col([
            dcc.Graph(figure={}, id='sep-vendor-purchase-time-chart')
        ]),
    ]),
    
    html.Hr(),

    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id='sep-vendor-hourly-table',
                data=vendors_time_df.to_dict('records'),
                columns=[{"name": i, "id": i, 'sortable': True} for i in vendors_time_df.columns],
                page_size=12,
                style_table={'overflowX': 'auto'},
                filter_action='native',
                sort_action='native',
                sort_mode='multi'
                )
        ])
    ], style={'margin-bottom': '100px'}),
])

individual_category_hourly_content = dbc.Container([
    ##########################################
    # PURCHASE TIME for each category separately
    ##########################################
    dbc.Row([
        html.Div('Hourly Purchase Time Analysis - Category-Specific', className="text-darkmagenta text-left fs-3 mb-3")
    ], style={'margin-top': '30px', 'margin-bottom': '20px'}),
    
    dbc.Row([
        dbc.Col([
            dcc.RadioItems(
                options=[
                    {'label': 'Number of Items', 'value': 'Number of Items'},
                    {'label': 'Total Price ($)', 'value': 'Total Price ($)'}
                ],
                value='Number of Items',
                inline=True,
                id='sep-category-purchase-time-radio-buttons'
            )], width=6),
        
        dbc.Col(html.Div([
            dcc.Dropdown(
                id='sep-category-hour-selector',
                options=[{'label': category, 'value': category} for category in categories_time_df['Category'].unique()],
                value=categories_time_df['Category'].unique()[0]  # default to first vendor
            )
        ]))
        
    ]),

    dbc.Row([

        dbc.Col([
            dcc.Graph(figure={}, id='sep-category-purchase-time-chart')
        ]),
    ]),
    
    html.Hr(),

    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id='sep-category-hourly-table',
                data=categories_time_df.to_dict('records'),
                columns=[{"name": i, "id": i, 'sortable': True} for i in categories_time_df.columns],
                page_size=12,
                style_table={'overflowX': 'auto'},
                filter_action='native',
                sort_action='native',
                sort_mode='multi'
                )
        ])
    ], style={'margin-bottom': '100px'}),
])

vendors_comparison_weekday_content = dbc.Container([
    ##########################################
    # PURCHASE WEEKDAY for all vendors
    ##########################################
    dbc.Row([
        html.Div('Weekday vs. Weekend Purchase Time Analysis - Vendors Comparison', className="text-darkmagenta text-left fs-3 mb-3")
    ], style={'margin-top': '30px', 'margin-bottom': '20px'}),
    
    dbc.Row([
        dbc.Col([
            dcc.RadioItems(
                options=[
                    {'label': 'Number of Items', 'value': 'Number of Items'},
                    {'label': 'Total Price ($)', 'value': 'Total Price ($)'}
                ],
                value='Number of Items',
                inline=True,
                id='vendors-purchase-weekday-radio-buttons'
            )], width=6),
        
        dbc.Col(
            dcc.Dropdown(
                id='vendors-weekday-selector',
                options=[
                    {'label': 'Weekday', 'value': 'Weekday'},
                    {'label': 'Weekend', 'value': 'Weekend'}
                ],
                value='Weekday',
                clearable=False 
            ), width=3)
        
    ]),

    dbc.Row([

        dbc.Col([
            dcc.Graph(figure={}, id='vendors-purchase-weekday-chart')
        ]),
    ]),
    
    html.Hr(),

    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id='vendors-comparison-weekday-table',
                data=vendors_weekday_df.to_dict('records'),
                columns=[{"name": i, "id": i, 'sortable': True} for i in vendors_weekday_df.columns],
                page_size=12,
                style_table={'overflowX': 'auto'},
                filter_action='native',
                sort_action='native',
                sort_mode='multi'
                )
        ])
    ], style={'margin-bottom': '100px'}),
])

categories_comparison_weekday_content = dbc.Container([
    ##########################################
    # PURCHASE WEEKDAY for all categories
    ##########################################
    dbc.Row([
        html.Div('Weekday vs. Weekend Purchase Time Analysis - Categories Comparison', className="text-darkmagenta text-left fs-3 mb-3")
    ], style={'margin-top': '30px', 'margin-bottom': '20px'}),
    
    dbc.Row([
        dbc.Col([
            dcc.RadioItems(
                options=[
                    {'label': 'Number of Items', 'value': 'Number of Items'},
                    {'label': 'Total Price ($)', 'value': 'Total Price ($)'}
                ],
                value='Number of Items',
                inline=True,
                id='categories-purchase-weekday-radio-buttons'
            )], width=6),
        
        dbc.Col(
            dcc.Dropdown(
                id='categories-weekday-selector',
                options=[
                    {'label': 'Weekday', 'value': 'Weekday'},
                    {'label': 'Weekend', 'value': 'Weekend'}
                ],
                value='Weekday',
                clearable=False 
            ), width=3)
        
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(figure={}, id='categories-purchase-weekday-chart')
        ]),
    ]),
    
    html.Hr(),

    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id='categories-comparison-weekday-table',
                data=categories_weekday_df.to_dict('records'),
                columns=[{"name": i, "id": i, 'sortable': True} for i in categories_weekday_df.columns],
                page_size=12,
                style_table={'overflowX': 'auto'},
                filter_action='native',
                sort_action='native',
                sort_mode='multi'
                )
        ])
    ], style={'margin-bottom': '100px'}),
])

individual_vendor_weekday_content = dbc.Container([
    ##########################################
    # PURCHASE WEEKDAY for each vendor separately
    ##########################################
    dbc.Row([
        html.Div('Weekday vs. Weekend Purchase Time Analysis - Vendor-Specific', className="text-darkmagenta text-left fs-3 mb-3")
    ], style={'margin-top': '30px', 'margin-bottom': '20px'}),
    
    dbc.Row([
        dbc.Col([
            dcc.RadioItems(
                options=[
                    {'label': 'Number of Items', 'value': 'Number of Items'},
                    {'label': 'Total Price ($)', 'value': 'Total Price ($)'}
                ],
                value='Number of Items',
                inline=True,
                id='sep-vendor-purchase-weekday-radio-buttons'
            )], width=6),
        
        dbc.Col(html.Div([
            dcc.Dropdown(
                id='sep-vendor-weekday-selector',
                options=[{'label': vendor, 'value': vendor} for vendor in vendors_time_df['Vendor Name'].unique()],
                value=vendors_time_df['Vendor Name'].unique()[0]  # default to first vendor
            )
        ]))
        
    ]),

    dbc.Row([

        dbc.Col([
            dcc.Graph(figure={}, id='sep-vendor-purchase-weekday-chart')
        ]),
    ]),
    
    html.Hr(),

    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id='sep-vendor-weekday-table',
                data=vendors_weekday_df.to_dict('records'),
                columns=[{"name": i, "id": i, 'sortable': True} for i in vendors_weekday_df.columns],
                page_size=12,
                style_table={'overflowX': 'auto'},
                filter_action='native',
                sort_action='native',
                sort_mode='multi'
                )
        ])
    ], style={'margin-bottom': '100px'}),

])

individual_category_weekday_content = dbc.Container([
    ##########################################
    # PURCHASE WEEKDAY for each category separately
    ##########################################
    dbc.Row([
        html.Div('Weekday vs. Weekend Purchase Time Analysis - Category-Specific', className="text-darkmagenta text-left fs-3 mb-3")
    ], style={'margin-top': '30px', 'margin-bottom': '20px'}),
    
    dbc.Row([
        dbc.Col([
            dcc.RadioItems(
                options=[
                    {'label': 'Number of Items', 'value': 'Number of Items'},
                    {'label': 'Total Price ($)', 'value': 'Total Price ($)'}
                ],
                value='Number of Items',
                inline=True,
                id='sep-category-purchase-weekday-radio-buttons'
            )], width=6),
        
        dbc.Col(html.Div([
            dcc.Dropdown(
                id='sep-category-weekday-selector',
                options=[{'label': category, 'value': category} for category in categories_weekday_df['Category'].unique()],
                value=categories_weekday_df['Category'].unique()[0]  # default to first vendor
            )
        ]))
        
    ]),

    dbc.Row([

        dbc.Col([
            dcc.Graph(figure={}, id='sep-category-purchase-weekday-chart')
        ]),
    ]),
    
    html.Hr(),

    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id='sep-category-weekday-table',
                data=categories_weekday_df.to_dict('records'),
                columns=[{"name": i, "id": i, 'sortable': True} for i in categories_weekday_df.columns],
                page_size=12,
                style_table={'overflowX': 'auto'},
                filter_action='native',
                sort_action='native',
                sort_mode='multi'
                )
        ])
    ], style={'margin-bottom': '100px'}),
   
])

# Define the main content layout
content = dbc.Col(html.Div(id='page-content'), width=10)

# Combine sidebar and content
app.layout = dbc.Container(
    [
    dcc.Location(id='url', refresh=False),
    dbc.Row([sidebar, content])  
    ],
    fluid=True
)


###########################################################################
###########################################################################
################################ CALLBACKS ################################
###########################################################################
###########################################################################
# Callbacks for displaying different pages
@callback(
    Output('page-content', 'children'), [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/':
        return html.Div([
            receipts_process_table_content
        ])
    elif pathname == '/receipts-analysis/process-table':
        return html.Div([
            receipts_process_table_content
        ])
    elif pathname == '/receipts-analysis/vendors-count':
        return html.Div([
            receipts_vendors_count
        ])
    elif pathname == '/receipts-analysis/categories-count':
        return html.Div([
            receipts_categories_count
        ])
    elif pathname == '/vendors-analysis/vendors-names':
        return html.Div([
            vendors_name_content
        ])
    elif pathname == '/vendors-analysis/vendors-categories':
        return html.Div([
            vendors_category_content
        ])     
    elif pathname == '/items-analysis/items-names':
        return html.Div([
            items_name_content
        ])
    elif pathname == '/items-analysis/items-categories':
        return html.Div([
            items_category_content
        ])
    elif pathname == '/purchase-time-analysis/hourly/vendors-comparison':
        return html.Div([
            vendors_comparison_hourly_content
        ])
    elif pathname == '/purchase-time-analysis/hourly/categories-comparison':
        return html.Div([
            categories_comparison_hourly_content
        ])
    elif pathname == '/purchase-time-analysis/hourly/individual-vendor':
        return html.Div([
            individual_vendor_hourly_content
        ])
    elif pathname == '/purchase-time-analysis/hourly/individual-category':
        return html.Div([
            individual_category_hourly_content
        ])
    elif pathname == '/purchase-time-analysis/weekday/vendors-comparison':
        return html.Div([
            vendors_comparison_weekday_content
        ])
    elif pathname == '/purchase-time-analysis/weekday/categories-comparison':
        return html.Div([
            categories_comparison_weekday_content
        ])
    elif pathname == '/purchase-time-analysis/weekday/individual-vendor':
        return html.Div([
            individual_vendor_weekday_content
        ])
    elif pathname == '/purchase-time-analysis/weekday/individual-category':
        return html.Div([
            individual_category_weekday_content
        ])
    else:
        return html.Div([
            html.H3('404 :/')
        ], style={'margin-top': '200px', 'margin-left': '200px'})

# Callbacks for toggling the collapse
@callback(
    [Output(f"collapse-Receipts Analysis", "is_open"),
     Output(f"collapse-Vendors Analysis", "is_open"),
     Output(f"collapse-Items Analysis", "is_open"),
     Output(f"collapse-Purchase Time Analysis", "is_open"),
     Output(f"collapse-Hourly", "is_open"),
     Output(f"collapse-Weekday/Weekend", "is_open")],
    
    [Input(f"group-Receipts Analysis-toggle", "n_clicks"),
     Input(f"group-Vendors Analysis-toggle", "n_clicks"),
     Input(f"group-Items Analysis-toggle", "n_clicks"),
     Input(f"group-Purchase Time Analysis-toggle", "n_clicks"),
     Input(f"group-Hourly-toggle", "n_clicks"),
     Input(f"group-Weekday/Weekend-toggle", "n_clicks")],
    
    [State(f"collapse-Receipts Analysis", "is_open"),
     State(f"collapse-Vendors Analysis", "is_open"),
     State(f"collapse-Items Analysis", "is_open"),
     State(f"collapse-Purchase Time Analysis", "is_open"),
     State(f"collapse-Hourly", "is_open"),
     State(f"collapse-Weekday/Weekend", "is_open")],
)
def toggle_collapse(n1, n2, n3, n4, n5, n6, is_open1, is_open2, is_open3, is_open4, is_open5, is_open6):
    ctx = dash.callback_context

    if not ctx.triggered:
        return False, False, False, False, False, False
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "group-Receipts Analysis-toggle":
        return not is_open1, False, False, False, False, False
    elif button_id == "group-Vendors Analysis-toggle":
        return False, not is_open2, False, False, False, False
    elif button_id == "group-Items Analysis-toggle":
        return False, False, not is_open3, False, False, False
    elif button_id == "group-Purchase Time Analysis-toggle":
        return False, False, False, not is_open4, False, False
    elif button_id == "group-Hourly-toggle":
        return False, False, False, is_open4, not is_open5, False
    elif button_id == "group-Weekday/Weekend-toggle":
        return False, False, False, is_open4, False, not is_open6

    return False, False, False, False, False, False

# Callback for modal of receipts information 1
@callback(
    Output('modal', 'is_open'),
    [Input('receipt_process_table', 'active_cell'), Input('close-modal', 'n_clicks')],
    [State('modal', 'is_open')]
)
def toggle_modal(active_cell, n_clicks, is_open):
    if active_cell or n_clicks:
        return not is_open
    return is_open

# Callback for modal of receipts information 2
@callback(
    Output('modal-body', 'children'),
    [Input('receipt_process_table', 'active_cell')],
    [State('receipt_process_table', 'data')]
)
def update_modal_body(active_cell, data):
    if active_cell:
        row = active_cell['row']
        col = active_cell['column_id']
        cell_data = data[row][col]
        return html.Pre(cell_data)  # Using Pre for formatted text like JSON
    return "Click a cell"

# Callback for receipts vendors count section
@callback(
    [Output('receipts-vendors-count-chart', 'figure'),
     Output('vendors-count-table', 'data'),
     Output('vendors-count-table', 'columns'),],
    [Input('receipts-vendors-count-chart-radio-buttons', 'value'),
     Input('vendors-count-start-time', 'value'),
     Input('vendors-count-end-time', 'value'),
     Input('vendors-count-start-date', 'value'),
     Input('vendors-count-end-date', 'value'),]
)
def update_graph(graph_type, start_time, end_time, start_date, end_date):
    
    filtered_df = df_filterer(time_formatter(start_time), time_formatter(end_time), start_date, end_date, vendors_time_df)
    
    vendor_name_count = filtered_df['Vendor Name'].value_counts()
    vendor_name_count_df = vendor_name_count.reset_index()
    vendor_name_count_df.columns = ['Vendor Name', 'Number of Receipts']
    
    if graph_type == 'hist':
        fig = px.bar(vendor_name_count_df, x='Vendor Name', y='Number of Receipts', labels={'y':'Number of Receipts', 'index':'Vendor Name'})
    elif graph_type == 'pie':
        fig = px.pie(vendor_name_count, names=vendor_name_count.index, values=vendor_name_count.values, labels={'values':'Number of Receipts', 'index':'Vendor Name'})
    
    
    data = vendor_name_count_df.to_dict('records')
    columns = [{"name": i, "id": i, 'sortable': True} for i in vendor_name_count_df.columns]
    return fig, data, columns

# Callback for receipts categories count section
@callback(
    [Output('receipts-categories-count-chart', 'figure'),
     Output('categories-count-table', 'data'),
     Output('categories-count-table', 'columns')],
    [Input('receipts-categories-count-chart-radio-buttons', 'value'),
     Input('categories-count-start-time', 'value'),
     Input('categories-count-end-time', 'value'),
     Input('categories-count-start-date', 'value'),
     Input('categories-count-end-date', 'value'),]
)
def update_graph(graph_type, start_time, end_time, start_date, end_date):
    
    filtered_df = df_filterer(time_formatter(start_time), time_formatter(end_time), start_date, end_date, vendors_df_full)
    
    vendor_category_count = filtered_df['Category'].value_counts()
    vendor_category_count_df = vendor_category_count.reset_index()
    vendor_category_count_df.columns = ['Vendor Category', 'Number of Receipts']
    
    if graph_type == 'hist':
        # fig = px.bar(vendor_category_count, x=vendor_category_count.index, y=vendor_category_count.values, labels={'y':'Number of Receipts', 'index':'Vendor Category'})
        fig = px.bar(vendor_category_count_df, x='Vendor Category', y='Number of Receipts', labels={'y':'Number of Receipts', 'index':'Vendor Category'})
    elif graph_type == 'pie':
        fig = px.pie(vendor_category_count, names=vendor_category_count.index, values=vendor_category_count.values, labels={'values':'Number of Receipts', 'index':'Vendor Category'})
    
    data = vendor_category_count_df.to_dict('records')
    columns = [{"name": i, "id": i, 'sortable': True} for i in vendor_category_count_df.columns]
    return fig, data, columns

# Callback for the vendors information section
@callback(
    [Output('vendors-chart', 'figure'),
     Output('vendors-names-table', 'data'),
     Output('vendors-names-table', 'columns')],
    [Input('vendors-info-chart-radio-buttons', 'value'),
     Input('vendors-radio-buttons', 'value'),
     Input('vendors-names-start-time', 'value'),
     Input('vendors-names-end-time', 'value'),
     Input('vendors-names-start-date', 'value'),
     Input('vendors-names-end-date', 'value')]
)
def update_graph(chart_type, col_chosen, start_time, end_time, start_date, end_date):
    ctx_vendor_info = dash.callback_context
    
    filtered_df = df_filterer(time_formatter(start_time), time_formatter(end_time), start_date, end_date, vendors_time_df)
    filtered_df = filtered_df[['Vendor Name', 'Number of Items', 'Total Price ($)', 'Discount ($)', 'Tax ($)']]
    
    data = filtered_df.to_dict('records')
    columns = [{"name": i, "id": i, 'sortable': True} for i in filtered_df.columns]

    if not ctx_vendor_info.triggered:
        # Default action if no input has triggered the callback yet
        fig = px.histogram(filtered_df, x='Vendor Name', y=col_chosen, histfunc='avg')
    else:
        # Get the ID of the input that triggered the callback
        input_id = ctx_vendor_info.triggered[0]['prop_id'].split('.')[0]

        if (input_id == 'vendors-info-chart-radio-buttons' or input_id == 'vendors-radio-buttons' or
            input_id == 'vendors-names-start-time' or input_id == 'vendors-names-end-time' or
            input_id == 'vendors-names-start-date' or input_id == 'vendors-names-end-date'):
            if chart_type == 'hist':
                fig = px.histogram(filtered_df, x='Vendor Name', y=col_chosen, histfunc='avg')
            else:
                fig = px.pie(filtered_df, names='Vendor Name', values=col_chosen)
    
    return fig, data, columns

# Callback for the vendors classification section
@callback(
    [Output('vendors-classification-chart', 'figure'),
     Output('vendors-categories-table', 'data'),
     Output('vendors-categories-table', 'columns')],
    [Input('vendors-classification-chart-radio-buttons', 'value'),
     Input('vendors-classification-radio-buttons', 'value'),
     Input('vendors-categories-start-time', 'value'),
     Input('vendors-categories-end-time', 'value'),
     Input('vendors-categories-start-date', 'value'),
     Input('vendors-categories-end-date', 'value')]
)
def update_graph(chart_type, col_chosen, start_time, end_time, start_date, end_date):
    ctx_vendor_classification = dash.callback_context

    filtered_df = df_filterer(time_formatter(start_time), time_formatter(end_time), start_date, end_date, vendors_df_full)
    filtered_df = filtered_df[['Category', 'Number of Items', 'Total Price ($)', 'Discount ($)', 'Tax ($)']]

    data = filtered_df.to_dict('records')
    columns = [{"name": i, "id": i, 'sortable': True} for i in filtered_df.columns]

    if not ctx_vendor_classification.triggered:
        # Default action if no input has triggered the callback yet
        fig = px.histogram(filtered_df, x='Category', y=col_chosen, histfunc='avg')
    else:
        # Get the ID of the input that triggered the callback
        input_id = ctx_vendor_classification.triggered[0]['prop_id'].split('.')[0]

        if (input_id == 'vendors-classification-chart-radio-buttons' or input_id == 'vendors-classification-radio-buttons' or
            input_id == 'vendors-categories-start-time' or input_id == 'vendors-categories-end-time' or
            input_id == 'vendors-categories-start-date' or input_id == 'vendors-categories-end-date'):
            if chart_type == 'hist':
                fig = px.histogram(filtered_df, x='Category', y=col_chosen, histfunc='avg')
            else:
                fig = px.pie(filtered_df, names='Category', values=col_chosen)
    
    return fig, data, columns

# Callback for the vendors purchase hourly section
@callback(
    [Output('vendors-purchase-time-chart', 'figure'),
     Output('vendors-comparison-hourly-table', 'data'),
     Output('vendors-comparison-hourly-table', 'columns')],
    [Input('vendors-hour-selector', 'value'),
     Input('vendors-purchase-time-radio-buttons', 'value')]
)
def update_histogram(selected_hour, selected_metric):
    # Filter the DataFrame based on the selected hour
    filtered_df = vendors_time_df[vendors_time_df['Hour'].astype(int) == selected_hour]

    data = filtered_df.to_dict('records')
    columns = [{"name": i, "id": i, 'sortable': True} for i in filtered_df.columns]

    # Create a histogram based on the selected metric
    if selected_metric == 'Number of Items':
        fig = px.histogram(filtered_df, x='Vendor Name', y=selected_metric)
    else:  # selected_metric == 'Total Price ($)'
        fig = px.histogram(filtered_df, x='Vendor Name', y=selected_metric)

    fig.update_layout(title_text=f"Histogram of {selected_metric} at {selected_hour}")
    
    return fig, data, columns

# Callback for the vendors purchase weekday section
@callback(
    [Output('vendors-purchase-weekday-chart', 'figure'),
     Output('vendors-comparison-weekday-table', 'data'),
     Output('vendors-comparison-weekday-table', 'columns')],
    [Input('vendors-weekday-selector', 'value'),
     Input('vendors-purchase-weekday-radio-buttons', 'value')]
)
def update_histogram(selected_weekday, selected_metric):
    # Filter the DataFrame based on the selected hour
    filtered_df = vendors_weekday_df[vendors_weekday_df['Weekday or Weekend'] == selected_weekday]

    data = filtered_df.to_dict('records')
    columns = [{"name": i, "id": i, 'sortable': True} for i in filtered_df.columns]

    # Create a histogram based on the selected metric
    if selected_metric == 'Number of Items':
        fig = px.histogram(filtered_df, x='Vendor Name', y=selected_metric)
    else:  # selected_metric == 'Total Price ($)'
        fig = px.histogram(filtered_df, x='Vendor Name', y=selected_metric)

    fig.update_layout(title_text=f"Histogram of {selected_metric} at {selected_weekday}s")
    return fig, data, columns

# Callback for the categories purchase hourly section
@callback(
    [Output('categories-purchase-time-chart', 'figure'),
     Output('categories-comparison-hourly-table', 'data'),
     Output('categories-comparison-hourly-table', 'columns')],
    [Input('categories-hour-selector', 'value'),
     Input('categories-purchase-time-radio-buttons', 'value')]
)
def update_histogram(selected_hour, selected_metric):
    # Filter the DataFrame based on the selected hour
    filtered_df = categories_time_df[categories_time_df['Hour'].astype(int) == selected_hour]

    data = filtered_df.to_dict('records')
    columns = [{"name": i, "id": i, 'sortable': True} for i in filtered_df.columns]

    # Create a histogram based on the selected metric
    if selected_metric == 'Number of Items':
        fig = px.histogram(filtered_df, x='Category', y=selected_metric)
    else:  # selected_metric == 'Total Price ($)'
        fig = px.histogram(filtered_df, x='Category', y=selected_metric)

    fig.update_layout(title_text=f"Histogram of {selected_metric} at {selected_hour}")
    
    return fig, data, columns

# Callback for the categories purchase weekday section
@callback(
    [Output('categories-purchase-weekday-chart', 'figure'),
     Output('categories-comparison-weekday-table', 'data'),
     Output('categories-comparison-weekday-table', 'columns')],
    [Input('categories-weekday-selector', 'value'),
     Input('categories-purchase-weekday-radio-buttons', 'value')]
)
def update_histogram(selected_weekday, selected_metric):
    # Filter the DataFrame based on the selected hour
    filtered_df = categories_weekday_df[categories_weekday_df['Weekday or Weekend'] == selected_weekday]

    data = filtered_df.to_dict('records')
    columns = [{"name": i, "id": i, 'sortable': True} for i in filtered_df.columns]

    # Create a histogram based on the selected metric
    if selected_metric == 'Number of Items':
        fig = px.histogram(filtered_df, x='Category', y=selected_metric)
    else:  # selected_metric == 'Total Price ($)'
        fig = px.histogram(filtered_df, x='Category', y=selected_metric)

    fig.update_layout(title_text=f"Histogram of {selected_metric} at {selected_weekday}s")
    return fig, data, columns

# Callback for each sep vendor purchase hourly section
@callback(
    [Output('sep-vendor-purchase-time-chart', 'figure'),
     Output('sep-vendor-hourly-table', 'data'),
     Output('sep-vendor-hourly-table', 'columns')],
    [Input('sep-vendor-hour-selector', 'value'),
     Input('sep-vendor-purchase-time-radio-buttons', 'value')]
)
def update_histogram(selected_vendor, selected_metric):
    # Filter the DataFrame based on the selected hour
    filtered_df = vendors_time_df[vendors_time_df['Vendor Name'] == selected_vendor]

    data = filtered_df.to_dict('records')
    columns = [{"name": i, "id": i, 'sortable': True} for i in filtered_df.columns]

    # Create a histogram based on the selected metric
    if selected_metric == 'Number of Items':
        hourly_item_num = filtered_df.groupby('Hour')['Number of Items'].sum().reset_index()
        fig = px.bar(hourly_item_num, x='Hour', y='Number of Items', title=f"Sum of Number of Items by Hour for {selected_vendor}")
    else:  # selected_metric == 'Total Price ($)'
        hourly_sales = filtered_df.groupby('Hour')['Total Price ($)'].sum().reset_index()
        fig = px.bar(hourly_sales, x='Hour', y='Total Price ($)', title=f"Total Sales by Hour for {selected_vendor}")

    fig.update_layout(title_text=f"Histogram of {selected_metric} for {selected_vendor}")
    
    return fig, data, columns

# Callback for each sep vendor purchase weekday section
@callback(
    [Output('sep-vendor-purchase-weekday-chart', 'figure'),
     Output('sep-vendor-weekday-table', 'data'),
     Output('sep-vendor-weekday-table', 'columns')],
    [Input('sep-vendor-weekday-selector', 'value'),
     Input('sep-vendor-purchase-weekday-radio-buttons', 'value')]
)
def update_histogram(selected_vendor, selected_metric):
    # Filter the DataFrame based on the selected hour
    filtered_df = vendors_weekday_df[vendors_weekday_df['Vendor Name'] == selected_vendor]

    data = filtered_df.to_dict('records')
    columns = [{"name": i, "id": i, 'sortable': True} for i in filtered_df.columns]

    # Create a histogram based on the selected metric
    if selected_metric == 'Number of Items':
        hourly_item_num = filtered_df.groupby('Weekday or Weekend')['Number of Items'].mean().reset_index()
        fig = px.bar(hourly_item_num, x='Weekday or Weekend', y='Number of Items', title=f"Mean of Number of Items by Weekday/Weekend for {selected_vendor}")
    else:  # selected_metric == 'Total Price ($)'
        hourly_sales = filtered_df.groupby('Weekday or Weekend')['Total Price ($)'].mean().reset_index()
        fig = px.bar(hourly_sales, x='Weekday or Weekend', y='Total Price ($)', title=f"Sales Mean by Weekday/Weekend for {selected_vendor}")

    fig.update_layout(title_text=f"Mean of {selected_metric} for {selected_vendor}")
    return fig, data, columns

# Callback for each sep category purchase hourly section
@callback(
    [Output('sep-category-purchase-time-chart', 'figure'),
     Output('sep-category-hourly-table', 'data'),
     Output('sep-category-hourly-table', 'columns')],
    [Input('sep-category-hour-selector', 'value'),
     Input('sep-category-purchase-time-radio-buttons', 'value')]
)
def update_histogram(selected_category, selected_metric):
    # Filter the DataFrame based on the selected hour
    filtered_df = categories_time_df[categories_time_df['Category'] == selected_category]

    data = filtered_df.to_dict('records')
    columns = [{"name": i, "id": i, 'sortable': True} for i in filtered_df.columns]

    # Create a histogram based on the selected metric
    if selected_metric == 'Number of Items':
        hourly_item_num = filtered_df.groupby('Hour')['Number of Items'].sum().reset_index()
        fig = px.bar(hourly_item_num, x='Hour', y='Number of Items', title=f"Sum of Number of Items by Hour for {selected_category}")
    else:  # selected_metric == 'Total Price ($)'
        hourly_sales = filtered_df.groupby('Hour')['Total Price ($)'].sum().reset_index()
        fig = px.bar(hourly_sales, x='Hour', y='Total Price ($)', title=f"Total Sales by Hour for {selected_category}")

    fig.update_layout(title_text=f"Histogram of {selected_metric} for {selected_category}")
    
    return fig, data, columns

# Callback for each sep category purchase weekday section
@callback(
    [Output('sep-category-purchase-weekday-chart', 'figure'),
     Output('sep-category-weekday-table', 'data'),
     Output('sep-category-weekday-table', 'columns')],
    [Input('sep-category-weekday-selector', 'value'),
     Input('sep-category-purchase-weekday-radio-buttons', 'value')]
)
def update_histogram(selected_category, selected_metric):
    # Filter the DataFrame based on the selected hour
    filtered_df = categories_weekday_df[categories_weekday_df['Category'] == selected_category]

    data = filtered_df.to_dict('records')
    columns = [{"name": i, "id": i, 'sortable': True} for i in filtered_df.columns]

    # Create a histogram based on the selected metric
    if selected_metric == 'Number of Items':
        hourly_item_num = filtered_df.groupby('Weekday or Weekend')['Number of Items'].mean().reset_index()
        fig = px.bar(hourly_item_num, x='Weekday or Weekend', y='Number of Items', title=f"Mean of Number of Items by Weekday/Weekend for {selected_category}")
    else:  # selected_metric == 'Total Price ($)'
        hourly_sales = filtered_df.groupby('Weekday or Weekend')['Total Price ($)'].mean().reset_index()
        fig = px.bar(hourly_sales, x='Weekday or Weekend', y='Total Price ($)', title=f"Sales Mean by Weekday/Weekend for {selected_category}")

    fig.update_layout(title_text=f"Mean of {selected_metric} for {selected_category}")
    return fig, data, columns

# Callback for the items names section
@callback(
    [Output('items-classification-chart', 'figure'),
     Output('items-names-table', 'data'),
     Output('items-names-table', 'columns')],
    [Input('items-classification-chart-radio-buttons', 'value'),
     Input('items-classification-radio-buttons', 'value'),
     Input('items-names-start-time', 'value'),
     Input('items-names-end-time', 'value'),
     Input('items-names-start-date', 'value'),
     Input('items-names-end-date', 'value')]
)
def update_graph(chart_type, col_chosen, start_time, end_time, start_date, end_date):
    ctx_item_classification = dash.callback_context

    filtered_df = df_filterer(time_formatter(start_time), time_formatter(end_time), start_date, end_date, items_df_full)
    filtered_df = filtered_df[['Item Name', 'Unit Price ($)', 'Discount ($)']]

    data = filtered_df.to_dict('records')
    columns = [{"name": i, "id": i, 'sortable': True} for i in filtered_df.columns]

    if not ctx_item_classification.triggered:
        # Default action if no input has triggered the callback yet
        fig = px.histogram(filtered_df, x='Item Name', y=col_chosen, histfunc='avg')
    else:
        # Get the ID of the input that triggered the callback
        input_id = ctx_item_classification.triggered[0]['prop_id'].split('.')[0]

        if (input_id == 'items-classification-chart-radio-buttons' or input_id == 'items-classification-radio-buttons' or
            input_id == 'items-names-start-time' or input_id == 'items-names-end-time' or
            input_id == 'items-names-start-date' or input_id == 'items-names-end-date'):
            if chart_type == 'hist':
                fig = px.histogram(items_df, x='Item Name', y=col_chosen, histfunc='avg')
            else:
                fig = px.pie(items_df, names='Item Name', values=col_chosen)
    
    return fig, data, columns

# Callback for the items categories section
@callback(
    [Output('items-categories-classification-chart', 'figure'),
     Output('items-categories-table', 'data'),
     Output('items-categories-table', 'columns')],
    [Input('items-categories-classification-chart-radio-buttons', 'value'),
     Input('items-categories-classification-radio-buttons', 'value'),
     Input('items-categories-start-time', 'value'),
     Input('items-categories-end-time', 'value'),
     Input('items-categories-start-date', 'value'),
     Input('items-categories-end-date', 'value')]
)
def update_graph(chart_type, col_chosen, start_time, end_time, start_date, end_date):
    ctx_item_categories_classification = dash.callback_context

    filtered_df = df_filterer(time_formatter(start_time), time_formatter(end_time), start_date, end_date, items_df_full)
    filtered_df = filtered_df[['Item Category', 'Unit Price ($)', 'Discount ($)']]

    data = filtered_df.to_dict('records')
    columns = [{"name": i, "id": i, 'sortable': True} for i in filtered_df.columns]

    if not ctx_item_categories_classification.triggered:
        # Default action if no input has triggered the callback yet
        fig = px.histogram(filtered_df, x='Item Category', y=col_chosen, histfunc='avg')
    else:
        # Get the ID of the input that triggered the callback
        input_id = ctx_item_categories_classification.triggered[0]['prop_id'].split('.')[0]

        if (input_id == 'items-categories-classification-chart-radio-buttons' or
            input_id == 'items-categories-classification-radio-buttons' or
            input_id == 'items-categories-start-time' or input_id == 'items-categories-end-time' or
            input_id == 'items-categories-start-date' or input_id == 'items-categories-end-date'):
            if chart_type == 'hist':
                fig = px.histogram(filtered_df, x='Item Category', y=col_chosen, histfunc='avg')
            else:
                fig = px.pie(filtered_df, names='Item Category', values=col_chosen)
    
    return fig, data, columns


if __name__ == '__main__':
    app.run_server(debug=False)
