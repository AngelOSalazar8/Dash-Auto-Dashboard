import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

# Carga de datos
DATA_URL = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv'
data = pd.read_csv(DATA_URL)

# App Dash con tema Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.title = "Automobile Statistics Dashboard"

# Lista años para dropdown
year_list = [i for i in range(1980, 2024)]

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Automobile Sales Statistics Dashboard", className='text-center mb-4'), width=12)
    ]),
    dbc.Row([
        dbc.Col([
            html.Label("Select Statistics:", className='mb-1'),
            dcc.Dropdown(
                id='dropdown-statistics',
                options=[
                    {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
                    {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
                ],
                placeholder='Select a report type'
            )
        ], md=6),
        dbc.Col([
            html.Label("Select Year:", className='mb-1'),
            dcc.Dropdown(
                id='select-year',
                options=[{'label': str(y), 'value': y} for y in year_list],
                placeholder='Select Year',
                disabled=True
            )
        ], md=6),
    ], className='mb-4'),
    dbc.Row([
        dbc.Col(html.Div(id='output-container'), width=12)
    ])
], fluid=True)

# Callback para habilitar/deshabilitar el dropdown de año
@app.callback(
    Output('select-year', 'disabled'),
    Input('dropdown-statistics', 'value')
)
def toggle_year_dropdown(selected_stat):
    return selected_stat != 'Yearly Statistics'

# Callback principal para mostrar gráficos
@app.callback(
    Output('output-container', 'children'),
    [Input('dropdown-statistics', 'value'),
     Input('select-year', 'value')]
)
def update_graphs(statistics, year):
    if statistics == 'Recession Period Statistics':
        rec_data = data[data['Recession'] == 1]
        
        # Gráfico 1: Ventas promedio por año durante recesión
        yearly_rec = rec_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        graph1 = dcc.Graph(figure=px.line(yearly_rec, x='Year', y='Automobile_Sales',
                                          title='Average Automobile Sales During Recession Periods'))

        # Gráfico 2: Ventas promedio por tipo de vehículo durante recesión
        sales_by_type = rec_data.groupby(['Year', 'Vehicle_Type'])['Automobile_Sales'].mean().reset_index()
        graph2 = dcc.Graph(figure=px.bar(sales_by_type, x='Year', y='Automobile_Sales',
                                         color='Vehicle_Type',
                                         title='Average Sales by Vehicle Type During Recession Periods'))

        # Gráfico 3: Participación en publicidad por tipo de vehículo durante recesión
        # Aquí sumamos gasto por Vehicle_Type
        adv_exp = rec_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        graph3 = dcc.Graph(figure=px.pie(adv_exp, values='Advertising_Expenditure', names='Vehicle_Type',
                                         title='Advertising Expenditure Share by Vehicle Type During Recessions'))

        # Gráfico 4: Efecto tasa desempleo en ventas por tipo de vehículo
        unemp = rec_data.groupby('Vehicle_Type').agg({'Automobile_Sales':'mean', 'unemployment_rate':'mean'}).reset_index()
        graph4 = dcc.Graph(figure=px.scatter(unemp, x='unemployment_rate', y='Automobile_Sales', color='Vehicle_Type',
                                             size='Automobile_Sales',
                                             title='Unemployment Rate vs Automobile Sales by Vehicle Type'))

        return dbc.Row([
            dbc.Col(graph1, md=6),
            dbc.Col(graph2, md=6),
            dbc.Col(graph3, md=6),
            dbc.Col(graph4, md=6),
        ])

    elif statistics == 'Yearly Statistics' and year:
        yearly_data = data[data['Year'] == year]

        # Gráfico 1: Ventas promedio por año (todo el dataset)
        yearly_avg = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        graph1 = dcc.Graph(figure=px.line(yearly_avg, x='Year', y='Automobile_Sales',
                                          title='Average Yearly Automobile Sales (All Years)'))

        # Gráfico 2: Ventas promedio por mes (todo el dataset)
        monthly_avg = data.groupby('Month')['Automobile_Sales'].mean().reset_index()
        graph2 = dcc.Graph(figure=px.line(monthly_avg, x='Month', y='Automobile_Sales',
                                          title='Average Monthly Automobile Sales (All Years)'))

        # Gráfico 3: Ventas promedio por tipo de vehículo en año seleccionado
        sales_by_type = yearly_data.groupby(['Month', 'Vehicle_Type'])['Automobile_Sales'].mean().reset_index()
        graph3 = dcc.Graph(figure=px.bar(sales_by_type, x='Month', y='Automobile_Sales',
                                         color='Vehicle_Type',
                                         title=f'Average Sales by Vehicle Type in {year}'))

        # Gráfico 4: Gasto en publicidad por tipo de vehículo en año seleccionado
        adv_exp = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        graph4 = dcc.Graph(figure=px.pie(adv_exp, values='Advertising_Expenditure', names='Vehicle_Type',
                                         title=f'Advertising Expenditure Share by Vehicle Type in {year}'))

        return dbc.Row([
            dbc.Col(graph1, md=6),
            dbc.Col(graph2, md=6),
            dbc.Col(graph3, md=6),
            dbc.Col(graph4, md=6),
        ])

    else:
        return html.Div("Please select a report type and year (if applicable).", className='text-center')


if __name__ == '__main__':
    app.run(debug=True)

