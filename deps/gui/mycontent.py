import pandas

from .__includes import *

INTERVAL_SLOW = 500
INTERVAL_FAST = 200


class Chart:
    PLOT_XYZ = 'xyz'
    PLOT_POLAR = 'polar'

    STYLE_LINE = 'line'
    STYLE_SCATTER = 'scatter'
    STYLE_BAR = 'bar'

    LINE_TYPES = ['line', 'scatter']
    POLAR_TYPES = ['bar', 'scatter']
    MARGIN = dict(l=20, r=20, t=100, b=20)

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
        fig.update_layout(margin=Chart.MARGIN)
        return Chart.__make_dcc(fig)

    @staticmethod
    def make_line_chart_3d(data: pandas.DataFrame, x_key: str, y_key: str, z_key: str):
        camera = dict(
            eye=dict(x=1.5, y=2, z=0.1)
        )
        fig = px.line_3d(
            data, x=x_key, y=y_key, z=z_key, title='3D: ' + Chart.make_chart_title(y_key, x_key, z_key)
        )
        fig.update_layout(margin=Chart.MARGIN, scene_camera=camera)
        return Chart.__make_dcc(fig)

    @staticmethod
    def make_scatter_chart_2d(data: pandas.DataFrame, x_key: str, y_keys: list[str]):
        fig = px.scatter(
            data, x=x_key, y=y_keys, title=Chart.make_chart_title(','.join(y_keys), x_key),
        )
        fig.update_layout(margin=Chart.MARGIN)
        return Chart.__make_dcc(fig)

    @staticmethod
    def make_scatter_chart_3d(data: pandas.DataFrame, x_key: str, y_key: str, z_key: str):
        camera = dict(
            eye=dict(x=1.5, y=2, z=0.1)
        )
        fig = px.scatter_3d(
            data, x=x_key, y=y_key, z=z_key, title='3D: {}'.format(Chart.make_chart_title(y_key, x_key, z_key))
        )
        fig.update_layout(margin=Chart.MARGIN, scene_camera=camera)
        return Chart.__make_dcc(fig)

    @staticmethod
    def make_bar_polar_chart(data: pandas.DataFrame, r: str | list[str], theta: str):
        fig = px.bar_polar(
            data, r, theta, title='Polar: r: {} - theta: {}'.format(r, theta),
        )
        fig.update_layout(margin=Chart.MARGIN)
        return Chart.__make_dcc(fig)

    @staticmethod
    def make_scatter_polar_chart(data: pandas.DataFrame, r: str | list[str], theta: str):
        fig = px.scatter_polar(
            data, r, theta, title='Polar: r: {} - theta: {}'.format(r, theta),
        )
        fig.update_layout(margin=Chart.MARGIN)
        return Chart.__make_dcc(fig)

    @staticmethod
    def __make_dcc(fig):
        return dcc.Graph(
            figure=fig,
            config={
                'displayModeBar': False
            }
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

    dropdown_plot_xyz_type = dcc.Dropdown(
        [], id='dropdown-plot-xyz-type'
    )

    dropdown_plot_r = dcc.Dropdown(
        [], id='dropdown-plot-r'
    )

    dropdown_plot_theta = dcc.Dropdown(
        [], id='dropdown-plot-theta'
    )

    dropdown_plot_rt_type = dcc.Dropdown(
        [], id='dropdown-plot-rt-type'
    )

    btn_add_chart_xyz = dbc.Button('Add Chart to View', id='btn-add-chart-xyz',
                                   className='mx-1 btn-primary')

    btn_add_chart_polar = dbc.Button('Add Chart to View', id='btn-add-chart-polar',
                                     className='mx-1 btn-primary')

    btn_pop_chart = dbc.Button('Pop Last Data', id='btn-pop-chart',
                               className='mx-1 btn-danger')

    sidebar_page1 = dbc.Card(dbc.CardBody([
        dbc.Label('X Axis', html_for='dropdown-plot-x'),
        dropdown_plot_x,
        html.Br(),
        dbc.Label('Y Axis', html_for='dropdown-plot-y'),
        dropdown_plot_y,
        html.Br(),
        dbc.Label('Z Axis (Optional), choose 1 Y only.', html_for='dropdown-plot-z'),
        dropdown_plot_z,
        html.Br(),
        dbc.Label('Line Type', html_for='dropdown-plot-xyz-type'),
        dropdown_plot_xyz_type,
        html.Br(),
        btn_add_chart_xyz,
    ]), className='mt-3 mb-3')

    sidebar_page2 = dbc.Card(dbc.CardBody([
        dbc.Label('Polar r', html_for='dropdown-plot-r'),
        dropdown_plot_r,
        html.Br(),
        dbc.Label('Polar theta', html_for='dropdown-plot-theta'),
        dropdown_plot_theta,
        html.Br(),
        dbc.Label('Plotting Type', html_for='dropdown-plot-rt-type'),
        dropdown_plot_rt_type,
        html.Br(),
        btn_add_chart_polar,
    ]), className='mt-3 mb-3')

    sidebar_ctrl = html.Div([
        dbc.Tabs([
            dbc.Tab(sidebar_page1, label='XYZ Graph'),
            dbc.Tab(sidebar_page2, label='Polar Graph'),
            dbc.Tab(html.Div([]), label='Other', disabled=True),
        ]),
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
        dbc.Card(dbc.CardBody([
            serial_options
        ]), className='mt-3 mb-3'),
        html.Hr(),
    ])

    # Plot Section

    plot_col1 = dbc.Col([])
    plot_col2 = dbc.Col([])
    plot_col3 = dbc.Col([])
    plot_area = dbc.Row([plot_col1, plot_col2, plot_col3])

    @staticmethod
    def make_new_chart(
            data: pandas.DataFrame,
            x_key: str, y_keys: list[str] | str, z_key: str,
            r_key: str, theta_key: str,
            line_style: str, plot_type: str):
        if plot_type == 'xyz':
            if z_key is not None:
                if isinstance(y_keys, str):
                    # 3D line chart with one Y.
                    if line_style == 'scatter':
                        return Chart.make_scatter_chart_3d(data, x_key, y_keys, z_key)
                    return Chart.make_line_chart_3d(data, x_key, y_keys, z_key)
                elif isinstance(y_keys, list):
                    # 3D line chart with many Y inputs -> Choose only first one.
                    if line_style == 'scatter':
                        return Chart.make_scatter_chart_3d(data, x_key, y_keys[0], z_key)
                    return Chart.make_line_chart_3d(data, x_key, y_keys[0], z_key)

            if line_style == 'scatter':
                return Chart.make_scatter_chart_2d(data, x_key, y_keys)
            # Default chart type: 2D line chart
            return Chart.make_line_chart_2d(data, x_key, y_keys)
        elif plot_type == 'polar':
            if line_style == 'bar':
                return Chart.make_bar_polar_chart(data, r_key, theta_key)
            return Chart.make_scatter_polar_chart(data, r_key, theta_key)

    @staticmethod
    def make_plot_area(
            data: pandas.DataFrame,
            x_key: str = None, y_keys: list[str] | str = None, z_key: str = None,
            r_key: str = None, theta_key: str = None,
            line_style: str = 'line', plot_type: str = 'xyz'):
        __graph = Component.make_new_chart(data, x_key, y_keys, z_key, r_key, theta_key, line_style, plot_type)
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
    ], fluid=True)], className='mb-5')

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
    ], fluid=True)], className='mb-5')

    @staticmethod
    def de_flatten(flats: list, cols: int = 3):
        layout = [[] for _ in range(cols)]
        for i, e in enumerate(flats):
            layout[i % cols].append(e)
        return layout

    @staticmethod
    def page_404(url):
        return dbc.Container([
            html.H1('404: Not found!', className='text-danger'),
            html.Hr(),
            html.P('The pathname {} was not recognised...'.format(url), className='lead'),
        ], fluid=True, className="py-3")
