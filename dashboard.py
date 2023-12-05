# Import packages
import dash
from dash import Dash, html, dash_table, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Incorporate data
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')

receipts_info_df = pd.read_csv('https://raw.githubusercontent.com/Soroush-Azizzadeh/ics438-final-project/main/datasets/test_receipt_information.csv')
vendors_classification_df = pd.read_csv('https://raw.githubusercontent.com/Soroush-Azizzadeh/ics438-final-project/main/datasets/synthetic_receipts_dataset_with_category.csv')
vendors_classification_df = vendors_classification_df[['Category', 'Number of Items', 'Total Price ($)', 'Discount ($)', 'Tax ($)']]
vendors_df = pd.read_csv('https://raw.githubusercontent.com/Soroush-Azizzadeh/ics438-final-project/main/datasets/synthetic_vendors_dataset.csv')
vendors_time_df = pd.read_csv('https://raw.githubusercontent.com/Soroush-Azizzadeh/ics438-final-project/main/datasets/synthetic_receipts_dataset_with_time.csv')

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
    
    
    ##############################
    # PURCHASE TIME
    ##############################
    html.Div(className='row', children='Purchase Time Analysis',
             style={'textAlign': 'center', 'color': 'blue', 'fontSize': 30, 'margin-bottom': 20}),
    
    html.Div(className='row', children=[
        html.Div(className='six columns', children='PLACEHOLDER FOR TABLE',
             style={'textAlign': 'center', 'color': 'blue', 'fontSize': 20}),
        
        html.Div(className='six columns', children='PLACEHOLDER FOR GRAPH',
             style={'textAlign': 'center', 'color': 'blue', 'fontSize': 20})
    ]),
    
    html.Hr(),
    
], fluid=True, style={'margin-right': '100px'})

#######################
# CALLBACKS
#######################
# @callback(
#     Output('vendors-chart', 'figure'),
#     [Input('vendors-info-chart-radio-buttons', 'value')],
#     allow_duplicate=True
# )
# def update_graph(chart_type):
#     if chart_type == 'hist':
#         # switch to histogram
#         fig = px.bar(df, x='Category', y='Values')
#     else:
#         # switch to pie chart
#         fig = px.pie(df, names='Category', values='Values')
#     return fig

# @callback(
#     Output(component_id='vendors-chart', component_property='figure'),
#     Input(component_id='vendors-radio-buttons', component_property='value'),
#     allow_duplicate=True
# )
# def update_graph(col_chosen):
#     fig = px.histogram(vendors_df, x='Vendor Name', y=col_chosen, histfunc='avg')
#     return fig

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
        elif input_id == 'vendors-classification-chart-radio-buttons':
            if chart_type == 'hist':
                fig = px.histogram(vendors_classification_df, x='Category', y=col_chosen, histfunc='avg')
            else:
                fig = px.pie(vendors_classification_df, names='Category', values=col_chosen)
    
    return fig


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