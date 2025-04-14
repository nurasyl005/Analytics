import dash
from dash import dcc, html, Input, Output
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# Connect to your PostgreSQL database
engine = create_engine("postgresql://alimbeknurasyl@localhost/screen_time_db")

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "📊 Screen Time Dashboard"

# App layout
app.layout = html.Div([
    html.H1("📱 Children's Screen Time Dashboard"),

    html.Div([
        html.Label("Select Day Type:"),
        dcc.Dropdown(
            id='day-type',
            options=[{'label': i, 'value': i} for i in ['Weekday', 'Weekend']],
            value='Weekday'
        ),
    ], style={'width': '25%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Select Gender:"),
        dcc.Dropdown(
            id='gender',
            options=[{'label': i, 'value': i} for i in ['Male', 'Female']],
            value='Male'
        ),
    ], style={'width': '25%', 'display': 'inline-block', 'marginLeft': '20px'}),

    html.Div([
        html.Label("Select Age Group:"),
        dcc.Dropdown(
            id='age',
            options=[{'label': str(i), 'value': str(i)} for i in range(1, 19)],
            value=str(10)
        ),
    ], style={'width': '25%', 'display': 'inline-block', 'marginLeft': '20px'}),
    
    dcc.Graph(id='screen-time-graph')
])

# Callback to update the chart
@app.callback(
    Output('screen-time-graph', 'figure'),
    Input('day-type', 'value'),
    Input('gender', 'value'),
    Input('age', 'value')
)
def update_chart(day_type, gender, age):
    query = f"""
        SELECT age, screen_time_type, AVG(avg_screen_time) AS avg_time
        FROM screen_time
        WHERE day_type = '{day_type}' AND gender = '{gender}' AND age = '{age}'
        GROUP BY age, screen_time_type
    """
    df = pd.read_sql(query, engine)
    fig = px.bar(
        df,
        x='age',
        y='avg_time',
        color='screen_time_type',
        barmode='group',
        title=f'Avg Screen Time (Age: {age}, Gender: {gender}, {day_type}s)',
        labels={'avg_time': 'Avg Hours'}
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)