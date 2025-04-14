import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# Connect to PostgreSQL database
engine = create_engine("postgresql://alimbeknurasyl@localhost/screen_time_db")

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "📊 Screen Time Dashboard"

# App layout
app.layout = html.Div([
    html.Div(id='summary-cards', style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}),

    html.Button("🔄 Reset Filters", id='reset-btn', n_clicks=0, style={'marginRight': '20px'}),
    dcc.Download(id="download-data"),
    html.Button("⬇️ Download CSV", id='download-btn', n_clicks=0),

    html.H1("📱 Children's Screen Time Dashboard"),

    html.Div([
        html.Label("Select Day Type:"),
        dcc.Dropdown(
            id='day-type',
            options=[{'label': i, 'value': i} for i in ['Weekday', 'Weekend']],
            value=None,
            placeholder="Select Day Type"
        ),
    ], style={'width': '25%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Select Gender:"),
        dcc.Dropdown(
            id='gender',
            options=[{'label': i, 'value': i} for i in ['Male', 'Female']],
            value=None,
            placeholder="Select Gender"
        ),
    ], style={'width': '25%', 'display': 'inline-block', 'marginLeft': '20px'}),

    html.Div([
        html.Label("Select Age Group:"),
        dcc.Dropdown(
            id='age',
            options=[{'label': str(i), 'value': str(i)} for i in range(5, 16)],
            value=None,
            placeholder="Select Age Group"
        ),
    ], style={'width': '25%', 'display': 'inline-block', 'marginLeft': '20px'}),
    
    dcc.Graph(id='screen-time-graph'),
    dcc.Store(id='reset-trigger', data=False)
])

# Callback to update the chart
@app.callback(
    Output('screen-time-graph', 'figure'),
    Output('summary-cards', 'children'),
    Output('day-type', 'value'),
    Output('gender', 'value'),
    Output('age', 'value'),
    Output('download-data', 'data'),
    Input('day-type', 'value'),
    Input('gender', 'value'),
    Input('age', 'value'),
    Input('reset-btn', 'n_clicks'),
    Input('download-btn', 'n_clicks'),
    prevent_initial_call=True
)
def update_chart(day_type, gender, age, reset_clicks, download_clicks):
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger == 'reset-btn':
        return dash.no_update, dash.no_update, None, None, None, None

    filters = []
    if day_type:
        filters.append(f"day_type = '{day_type}'")
    if gender:
        filters.append(f"gender = '{gender}'")
    if age:
        filters.append(f"age = '{age}'")
    where_clause = "WHERE " + " AND ".join(filters) if filters else ""

    query = f"""
        SELECT age, gender, screen_time_type, avg_screen_time
        FROM screen_time
        {where_clause}
    """
    df = pd.read_sql(query, engine)
    fig = px.bar(
        df.groupby(['age', 'screen_time_type'], as_index=False)['avg_screen_time'].mean(),
        x='age',
        y='avg_screen_time',
        color='screen_time_type',
        barmode='group',
        title='Avg Screen Time by Filters',
        labels={'avg_screen_time': 'Avg Hours'}
    )

    # Summary cards
    summary = [
        html.Div(f"📊 Records: {len(df)}", style={'padding': '10px', 'background': '#f2f2f2'}),
        html.Div(f"⏱️ Avg Time: {round(df['avg_screen_time'].mean(), 2) if not df.empty else 0} hrs", style={'padding': '10px', 'background': '#f2f2f2'}),
        html.Div(f"👥 Sample Size: {df.shape[0]}", style={'padding': '10px', 'background': '#f2f2f2'}),
    ]

    # Download
    if trigger == 'download-btn':
        return fig, summary, dash.no_update, dash.no_update, dash.no_update, dcc.send_data_frame(df.to_csv, "filtered_data.csv")

    return fig, summary, dash.no_update, dash.no_update, dash.no_update, None

# Run the app
if __name__ == '__main__':
    app.run(debug=True)