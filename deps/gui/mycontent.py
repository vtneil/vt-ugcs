import pandas

from .__includes import *

INTERVAL_SLOW = 500
INTERVAL_FAST = 200


class Chart:
    @staticmethod
    def make_chart_title(y: str, x: str, z: str = None):
        if z is None:
            return 'Y: [{}] - X: {}'.format(y, x)
        return '({},{},{})'.format(x, y, z)

    @staticmethod
    def make_line_chart_2d(data: pandas.DataFrame, x_key: str, y_keys: list[str]):
        fig = px.line(
            data, x=x_key, y=y_keys, title=Chart.make_chart_title(','.join(y_keys), x_key),
        )
        fig.update_layout(margin=dict(l=20, r=20, t=100, b=20))
        return dcc.Graph(
            figure=fig,
        )

    @staticmethod
    def make_line_chart_3d(data: pandas.DataFrame, x_key: str, y_key: str, z_key: str):
        camera = dict(
            eye=dict(x=1.5, y=2, z=0.1)
        )
        fig = px.line_3d(
            data, x=x_key, y=y_key, z=z_key, title='3D: ' + Chart.make_chart_title(y_key, x_key, z_key)
        )
        fig.update_layout(margin=dict(l=20, r=20, t=100, b=20), scene_camera=camera)
        return dcc.Graph(
            figure=fig,
        )

    @staticmethod
    def make_bar_polar_chart(data: pandas.DataFrame, r: str, theta: str):
        fig = px.bar_polar(
            data, r, theta, title='Polar Chart',
            color_discrete_sequence=px.colors.sequential.Plasma_r
        )
        fig.update_layout(margin=dict(l=20, r=20, t=100, b=20))
        return dcc.Graph(
            figure=fig,
        )


class Component:
    dropdown_port = dcc.Dropdown(
        [], id='dropdown-port', disabled=True, clearable=False,
        persistence='true', persistence_type='session',
        placeholder='Choose serial port from below'
    )

    dropdown_baud = dcc.Dropdown(
        [], id='dropdown-baud', disabled=True, clearable=False,
        persistence='true', persistence_type='session',
        placeholder='Choose baud rate from below'
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

    dropdown_plot_x = dcc.Dropdown(
        [], id='dropdown-plot-x'
    )

    dropdown_plot_y = dcc.Dropdown(
        [], id='dropdown-plot-y', multi=True
    )

    dropdown_plot_z = dcc.Dropdown(
        [], id='dropdown-plot-z'
    )

    btn_add_chart = dbc.Button('Add Chart', id='btn-add-chart',
                               className='mx-1 btn-primary')

    btn_pop_chart = dbc.Button('Pop Last Data', id='btn-pop-chart',
                               className='mx-1 btn-danger')

    sidebar_ctrl = html.Div([
        dbc.Label('X Axis', html_for='dropdown-plot-x'),
        dropdown_plot_x,
        html.Br(),
        dbc.Label('Y Axis', html_for='dropdown-plot-y'),
        dropdown_plot_y,
        html.Br(),
        dbc.Label('Z Axis (Optional), choose 1 Y only.', html_for='dropdown-plot-z'),
        dropdown_plot_z,
        html.Br(),
        btn_add_chart,
        btn_pop_chart
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

    plot_col1 = dbc.Col([])
    plot_col2 = dbc.Col([])
    plot_col3 = dbc.Col([])
    plot_area = dbc.Row([plot_col1, plot_col2, plot_col3])

    @staticmethod
    def make_new_chart(data: pandas.DataFrame, x_key: str, y_keys: list[str] | str, z_key: str):
        if z_key is not None and isinstance(y_keys, str):
            return Chart.make_line_chart_3d(data, x_key, y_keys, z_key)
        elif z_key is not None and isinstance(y_keys, list):
            return Chart.make_line_chart_3d(data, x_key, y_keys[0], z_key)
        else:
            return Chart.make_line_chart_2d(data, x_key, y_keys)

    @staticmethod
    def make_plot_area(data: pandas.DataFrame, x_key: str, y_keys: list[str] | str, z_key: str = None):
        __graph = Component.make_new_chart(data, x_key, y_keys, z_key)
        return html.Div([
            __graph
        ])


class Content:
    content = html.Div([], id='page-content')

    plot = html.Div([dbc.Container([
        h2('Live Plot'),
        dbc.Row([]),
        html.Hr(),
        dbc.Row([
            dbc.Col(Component.sidebar, width=3),
            dbc.Col(Component.plot_area, width=9),
        ], ),
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
    def make_plot_layout_2d(*components: list, cols: int = 3):
        flats = [e for sub in components for e in sub]
        layout = []
        n_full, remainder = divmod(len(flats), cols)
        for i in range(cols):
            layout.append(flats[i * n_full: (i + 1) * n_full])
        for i in range(remainder):
            layout[i].append(flats[cols * n_full + i])

        return layout

    @staticmethod
    def page_404(url):
        return dbc.Container([
            html.H1('404: Not found!', className='text-danger'),
            html.Hr(),
            html.P('The pathname {} was not recognised...'.format(url), className='lead'),
        ], fluid=True, className="py-3")
