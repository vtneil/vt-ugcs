import pandas

from .__includes import *

INTERVAL_SLOW = 500
INTERVAL_FAST = 100


class Chart:
    @staticmethod
    def line_chart(data: pandas.DataFrame, x_key: str, y_key: str):
        fig = px.line(
            data, x=x_key, y=y_key, title='{} - {}'.format(y_key, x_key)
        )
        return dcc.Graph(
            figure=fig
        )


class Component:
    dropdown_port = dcc.Dropdown(
        [], id='dropdown-port', disabled=True,
        persistence='true', persistence_type='session'
    )

    dropdown_baud = dcc.Dropdown(
        [], id='dropdown-baud', disabled=True,
        persistence='true', persistence_type='session'
    )

    btn_connect = dbc.Button('Connect', id='btn-connect',
                             className='mx-1 btn-primary disabled')

    btn_disconnect = dbc.Button('Disconnect', id='btn-disconnect',
                                className='mx-1 btn-danger disabled')

    # Interval

    interval_slow = dcc.Interval(
        id='interval-slow',
        interval=INTERVAL_SLOW,
        n_intervals=0
    )

    interval_fast = dcc.Interval(
        id='interval-fast',
        interval=INTERVAL_FAST,
        n_intervals=0
    )

    interval_once = dcc.Interval(
        id='interval-once',
        interval=INTERVAL_FAST,
        n_intervals=0,
        max_intervals=1
    )

    # Global Components

    serial_options = html.Div([
        dbc.Label('Serial Device Port', html_for='dropdown-port'),
        dropdown_port,

        html.Br(),

        dbc.Label('Baud Rate', html_for='dropdown-baud'),
        dropdown_baud,

        html.Br(),

        html.Div([
            btn_connect,
            btn_disconnect
        ]),
    ])

    sidebar_dataframe = html.Div([])

    btn_add_chart = dbc.Button('Add Chart', id='btn-add-chart',
                               className='mx-1 btn-primary')

    sidebar_ctrl = html.Div([
        btn_add_chart
    ])

    sidebar = html.Div([
        html.H3('Data View'),
        sidebar_ctrl,
        html.Hr(),

        html.H3('Tabular View'),
        sidebar_dataframe,
        html.Hr(),

        html.H3('Serial Connection'),
        serial_options,
        html.Hr(),
    ])

    # Plot Section

    plot_area = html.Div([])

    @staticmethod
    def frame_chart(data: pandas.DataFrame, x_key: str, y_key: str):
        return html.Div([
            Chart.line_chart(data, x_key, y_key)
        ])

    @staticmethod
    def frame_plot(data):
        return html.Div([
            Component.frame_chart(data, 'a', 'b'),
        ])


class Content:
    content = html.Div([], id='page-content')

    plot = html.Div([dbc.Container([
        h2('Live Plot'),
        html.Hr(),
        dbc.Row([
            dbc.Col(Component.sidebar, width=3),
            dbc.Col(Component.plot_area),
        ])
    ], fluid=True)])

    settings = html.Div([dbc.Container([
        h2('Settings'),
        html.Hr(),

        html.P('Settings page for serial port management and customization.', className='lead'),

        h3('Connection'),

        Component.serial_options,

        h3('File'),

        dbc.Label('File Saving Options', html_for='checklist-file'),
        dbc.Checklist(
            [
                {'label': 'Write data to file?', 'value': 1},
                {'label': 'Write Google Earth KML?', 'value': 2},
            ],
            [1, 2], id='checklist-file', switch=True,
            persistence='true', persistence_type='session'
        ),

        html.P('', id='test-box')
    ], fluid=True)])

    @staticmethod
    def page_404(url):
        return dbc.Container([
            html.H1('404: Not found!', className='text-danger'),
            html.Hr(),
            html.P('The pathname {} was not recognised...'.format(url), className='lead'),
        ], fluid=True, className="py-3")
