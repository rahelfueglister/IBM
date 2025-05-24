# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1.1: Define dropdown component
                                # TASK 1.2: Define options with 'All Sites' and individual sites
                                # TASK 1.3: Set default value, placeholder, and make searchable
                                    dcc.Dropdown(
                                        id='site-dropdown',
                                        options=[{'label': 'All Sites', 'value': 'ALL'}] +
                                                [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
                                        value='ALL',
                                        placeholder='Select a Launch Site',
                                        searchable=True
                                    ),

                                    html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    marks={i: f'{i}' for i in range(0, 10001, 2500)},
                                    value=[min_payload, max_payload]
                                ),

                                html.Br(),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])


# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# TASK 2.1: Callback zur Aktualisierung des Tortendiagramms basierend auf Startplatz
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    # TASK 2.2: Wenn 'ALL' ausgewählt ist, zeige erfolgreiche Starts pro Startplatz
    if selected_site == 'ALL':
        success_counts = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size().reset_index(name='counts')
        fig = px.pie(success_counts,
                     values='counts',
                     names='Launch Site',
                     title='Erfolgreiche Starts nach Startplatz (Alle)')
    else:
        # TASK 2.3: Wenn ein spezifischer Startplatz ausgewählt ist, zeige Erfolg vs. Fehlschlag
        site_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        outcome_counts = site_df['class'].value_counts().reset_index()
        outcome_counts.columns = ['class', 'count']
        outcome_counts['class'] = outcome_counts['class'].map({1: 'Erfolg', 0: 'Fehlschlag'})
        fig = px.pie(outcome_counts,
                     values='count',
                     names='class',
                     title=f'Start-Ergebnisse für {selected_site}')
    return fig

# TASK 3: Add a slider to select payload range

dcc.RangeSlider(
    id='payload-slider',
    min=0,
    max=10000,
    step=1000,
    marks={i: f'{i}' for i in range(0, 10001, 2500)},
    value=[min_payload, max_payload]
),

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
# TASK 4.1: Callback mit zwei Inputs (Dropdown + Slider) und Scatter-Plot als Output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter_plot(selected_site, payload_range):
    # TASK 4.2: Filter nach Payload-Bereich
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]

    # TASK 4.3: Für 'ALL' Sites – kein zusätzlicher Filter
    if selected_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Payload vs. Erfolg für alle Startplätze'
        )
    else:
        # TASK 4.4: Filter zusätzlich nach Startplatz
        site_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(
            site_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Payload vs. Erfolg für {selected_site}'
        )

    return fig


# Run the app
if __name__ == '__main__':
    app.run()
    
