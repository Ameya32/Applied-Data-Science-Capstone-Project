# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the space launch data into pandas dataframe
launch_data = pd.read_csv("spacex_launch_dash.csv")
max_payload_mass = launch_data['Payload Mass (kg)'].max()
min_payload_mass = launch_data['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                
                                dcc.Dropdown(id='launch-site-dropdown',
                                options=[
                                    {'label': 'All Sites', 'value': 'All Sites'},
                                    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                                ],
                                placeholder='Select a Launch Site',
                                value='All Sites',
                                searchable=True
                                ),
                                html.Br(),

                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                
                                dcc.RangeSlider(id='payload-range-slider',
                                min=0,
                                max=10000,
                                step=1000,
                                marks={i: '{}'.format(i) for i in range(0, 10001, 1000)},
                                value=[min_payload_mass, max_payload_mass]),

                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# Callback for pie chart
def get_pie_chart(selected_site):
    if selected_site == 'All Sites':
        fig = px.pie(values=launch_data.groupby('Launch Site')['class'].mean(), 
                     names=launch_data.groupby('Launch Site')['Launch Site'].first(),
                     title='Total Success Launches by Site')
    else:
        fig = px.pie(values=launch_data[launch_data['Launch Site']==str(selected_site)]['class'].value_counts(normalize=True), 
                     names=launch_data['class'].unique(), 
                     title='Total Success Launches for Site {}'.format(selected_site))
    return fig

@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='launch-site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    return get_pie_chart(selected_site)

# Callback for scatter plot
def get_payload_chart(selected_site, payload_range):
    if selected_site == 'All Sites':
        fig = px.scatter(launch_data[launch_data['Payload Mass (kg)'].between(payload_range[0], payload_range[1])], 
                x="Payload Mass (kg)",
                y="class",
                color="Booster Version Category",
                hover_data=['Launch Site'],
                title='Correlation Between Payload and Success for All Sites')
    else:
        site_data = launch_data[launch_data['Launch Site']==str(selected_site)]
        fig = px.scatter(site_data[site_data['Payload Mass (kg)'].between(payload_range[0], payload_range[1])], 
                x="Payload Mass (kg)",
                y="class",
                color="Booster Version Category",
                hover_data=['Launch Site'],
                title='Correlation Between Payload and Success for Site {}'.format(selected_site))
    return fig

@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='launch-site-dropdown', component_property='value'),
     Input(component_id='payload-range-slider',component_property='value')]
)
def update_payload_chart(selected_site, payload_range):
    return get_payload_chart(selected_site, payload_range)

# Run the app
if __name__ == '__main__':
    app.run_server()