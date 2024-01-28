# Загрузим необходимые пакеты
from dash import Dash, dcc, html, Input, Output, State
import pandas as pd
import numpy as np
import plotly.express as px
import geopandas as gpd
# import dash_bootstrap_components as dbc
import json
import joblib
# from lightgbm import LGBMRegressor

# Загрузка моделей
model_invest = joblib.load('data/finalized_model_Invest.sav')
model_OwOc = joblib.load('data/finalized_model_OwOc.sav')

# Загрузка геоданных Административных округов и Муниципальных образований
data = gpd.read_file('data/mo.geojson')
data = data.set_index('NAME')

# Загрузка словаря, в котором каждому муницип округу (МО) поставлены в соотв-е находящиеся рядом ж/д станции
# для сужения вариантов выбора для пользователя
sprav_sub_area_id_railroad = json.load( open( 'data/spravka_mo_sub_area_ID_railroad_station_walk.json' ) )
sprav_sub_area_id_railroad['if_none'] = ['']

# Загрузка словаря, в котором каждому муницип округу (МО) поставлены в соотв-е находящиеся рядом станции метро
# для сужения вариантов выбора для пользователя
sprav_sub_area_id_metro = json.load( open( 'data/spravka_mo_sub_area_ID_metro.json' ) )
sprav_sub_area_id_metro['if_none'] = ['']

# Загрузка таблиц, в котором каждому муницип округу (МО) поставлены в соотв-е диапазон расстояний до колец Москвы
# для сужения вариантов выбора для пользователя
sprav_bulvar = pd.read_csv('data/bulvar_ring_km.csv')
sprav_bulvar = sprav_bulvar.set_index('NAME')
sprav_bulvar.loc['if_none'] = [-20, 20]

sprav_ttk = pd.read_csv('data/ttk_km.csv')
sprav_ttk = sprav_ttk.set_index('NAME')
sprav_ttk.loc['if_none'] = [-20, 20]

sprav_mkad = pd.read_csv('data/mkad_km.csv')
sprav_mkad = sprav_mkad.set_index('NAME')
sprav_mkad.loc['if_none'] = [-20, 20]

# Загрузка таблиц, в котором каждому муницип округу (МО) поставлены в соотв-е диапазон минут пешком до метро
# для сужения вариантов выбора для пользователя
sprav_metro_min_walk = pd.read_csv('data/metro_min_walk.csv')
sprav_metro_min_walk = sprav_metro_min_walk.set_index('NAME')
sprav_metro_min_walk.loc['if_none'] = [0, 30]

# Загрузка справочника муниципальных образований на русском и английском
# В приложении используются названия на русском, в модели на английском
sprav_mo = pd.read_csv('data/sprav_mo.csv')
sprav_mo = sprav_mo.set_index('NAME')
sprav_mo.loc['if_none'] = ['']

# Карта Административных округов и МО
fig = px.choropleth_mapbox(data,
                           geojson = data.geometry,
                           locations = data.index,
                           #width=650,
                           height=520,
                           #colorscale="Viridis",
                           color=data.NAME_AO,
                           center={"lat": 55.6, "lon": 37.45},
                           #mapbox_style="open-street-map",
                           mapbox_style="carto-positron",
                           zoom=7.5)
fig.update_layout(clickmode='event+select')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'width': '60%',
        #'overflowX': 'scroll'
    }
}


app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H2(children='Введите данные о квартире в Москве и узнайте ее ожидаемую стоимость',
            style = {'text-align': 'center'}
            ),


   # html.Div([
   #     dcc.Graph(id='map_sensors',figure=fig)
   # ],style={'width': '49%', 'display': 'inline-block', 'vertical-align': 'middle'}),
    html.Div([
        html.Div([

            html.Div([
                dcc.RadioItems(
                    id = 'invest_or_owoc',
                    options=[
                        'Новостройка',
                        'Вторичка'
                        #{'label': 'Новостройка', 'value': 'OwOc'},
                        #{'label': 'Вторичка', 'value': 'Invest'},
                    ],
                    value='Вторичка',
                    inline = True,
                ),

                dcc.Dropdown(
                    id = "sale_year",
                    options = ['2011','2012','2013','2014','2015','2016'],
                    placeholder = "Год продажи",
                    style = {'padding': 0, 'margin-right': '10px', 'flex': 0.5, 'font-size': '14px'},  #NOT HERE
                ),

                dcc.Dropdown(
                    id = "sale_month",
                    options = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
                    placeholder = "Месяц продажи",
                    style = {'padding': 0, 'margin-right': '0px', 'flex': 0.5, 'font-size': '14px'},  #NOT HERE
                ),


            ], style={"display": "grid", "grid-template-columns": "50% 25% 25%"}),
            html.Br(),

            html.Div([

                html.Label('Выберите округ на карте:', style={
                    'font-style': 'italic',
                    'font-weight': 'bold',
                    'font-size': '13px'
                }),

                #html.Pre(id='name_ao', title='Выберете МО на карте', style=styles['pre']), #styles['pre']
                dcc.Input(
                    id = 'name_ao',
                    placeholder='Кликните по карте',
                    type='text',
                    value='',
                    readOnly = True,
                    style = {
                        'margin-left': '20px',
                        'flex': 0.9,
                        'font-size': '14px',
                        'text-align': 'center'
                    },
                ),
            ], style={'display': 'flex', 'flex-direction': 'row'}),
            html.Br(),


            html.Label('Выберите ближайшее метро и время пешком, ближайшую ЖД станцию:', style={
                'font-style': 'italic',
                'font-weight': 'bold',
                'font-size': '13px'
            }),

            html.Div([
                dcc.Dropdown(
                    id = "metro",
                    placeholder = "Метро",
                    style = {'padding': 0, 'margin-right': '0px', 'flex': 0.5, 'font-size': '14px'},
                ),

                dcc.Dropdown(
                    id = "metro_min",
                    #options = pd.DataFrame(np.arange(0,800,0.5))[0],
                    placeholder = "Минут пешком",
                    style = {'padding': 0, 'margin-right': '20px', 'flex': 0.5, 'font-size': '14px'},  #NOT HERE
                ),


                dcc.Dropdown(
                    id = "railway_station",
                    placeholder = "ЖД станция",
                    style = {'padding': 0, 'margin-left': '0px', 'flex': 0.5, 'font-size': '14px'},
                ),
            ], style={"display": "grid", "grid-template-columns": "30% 30% 40%"}),
            html.Br(),


            html.Label('Введите площади квартиры, кв.м.', style={
                'font-style': 'italic',
                'font-weight': 'bold',
                'font-size': '13px'
            }),
            html.Br(),

            html.Div([
                dcc.Input(
                    id = 'full_sq',
                    placeholder='Общая',
                    type='number',
                    value='',
                    style = {
                        'padding': 0,
                        'margin-right': '20px',
                        'flex': 0.6,
                        'font-size': '12px',
                        'width': '40%',
                        'text-align': 'center'
                    },
                ),

                dcc.Input(
                    id = 'life_sq',
                    placeholder='Жилая',
                    type='number',
                    value='',
                    style = {
                        'padding': 0,
                         'margin-right': '20px',
                         'flex': 0.6,
                         'font-size': '12px',
                         'width': '40%',
                         'text-align': 'center'
                    },
                ),

                dcc.Input(
                    id = 'kitch_sq',
                    placeholder='Кухня',
                    type='number',
                    value='',
                    style = {
                        #'margin-right': '20px',
                        'flex': 0.6,
                        'font-size': '12px',
                        'width': '40%',
                        'text-align': 'center'
                    },
                ),
            ], style={'display': 'flex', 'flex-direction': 'row'}),



            html.Br(),
            html.Label('Введите этаж квартиры, макс.этажность и год постройки дома',style={
                'font-style': 'italic',
                'font-weight': 'bold',
                'font-size': '13px'
            }),
            html.Br(),

            html.Div(
                [

                    dcc.Dropdown(
                        id = "floor_dropdown",
                        options = pd.DataFrame(range(1,100,1))[0],
                        placeholder = "Введите этаж",
                        style = {'padding': 0, 'margin-right': '20px', 'flex': 0.5, 'font-size': '14px'},  #NOT HERE
                    ),
                    html.Div(id="dd_output_floor"),


                    dcc.Dropdown(
                        id="max_floor_dropdown",
                        options = pd.DataFrame(range(1,100,1))[0],
                        placeholder = "Этажность дома",
                        style={'padding': 0, 'margin-right': '20px',  'flex': 0.5, 'font-size': '14px'},  #NOT HERE
                    ),
                    html.Div(id="dd_output_max_floor"),

                    dcc.Dropdown(
                        id = "build_year",
                        options = pd.DataFrame(range(2020,1800,-1))[0],
                        placeholder = "Год постройки",
                        style = {'padding': 0, 'flex': 0.5, 'font-size': '14px'},  #NOT HERE
                    ),
                    html.Div(id="dd_output_build_year"),

                ],
                style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'space-between'},
            ),
            html.Br(),

            html.Label('Введите расстояние в КМ от дома до Бульварного кольца, ТТК, МКАД', style={
                'font-style': 'italic',
                'font-weight': 'bold',
                'font-size': '13px'
            }),
            html.Label('Если дом внутри кольца, используется знак ''+'', иначе ''-''', style={
                'font-style': 'italic',
                'font-weight': 'bold',
                'font-size': '13px'
            }),
            html.Br(),

            dcc.Slider(0, 70, 0.1, value=2.4, marks=None,
                        id='slider_bulvar_ring',
                        tooltip={"placement": "bottom", "always_visible": True}),

            dcc.Slider(-70, 70, 0.1, value=0, marks=None,
                       id='slider_ttk',
                       tooltip={"placement": "bottom", "always_visible": True}),

            dcc.Slider(0, 70, 0.1, value=7.1, marks=None,
                       id='slider_mkad',
                       tooltip={"placement": "bottom", "always_visible": True}),
        ], style={'width': '43%', 'display': 'inline-block'}), #


        html.Div([
            html.Div([
                dcc.Graph(id='map_sensors',figure=fig),
            ]),
            html.Div([
                html.Button('Узнать цену', id='submit_val', n_clicks=0, style = {'background-color': 'blue',
                                                                                 'color': 'white',}),
            ],style={'display': 'flex', 'flex-direction': 'row-reverse', 'justify-content': 'center'}),
            html.Br(),
            html.Div([
                html.Div(id='container_button',
                         children='Здесь появится стоимость квартиры')
            ],style={'display': 'flex', 'flex-direction': 'row-reverse', 'justify-content': 'center'}),
        ], style={'width': '55%', 'display': 'inline-block'}),

    ], style={'display': 'flex'}),

    html.Hr(),
    html.Div(id="number-out"),
    #dcc.Markdown(id="number-out"),
    html.Hr(),

] ) #style = {'background-color': 'darkcyan'}


@app.callback(
    Output('container_button', 'children'),
    Input('submit_val', 'n_clicks'),
    State('name_ao', "value"),
    State('metro', "value"),
    State('metro_min', "value"),
    State('railway_station', "value"),
    State('invest_or_owoc', "value"),
    State("full_sq", "value"),
    State("life_sq", "value"),
    State("kitch_sq", "value"),
    State('floor_dropdown', "value"),
    State('max_floor_dropdown', "value"),
    State('build_year', "value"),
    State('slider_bulvar_ring', "value"),
    State('slider_ttk', "value"),
    State('slider_mkad', "value"),
    State('sale_year', "value"),
    State('sale_month', "value"),

)
def update_output(
                  n_clicks,
                  name_ao,
                  metro,
                  metro_min,
                  railway_station,
                  invest_or_owoc,
                  full_sq,
                  life_sq,
                  kitch_sq,
                  floor_dropdown,
                  max_floor_dropdown,
                  build_year,
                  slider_bulvar_ring,
                  slider_ttk,
                  slider_mkad,
                  sale_year,
                  sale_month
    ):

    if invest_or_owoc == 'Новостройка':
        model = model_OwOc
    else:
        model = model_invest

    result = 'Здесь появится стоимость квартиры'

    if n_clicks >= 1 and name_ao is not None:
        try:
            X = pd.DataFrame({
                'full_sq': [full_sq],
                'floor': [floor_dropdown],
                'month': [sale_month],
                'sub_area': [sprav_mo.loc[name_ao][0]],
                'max_floor': [max_floor_dropdown],
                'life_sq': [life_sq],
                'ID_metro': [metro],
                'build_year': [build_year],
                'year': [sale_year],
                'ID_railroad_station_walk': [railway_station],
                'kitch_sq': [kitch_sq],
                'metro_min_walk': [metro_min],
                'bulvar_ring_km': [slider_bulvar_ring],
                'mkad_km': [slider_mkad],
                'ttk_km': [slider_ttk],
            })

            categ_col = ['month', 'sub_area', 'ID_metro', 'year', 'ID_railroad_station_walk']
            for c in categ_col:
                X[c] = X[c].astype('category')

            price_sq_m = model.predict(X)
            result = 'Цена квартиры {} тыс.руб. при цене 1 кв.м. {} тыс.руб.'.format(
                                                                                    (price_sq_m*full_sq).round(0)[0],
                                                                                    price_sq_m.round(1)[0]
                                                                                )

        except ValueError:  #TypeError or ValueError or KeyError
            result = 'Пожалуйста, введите данные во все поля'

    return result



@app.callback(
    Output("number-out", "children"),
    Input('name_ao', "value"),
    Input('metro', "value"),
    Input('metro_min', "value"),
    Input('railway_station', "value"),
    Input('invest_or_owoc', "value"),
    Input("full_sq", "value"),
    Input("life_sq", "value"),
    Input("kitch_sq", "value"),
    Input('floor_dropdown', "value"),
    Input('max_floor_dropdown', "value"),
    Input('build_year', "value"),
    Input('slider_bulvar_ring', "value"),
    Input('slider_ttk', "value"),
    Input('slider_mkad', "value"),

    )
def number_render(
        name_ao,
        metro,
        metro_min,
        railway_station,
        invest_or_owoc,
        full_sq,
        life_sq,
        kitch_sq,
        floor_dropdown,
        max_floor_dropdown,
        build_year,
        slider_bulvar_ring,
        slider_ttk,
        slider_mkad

        ):
    in_or_out_bulvar = 'внутри' if slider_bulvar_ring > 0 else 'снаружи'
    in_or_out_ttk = 'внутри' if slider_ttk > 0 else 'снаружи'
    in_or_out_mkad = 'внутри' if slider_mkad > 0 else 'снаружи'
    return "Район {}, до метро {} пешком {} мин, ближайш. ж.д. стация {}. " \
           "Квартира - {}, Общ.площадь: {} кв.м., Жил.площадь: {} кв.м., Кухня: {} кв.м., Этаж: {} из {} " \
           "в доме {} года постройки, {} Бульварного ({} км), {} ТТК ({} км), {} МКАД ({} км)".\
        format(
               name_ao,
               metro,
               metro_min,
               railway_station,
               invest_or_owoc,
               full_sq,
               life_sq,
               kitch_sq,
               floor_dropdown,
               max_floor_dropdown,
               build_year,
               in_or_out_bulvar,
               slider_bulvar_ring,
               in_or_out_ttk,
               slider_ttk,
               in_or_out_mkad,
               slider_mkad
        )




@app.callback(
    Output('name_ao', 'value'),      #children
    Input('map_sensors', 'clickData'))
def display_click_data(clickData):
    n = None
    if clickData is not None:
        n = clickData.get("points")[0].get("location")
    return n #f'Вы выбрали: {n}'

# Отвечает за выпадающий список ЖД станций в зависимости от выбранного значения округа
@app.callback(
    Output('railway_station', 'options'),
    Input('name_ao', 'value'))   #children
def set_railway_stations_options(selected_name_ao):
    #print([{'label': i, 'value': i} for i in sprav_sub_area_id_railroad[selected_name_ao]])
    if selected_name_ao is not None:
        selected_name_ao
    else:
        selected_name_ao = 'if_none'
    return sprav_sub_area_id_railroad[selected_name_ao]

@app.callback(
    Output('metro', 'options'),
    Input('name_ao', 'value'))   #children
def set_metro_options(selected_name_ao):
    #print([{'label': i, 'value': i} for i in sprav_sub_area_id_railroad[selected_name_ao]])
    if selected_name_ao is not None:
        selected_name_ao
    else:
        selected_name_ao = 'if_none'
    return sprav_sub_area_id_metro[selected_name_ao]

@app.callback(
    Output('slider_bulvar_ring', 'min'),
    Output('slider_bulvar_ring', 'max'),
    Output('slider_bulvar_ring', 'value'),
    Input('name_ao', 'value'))   #children
def set_min_max_bulvar_options(selected_name_ao):
    #print([{'label': i, 'value': i} for i in sprav_sub_area_id_railroad[selected_name_ao]])
    if selected_name_ao is not None:
        selected_name_ao
    else:
        selected_name_ao = 'if_none'
    return sprav_bulvar.loc[selected_name_ao]['min'], \
           sprav_bulvar.loc[selected_name_ao]['max'], \
           (sprav_bulvar.loc[selected_name_ao]['min'] + sprav_bulvar.loc[selected_name_ao]['max'])/2

@app.callback(
    Output('slider_ttk', 'min'),
    Output('slider_ttk', 'max'),
    Output('slider_ttk', 'value'),
    Input('name_ao', 'value'))   #children
def sset_min_max_ttk_options(selected_name_ao):
    if selected_name_ao is not None:
        selected_name_ao
    else:
        selected_name_ao = 'if_none'
    return sprav_ttk.loc[selected_name_ao]['min'], \
           sprav_ttk.loc[selected_name_ao]['max'], \
           (sprav_ttk.loc[selected_name_ao]['min'] + sprav_ttk.loc[selected_name_ao]['max'])/2

@app.callback(
    Output('slider_mkad', 'min'),
    Output('slider_mkad', 'max'),
    Output('slider_mkad', 'value'),
    Input('name_ao', 'value'))   #children
def sset_min_max_mkad_options(selected_name_ao):
    if selected_name_ao is not None:
        selected_name_ao
    else:
        selected_name_ao = 'if_none'
    return sprav_mkad.loc[selected_name_ao]['min'], \
           sprav_mkad.loc[selected_name_ao]['max'], \
           (sprav_mkad.loc[selected_name_ao]['min'] + sprav_mkad.loc[selected_name_ao]['max'])/2

@app.callback(
    Output('metro_min', 'options'),
    Input('name_ao', 'value'))   #children
def sset_metro_min_walk_options(selected_name_ao):
    if selected_name_ao is not None:
        selected_name_ao
    else:
        selected_name_ao = 'if_none'
    return pd.DataFrame(np.arange(sprav_metro_min_walk.loc[selected_name_ao]['min'] ,
                                  sprav_metro_min_walk.loc[selected_name_ao]['max'] ,
                                  0.5))[0]


# Отвечает за значение "по умолчанию" в выпадающем списке ЖД станций
# @app.callback(
#     Output('railway_station', 'value'),
#     Input('railway_station', 'options'))
# def set_railway_stations_value(options):
#     #print(options[0])
#     return options[0]
# @app.callback(
#     Output('metro', 'value'),
#     Input('metro', 'options'))
# def set_metro_value(options):
#     #print(options[0])
#     return options[0]



if __name__ == '__main__':
    app.run_server(debug=True)