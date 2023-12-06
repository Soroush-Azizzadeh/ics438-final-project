# Import packages
import dash
from dash import Dash, html, dash_table, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

from datetime import datetime

# For the analysis of weekday vs weekend purchases
def is_weekday_or_weekend(input_date):
    input_date = datetime.strptime(input_date, "%Y-%m-%d %H:%M:%S")

    if input_date.weekday() < 5:
        return "Weekday"
    else:
        return "Weekend"

# Incorporate data
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')

receipts_info_df = pd.read_csv('https://raw.githubusercontent.com/Soroush-Azizzadeh/ics438-final-project/main/datasets/test_receipt_information.csv')

vendors_df = pd.read_csv('https://raw.githubusercontent.com/Soroush-Azizzadeh/ics438-final-project/main/datasets/synthetic_vendors_dataset.csv')

vendors_classification_df = pd.read_csv('https://raw.githubusercontent.com/Soroush-Azizzadeh/ics438-final-project/main/datasets/synthetic_receipts_dataset_with_category.csv')
vendors_classification_df = vendors_classification_df[['Category', 'Number of Items', 'Total Price ($)', 'Discount ($)', 'Tax ($)']]

vendors_time_df = pd.read_csv('https://raw.githubusercontent.com/Soroush-Azizzadeh/ics438-final-project/main/datasets/synthetic_receipts_dataset_with_time.csv')
vendors_time_df['Hour'] = pd.to_datetime(vendors_time_df['Time']).dt.hour
vendors_time_df = vendors_time_df[['Vendor Name', 'Number of Items', 'Total Price ($)', 'Time', 'Hour']]

vendors_weekday_df = vendors_time_df[['Vendor Name', 'Number of Items', 'Total Price ($)', 'Time']]
vendors_weekday_df['Weekday or Weekend'] = vendors_weekday_df['Time'].apply(lambda x: is_weekday_or_weekend(x))

categories_time_df = pd.read_csv('https://raw.githubusercontent.com/Soroush-Azizzadeh/ics438-final-project/main/datasets/synthetic_receipts_dataset_with_time.csv')
categories_time_df['Hour'] = pd.to_datetime(categories_time_df['Time']).dt.hour
categories_time_df = categories_time_df[['Category', 'Number of Items', 'Total Price ($)', 'Time', 'Hour']]

categories_weekday_df = pd.read_csv('https://raw.githubusercontent.com/Soroush-Azizzadeh/ics438-final-project/main/datasets/synthetic_receipts_dataset_with_time.csv')
categories_weekday_df = categories_weekday_df[['Category', 'Number of Items', 'Total Price ($)', 'Time']]
categories_weekday_df['Weekday or Weekend'] = categories_weekday_df['Time'].apply(lambda x: is_weekday_or_weekend(x))

items_df = pd.read_csv('https://raw.githubusercontent.com/Soroush-Azizzadeh/ics438-final-project/main/datasets/synthetic_items_dataset.csv')
items_df = items_df[['Item Name', 'Unit Price ($)', 'Discount ($)', 'Tax ($)']]

items_classification_df = pd.read_csv('https://raw.githubusercontent.com/Soroush-Azizzadeh/ics438-final-project/main/datasets/synthetic_items_dataset.csv')
items_classification_df = items_classification_df[['Item Name', 'Item Category', 'Unit Price ($)', 'Discount ($)', 'Tax ($)']]

# Initialize the app - incorporate css
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

modal_body_style = {
    'maxWidth': '2000px',
    'height': 'auto'
}

# Modal Component
receipt_info_modal = dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Cell Details")),
                dbc.ModalBody(html.Div(id="modal-body", style=modal_body_style)),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-modal", className="ml-auto")
                ),
            ],
            id="modal",
            is_open=False
        )

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

# App layout
app.layout = dbc.Container([
    
    ##############################
    # HEADER
    ##############################
    dbc.Row([
        html.Div('Receipts Analysis Dashboard', className="text-primary text-center fs-3")
    ]),
    
    html.Hr(),
    
    ##############################
    # RECEIPTS INFO
    ##############################
    dbc.Row([
        html.Div('Receipts Information', className="text-darkmagenta text-left fs-3 mb-3")
    ]),
    
    html.Div(className='row', children=[
        dash_table.DataTable(
            id='receipt_info_table',
            data=receipts_info_df.to_dict('records'),
            page_size=11,
            style_table={'overflowX': 'auto'},
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'lineHeight': '15px'
            })
    ]),
    receipt_info_modal,
    
    html.Hr(),
    
    ##############################
    # VENDOR INFO
    ##############################
    dbc.Row([
        html.Div('Vendors Information Analysis', className="text-darkmagenta text-left fs-3 mb-3")
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
        
    ]),

    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                data=vendors_df.to_dict('records'),
                page_size=12,
                style_table={'overflowX': 'auto'}
                )
        ], width=6),

        dbc.Col([
            dcc.Graph(figure={}, id='vendors-chart')
        ], width=6),
    ]),
    
    html.Hr(),
    
    
    ##############################
    # VENDOR CLASSIFICATION
    ##############################
    
    dbc.Row([
        html.Div('Vendors Classification Analysis', className="text-darkmagenta text-left fs-3 mb-3")
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
            dash_table.DataTable(
                data=vendors_classification_df.to_dict('records'),
                page_size=12,
                style_table={'overflowX': 'auto'}
                )
        ], width=6),

        dbc.Col([
            dcc.Graph(figure={}, id='vendors-classification-chart')
        ], width=6),
    ]),
    
    html.Hr(),
    
    
    ##########################################
    # PURCHASE TIME for all vendors
    ##########################################
    dbc.Row([
        html.Div('Purchase Time Analysis for all the Vendors', className="text-darkmagenta text-left fs-3 mb-3")
    ]),
    
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
            dash_table.DataTable(
                data=vendors_time_df.to_dict('records'),
                page_size=12,
                style_table={'overflowX': 'auto'}
                )
        ], width=6),

        dbc.Col([
            dcc.Graph(figure={}, id='vendors-purchase-time-chart')
        ], width=6),
    ]),
    
    html.Hr(),


    ##########################################
    # PURCHASE WEEKDAY for all vendors
    ##########################################
    dbc.Row([
        html.Div('Purchase Weekday Analysis for all the Vendors', className="text-darkmagenta text-left fs-3 mb-3")
    ]),
    
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
            dash_table.DataTable(
                data=vendors_weekday_df.to_dict('records'),
                page_size=12,
                style_table={'overflowX': 'auto'}
                )
        ], width=6),

        dbc.Col([
            dcc.Graph(figure={}, id='vendors-purchase-weekday-chart')
        ], width=6),
    ]),
    
    html.Hr(),


    ##########################################
    # PURCHASE TIME for all categories
    ##########################################
    dbc.Row([
        html.Div('Purchase Time Analysis for all categories', className="text-darkmagenta text-left fs-3 mb-3")
    ]),
    
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
            dash_table.DataTable(
                data=categories_time_df.to_dict('records'),
                page_size=12,
                style_table={'overflowX': 'auto'}
                )
        ], width=6),

        dbc.Col([
            dcc.Graph(figure={}, id='categories-purchase-time-chart')
        ], width=6),
    ]),
    
    html.Hr(),

    ##########################################
    # PURCHASE WEEKDAY for all categories
    ##########################################
    dbc.Row([
        html.Div('Purchase Weekday Analysis for all categories', className="text-darkmagenta text-left fs-3 mb-3")
    ]),
    
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
            dash_table.DataTable(
                data=categories_weekday_df.to_dict('records'),
                page_size=12,
                style_table={'overflowX': 'auto'}
                )
        ], width=6),

        dbc.Col([
            dcc.Graph(figure={}, id='categories-purchase-weekday-chart')
        ], width=6),
    ]),
    
    html.Hr(),

    ##########################################
    # PURCHASE TIME for each vendor separately
    ##########################################
    dbc.Row([
        html.Div('Purchase Time Analysis for each vendor separately', className="text-darkmagenta text-left fs-3 mb-3")
    ]),
    
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
            dash_table.DataTable(
                data=vendors_time_df.to_dict('records'),
                page_size=12,
                style_table={'overflowX': 'auto'}
                )
        ], width=6),

        dbc.Col([
            dcc.Graph(figure={}, id='sep-vendor-purchase-time-chart')
        ], width=6),
    ]),
    
    html.Hr(),


    ##########################################
    # PURCHASE WEEKDAY for each vendor separately
    ##########################################
    dbc.Row([
        html.Div('Purchase Weekday Analysis for each vendor separately', className="text-darkmagenta text-left fs-3 mb-3")
    ]),
    
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
            dash_table.DataTable(
                data=vendors_weekday_df.to_dict('records'),
                page_size=12,
                style_table={'overflowX': 'auto'}
                )
        ], width=6),

        dbc.Col([
            dcc.Graph(figure={}, id='sep-vendor-purchase-weekday-chart')
        ], width=6),
    ]),
    
    html.Hr(),


    ##########################################
    # PURCHASE TIME for each category separately
    ##########################################
    dbc.Row([
        html.Div('Purchase Time Analysis for each category separately', className="text-darkmagenta text-left fs-3 mb-3")
    ]),
    
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
            dash_table.DataTable(
                data=categories_time_df.to_dict('records'),
                page_size=12,
                style_table={'overflowX': 'auto'}
                )
        ], width=6),

        dbc.Col([
            dcc.Graph(figure={}, id='sep-category-purchase-time-chart')
        ], width=6),
    ]),
    
    html.Hr(),

    ##########################################
    # PURCHASE WEEKDAY for each category separately
    ##########################################
    dbc.Row([
        html.Div('Purchase Weekday Analysis for each category separately', className="text-darkmagenta text-left fs-3 mb-3")
    ]),
    
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
            dash_table.DataTable(
                data=categories_weekday_df.to_dict('records'),
                page_size=12,
                style_table={'overflowX': 'auto'}
                )
        ], width=6),

        dbc.Col([
            dcc.Graph(figure={}, id='sep-category-purchase-weekday-chart')
        ], width=6),
    ]),
    
    html.Hr(),



    ##############################
    # ITEMS ANALYSIS
    ##############################
    
    dbc.Row([
        html.Div('Items Classification Analysis', className="text-darkmagenta text-left fs-3 mb-3")
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.RadioItems(options=[{"label": x, "value": x} for x in ['Unit Price ($)', 'Discount ($)', 'Tax ($)']],
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
            dash_table.DataTable(
                data=items_df.to_dict('records'),
                page_size=12,
                style_table={'overflowX': 'auto'}
                )
        ], width=6),

        dbc.Col([
            dcc.Graph(figure={}, id='items-classification-chart')
        ], width=6),
    ]),
    
    html.Hr(),

    ##############################
    # ITEMS CLASSIFICATION
    ##############################
    
    dbc.Row([
        html.Div('Items Classification Analysis', className="text-darkmagenta text-left fs-3 mb-3")
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.RadioItems(options=[{"label": x, "value": x} for x in ['Unit Price ($)', 'Discount ($)', 'Tax ($)']],
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
            dash_table.DataTable(
                data=items_classification_df.to_dict('records'),
                page_size=12,
                style_table={'overflowX': 'auto'}
                )
        ], width=6),

        dbc.Col([
            dcc.Graph(figure={}, id='items-categories-classification-chart')
        ], width=6),
    ]),
    
    html.Hr(),


], fluid=True, style={'margin-right': '100px'})

#######################
# CALLBACKS
#######################

# Callback for the vendors information section
@callback(
    Output('vendors-chart', 'figure'),
    [Input('vendors-info-chart-radio-buttons', 'value'),
     Input('vendors-radio-buttons', 'value')]
)
def update_graph(chart_type, col_chosen):
    ctx_vendor_info = dash.callback_context

    if not ctx_vendor_info.triggered:
        # Default action if no input has triggered the callback yet
        fig = px.histogram(vendors_df, x='Vendor Name', y=col_chosen, histfunc='avg')
    else:
        # Get the ID of the input that triggered the callback
        input_id = ctx_vendor_info.triggered[0]['prop_id'].split('.')[0]

        if input_id == 'vendors-info-chart-radio-buttons':
            if chart_type == 'hist':
                fig = px.histogram(vendors_df, x='Vendor Name', y=col_chosen, histfunc='avg')
            else:
                fig = px.pie(vendors_df, names='Vendor Name', values=col_chosen)
        elif input_id == 'vendors-radio-buttons':
            if chart_type == 'hist':
                fig = px.histogram(vendors_df, x='Vendor Name', y=col_chosen, histfunc='avg')
            else:
                fig = px.pie(vendors_df, names='Vendor Name', values=col_chosen)
    
    return fig

# Callback for the vendors classification section
@callback(
    Output('vendors-classification-chart', 'figure'),
    [Input('vendors-classification-chart-radio-buttons', 'value'),
     Input('vendors-classification-radio-buttons', 'value')]
)
def update_graph(chart_type, col_chosen):
    ctx_vendor_classification = dash.callback_context

    if not ctx_vendor_classification.triggered:
        # Default action if no input has triggered the callback yet
        fig = px.histogram(vendors_classification_df, x='Category', y=col_chosen, histfunc='avg')
    else:
        # Get the ID of the input that triggered the callback
        input_id = ctx_vendor_classification.triggered[0]['prop_id'].split('.')[0]

        if input_id == 'vendors-classification-chart-radio-buttons':
            if chart_type == 'hist':
                fig = px.histogram(vendors_classification_df, x='Category', y=col_chosen, histfunc='avg')
            else:
                fig = px.pie(vendors_classification_df, names='Category', values=col_chosen)
        elif input_id == 'vendors-classification-radio-buttons':
            if chart_type == 'hist':
                fig = px.histogram(vendors_classification_df, x='Category', y=col_chosen, histfunc='avg')
            else:
                fig = px.pie(vendors_classification_df, names='Category', values=col_chosen)
    
    return fig


# Callback for the vendors purchase time section
@callback(
    Output('vendors-purchase-time-chart', 'figure'),
    [Input('vendors-hour-selector', 'value'),
     Input('vendors-purchase-time-radio-buttons', 'value')]
)
def update_histogram(selected_hour, selected_metric):
    # Filter the DataFrame based on the selected hour
    filtered_df = vendors_time_df[vendors_time_df['Hour'] == selected_hour]

    # Create a histogram based on the selected metric
    if selected_metric == 'Number of Items':
        fig = px.histogram(filtered_df, x='Vendor Name', y=selected_metric)
    else:  # selected_metric == 'Total Price ($)'
        fig = px.histogram(filtered_df, x='Vendor Name', y=selected_metric)

    fig.update_layout(title_text=f"Histogram of {selected_metric} at {selected_hour}:00")
    return fig

# Callback for the vendors purchase weekday section
@callback(
    Output('vendors-purchase-weekday-chart', 'figure'),
    [Input('vendors-weekday-selector', 'value'),
     Input('vendors-purchase-weekday-radio-buttons', 'value')]
)
def update_histogram(selected_weekday, selected_metric):
    # Filter the DataFrame based on the selected hour
    filtered_df = vendors_weekday_df[vendors_weekday_df['Weekday or Weekend'] == selected_weekday]

    # Create a histogram based on the selected metric
    if selected_metric == 'Number of Items':
        fig = px.histogram(filtered_df, x='Vendor Name', y=selected_metric)
    else:  # selected_metric == 'Total Price ($)'
        fig = px.histogram(filtered_df, x='Vendor Name', y=selected_metric)

    fig.update_layout(title_text=f"Histogram of {selected_metric} at {selected_weekday}s")
    return fig

# Callback for the categories purchase time section
@callback(
    Output('categories-purchase-time-chart', 'figure'),
    [Input('categories-hour-selector', 'value'),
     Input('categories-purchase-time-radio-buttons', 'value')]
)
def update_histogram(selected_hour, selected_metric):
    # Filter the DataFrame based on the selected hour
    filtered_df = categories_time_df[categories_time_df['Hour'] == selected_hour]

    # Create a histogram based on the selected metric
    if selected_metric == 'Number of Items':
        fig = px.histogram(filtered_df, x='Category', y=selected_metric)
    else:  # selected_metric == 'Total Price ($)'
        fig = px.histogram(filtered_df, x='Category', y=selected_metric)

    fig.update_layout(title_text=f"Histogram of {selected_metric} at {selected_hour}:00")
    return fig

# Callback for the categories purchase weekday section
@callback(
    Output('categories-purchase-weekday-chart', 'figure'),
    [Input('categories-weekday-selector', 'value'),
     Input('categories-purchase-weekday-radio-buttons', 'value')]
)
def update_histogram(selected_weekday, selected_metric):
    # Filter the DataFrame based on the selected hour
    filtered_df = categories_weekday_df[categories_weekday_df['Weekday or Weekend'] == selected_weekday]

    # Create a histogram based on the selected metric
    if selected_metric == 'Number of Items':
        fig = px.histogram(filtered_df, x='Category', y=selected_metric)
    else:  # selected_metric == 'Total Price ($)'
        fig = px.histogram(filtered_df, x='Category', y=selected_metric)

    fig.update_layout(title_text=f"Histogram of {selected_metric} at {selected_weekday}s")
    return fig

# Callback for each sep vendor purchase time section
@callback(
    Output('sep-vendor-purchase-time-chart', 'figure'),
    [Input('sep-vendor-hour-selector', 'value'),
     Input('sep-vendor-purchase-time-radio-buttons', 'value')]
)
def update_histogram(selected_vendor, selected_metric):
    # Filter the DataFrame based on the selected hour
    filtered_df = vendors_time_df[vendors_time_df['Vendor Name'] == selected_vendor]

    # Create a histogram based on the selected metric
    if selected_metric == 'Number of Items':
        hourly_item_num = filtered_df.groupby('Hour')['Number of Items'].sum().reset_index()
        fig = px.bar(hourly_item_num, x='Hour', y='Number of Items', title=f"Sum of Number of Items by Hour for {selected_vendor}")
    else:  # selected_metric == 'Total Price ($)'
        hourly_sales = filtered_df.groupby('Hour')['Total Price ($)'].sum().reset_index()
        fig = px.bar(hourly_sales, x='Hour', y='Total Price ($)', title=f"Total Sales by Hour for {selected_vendor}")

    fig.update_layout(title_text=f"Histogram of {selected_metric} for {selected_vendor}")
    return fig

# Callback for each sep vendor purchase weekday section
@callback(
    Output('sep-vendor-purchase-weekday-chart', 'figure'),
    [Input('sep-vendor-weekday-selector', 'value'),
     Input('sep-vendor-purchase-weekday-radio-buttons', 'value')]
)
def update_histogram(selected_vendor, selected_metric):
    # Filter the DataFrame based on the selected hour
    filtered_df = vendors_weekday_df[vendors_weekday_df['Vendor Name'] == selected_vendor]

    # Create a histogram based on the selected metric
    if selected_metric == 'Number of Items':
        hourly_item_num = filtered_df.groupby('Weekday or Weekend')['Number of Items'].mean().reset_index()
        fig = px.bar(hourly_item_num, x='Weekday or Weekend', y='Number of Items', title=f"Mean of Number of Items by Weekday/Weekend for {selected_vendor}")
    else:  # selected_metric == 'Total Price ($)'
        hourly_sales = filtered_df.groupby('Weekday or Weekend')['Total Price ($)'].mean().reset_index()
        fig = px.bar(hourly_sales, x='Weekday or Weekend', y='Total Price ($)', title=f"Sales Mean by Weekday/Weekend for {selected_vendor}")

    fig.update_layout(title_text=f"Mean of {selected_metric} for {selected_vendor}")
    return fig

# Callback for each sep category purchase time section
@callback(
    Output('sep-category-purchase-time-chart', 'figure'),
    [Input('sep-category-hour-selector', 'value'),
     Input('sep-category-purchase-time-radio-buttons', 'value')]
)
def update_histogram(selected_category, selected_metric):
    # Filter the DataFrame based on the selected hour
    filtered_df = categories_time_df[categories_time_df['Category'] == selected_category]

    # Create a histogram based on the selected metric
    if selected_metric == 'Number of Items':
        hourly_item_num = filtered_df.groupby('Hour')['Number of Items'].sum().reset_index()
        fig = px.bar(hourly_item_num, x='Hour', y='Number of Items', title=f"Sum of Number of Items by Hour for {selected_category}")
    else:  # selected_metric == 'Total Price ($)'
        hourly_sales = filtered_df.groupby('Hour')['Total Price ($)'].sum().reset_index()
        fig = px.bar(hourly_sales, x='Hour', y='Total Price ($)', title=f"Total Sales by Hour for {selected_category}")

    fig.update_layout(title_text=f"Histogram of {selected_metric} for {selected_category}")
    return fig

# Callback for each sep category purchase weekday section
@callback(
    Output('sep-category-purchase-weekday-chart', 'figure'),
    [Input('sep-category-weekday-selector', 'value'),
     Input('sep-category-purchase-weekday-radio-buttons', 'value')]
)
def update_histogram(selected_category, selected_metric):
    # Filter the DataFrame based on the selected hour
    filtered_df = categories_weekday_df[categories_weekday_df['Category'] == selected_category]

    # Create a histogram based on the selected metric
    if selected_metric == 'Number of Items':
        hourly_item_num = filtered_df.groupby('Weekday or Weekend')['Number of Items'].mean().reset_index()
        fig = px.bar(hourly_item_num, x='Weekday or Weekend', y='Number of Items', title=f"Mean of Number of Items by Weekday/Weekend for {selected_category}")
    else:  # selected_metric == 'Total Price ($)'
        hourly_sales = filtered_df.groupby('Weekday or Weekend')['Total Price ($)'].mean().reset_index()
        fig = px.bar(hourly_sales, x='Weekday or Weekend', y='Total Price ($)', title=f"Sales Mean by Weekday/Weekend for {selected_category}")

    fig.update_layout(title_text=f"Mean of {selected_metric} for {selected_category}")
    return fig


# Callback for the items classification section
@callback(
    Output('items-classification-chart', 'figure'),
    [Input('items-classification-chart-radio-buttons', 'value'),
     Input('items-classification-radio-buttons', 'value')]
)
def update_graph(chart_type, col_chosen):
    ctx_item_classification = dash.callback_context

    if not ctx_item_classification.triggered:
        # Default action if no input has triggered the callback yet
        fig = px.histogram(items_df, x='Item Name', y=col_chosen, histfunc='avg')
    else:
        # Get the ID of the input that triggered the callback
        input_id = ctx_item_classification.triggered[0]['prop_id'].split('.')[0]

        if input_id == 'items-classification-chart-radio-buttons':
            if chart_type == 'hist':
                fig = px.histogram(items_df, x='Item Name', y=col_chosen, histfunc='avg')
            else:
                fig = px.pie(items_df, names='Item Name', values=col_chosen)
        elif input_id == 'items-classification-radio-buttons':
            if chart_type == 'hist':
                fig = px.histogram(items_df, x='Item Name', y=col_chosen, histfunc='avg')
            else:
                fig = px.pie(items_df, names='Item Name', values=col_chosen)
    
    return fig

# Callback for the items categories classification section
@callback(
    Output('items-categories-classification-chart', 'figure'),
    [Input('items-categories-classification-chart-radio-buttons', 'value'),
     Input('items-categories-classification-radio-buttons', 'value')]
)
def update_graph(chart_type, col_chosen):
    ctx_item_categories_classification = dash.callback_context

    if not ctx_item_categories_classification.triggered:
        # Default action if no input has triggered the callback yet
        fig = px.histogram(items_classification_df, x='Item Category', y=col_chosen, histfunc='avg')
    else:
        # Get the ID of the input that triggered the callback
        input_id = ctx_item_categories_classification.triggered[0]['prop_id'].split('.')[0]

        if input_id == 'items-categories-classification-chart-radio-buttons':
            if chart_type == 'hist':
                fig = px.histogram(items_classification_df, x='Item Category', y=col_chosen, histfunc='avg')
            else:
                fig = px.pie(items_classification_df, names='Item Category', values=col_chosen)
        elif input_id == 'items-categories-classification-radio-buttons':
            if chart_type == 'hist':
                fig = px.histogram(items_classification_df, x='Item Category', y=col_chosen, histfunc='avg')
            else:
                fig = px.pie(items_classification_df, names='Item Category', values=col_chosen)
    
    return fig




# Callback for modal of receipts information
@callback(
    Output('modal', 'is_open'),
    [Input('receipt_info_table', 'active_cell'), Input('close-modal', 'n_clicks')],
    [State('modal', 'is_open')]
)
def toggle_modal(active_cell, n_clicks, is_open):
    if active_cell or n_clicks:
        return not is_open
    return is_open

@callback(
    Output('modal-body', 'children'),
    [Input('receipt_info_table', 'active_cell')],
    [State('receipt_info_table', 'data')]
)
def update_modal_body(active_cell, data):
    if active_cell:
        row = active_cell['row']
        col = active_cell['column_id']
        cell_data = data[row][col]
        return html.Pre(cell_data)  # Using Pre for formatted text like JSON
    return "Click a cell"

# Run the app
if __name__ == '__main__':
    app.run(debug=True)