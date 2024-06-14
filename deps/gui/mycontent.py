import pandas

from .__includes import *
from .mychart import Chart

INTERVAL_SLOW = 1000
INTERVAL_FAST = 500


class BaseComponent:
    def __init__(self):
        self.dropdown_ports = [dcc.Dropdown(
            [], id=f'dropdown-port-{i}', disabled=True, clearable=False,
            persistence='true', persistence_type='session',
            placeholder='Choose serial port from below',
        ) for i in range(NUM_MAX_SERIAL)]

        self.dropdown_bauds = [dcc.Dropdown(
            [], id=f'dropdown-baud-{i}', disabled=True, clearable=False,
            persistence='true', persistence_type='session',
            placeholder='Choose baud rate from below'
        ) for i in range(NUM_MAX_SERIAL)]

        self.btn_connects = [dbc.Button(
            'Connect', id=f'btn-connect-{i}',
            className='mx-1 btn-primary disabled'
        ) for i in range(NUM_MAX_SERIAL)]

        self.btn_disconnects = [dbc.Button(
            'Disconnect', id=f'btn-disconnect-{i}',
            className='mx-1 btn-danger disabled'
        ) for i in range(NUM_MAX_SERIAL)]

        # Interval

        self.interval_slow = dcc.Interval(
            id='interval-slow',
            interval=INTERVAL_SLOW,
            disabled=True,
            n_intervals=0
        )

        self.interval_fast = dcc.Interval(
            id='interval-fast',
            interval=INTERVAL_FAST,
            disabled=True,
            n_intervals=0
        )

        self.interval_once = dcc.Interval(
            id='interval-once',
            interval=INTERVAL_FAST,
            n_intervals=0,
            max_intervals=1
        )

        self.interval_load = dcc.Interval(
            id='interval-load',
            interval=2000,
            n_intervals=0,
            max_intervals=1
        )

        # Global Components

        self.serial_options = [html.Div([
            dbc.Label('Serial Device Port', html_for=f'dropdown-port-{i}'),
            self.dropdown_ports[i],

            html.Br(),

            dbc.Label('Baud Rate', html_for=f'dropdown-baud-{i}'),
            self.dropdown_bauds[i],

            html.Br(),

            html.Div([
                self.btn_connects[i],
                self.btn_disconnects[i]
            ]),

            html.Br(),
            html.Hr(),
            html.Br()
        ]) for i in range(NUM_MAX_SERIAL)]

        self.uplink_dd = dcc.Dropdown(options=[], id='dropdown-uplink', className='mx-1 btn-primary')
        self.uplink_submit = dbc.Button('Send', id='btn-submit-uplink')
        self.uplink_options = dbc.Row(children=[
            dbc.Col(children=self.uplink_dd, width=9),
            dbc.Col(children=self.uplink_submit)
        ])

        self.sidebar_dataframe = html.Div([])

        self.dropdown_plot_x = dcc.Dropdown(
            options=[], id='dropdown-plot-x'
        )

        self.dropdown_plot_y = dcc.Dropdown(
            options=[], id='dropdown-plot-y', multi=True
        )

        self.dropdown_plot_z = dcc.Dropdown(
            options=[], id='dropdown-plot-z'
        )

        self.dropdown_plot_xyz_type = dcc.Dropdown(
            options=[], id='dropdown-plot-xyz-type'
        )

        self.dropdown_plot_r = dcc.Dropdown(
            options=[], id='dropdown-plot-r'
        )

        self.dropdown_plot_theta = dcc.Dropdown(
            options=[], id='dropdown-plot-theta'
        )

        self.dropdown_plot_rt_type = dcc.Dropdown(
            options=[], id='dropdown-plot-rt-type'
        )

        self.btn_add_chart_xyz = dbc.Button('Add Chart to View', id='btn-add-chart-xyz',
                                            className='mx-1 btn-primary')

        self.btn_add_chart_polar = dbc.Button('Add Chart to View', id='btn-add-chart-polar',
                                              className='mx-1 btn-primary')

        self.btn_pop_chart = dbc.Button('Clear Data', id='btn-pop-chart',
                                        className='mx-1 btn-danger')

        self.sidebar_page1 = dbc.Card(dbc.CardBody([
            dbc.Label('X Axis', html_for='dropdown-plot-x'),
            self.dropdown_plot_x,
            html.Br(),
            dbc.Label('Y Axis', html_for='dropdown-plot-y'),
            self.dropdown_plot_y,
            html.Br(),
            dbc.Label('Z Axis (Optional), choose 1 Y only.', html_for='dropdown-plot-z'),
            self.dropdown_plot_z,
            html.Br(),
            dbc.Label('Line Type', html_for='dropdown-plot-xyz-type'),
            self.dropdown_plot_xyz_type,
            html.Br(),
            self.btn_add_chart_xyz,
        ]), className='mt-3 mb-3')

        self.sidebar_page2 = dbc.Card(dbc.CardBody([
            dbc.Label('Polar r', html_for='dropdown-plot-r'),
            self.dropdown_plot_r,
            html.Br(),
            dbc.Label('Polar theta', html_for='dropdown-plot-theta'),
            self.dropdown_plot_theta,
            html.Br(),
            dbc.Label('Plotting Type', html_for='dropdown-plot-rt-type'),
            self.dropdown_plot_rt_type,
            html.Br(),
            self.btn_add_chart_polar,
        ]), className='mt-3 mb-3')

        self.sidebar_ctrl = html.Div([
            dbc.Tabs([
                dbc.Tab(self.sidebar_page1, label='XYZ Graph'),
                dbc.Tab(self.sidebar_page2, label='Polar Graph'),
                dbc.Tab(html.Div([]), label='Other', disabled=True),
            ]),
            self.btn_pop_chart
        ])

        self.sidebar = html.Div([
            html.H3('Uplink Command'),
            self.uplink_options,
            html.Hr(),

            html.H3('Tabular View'),
            self.sidebar_dataframe,
            html.Hr(),

            html.H3('Data View'),
            self.sidebar_ctrl,
            html.Hr(),

            html.H3('Serial Connection'),
            dbc.Card(dbc.CardBody([
                *self.serial_options
            ]), className='mt-3 mb-3'),
            html.Hr(),
        ])

        # Plot Section

        self.plot_col1 = dbc.Col([])
        self.plot_col2 = dbc.Col([])
        self.plot_col3 = dbc.Col([])
        self.plot_area = dbc.Row([self.plot_col1, self.plot_col2, self.plot_col3])

    @staticmethod
    def make_new_chart(
            data: pandas.DataFrame,
            x_key: str, y_keys: list[str] | str, z_key: str,
            r_key: str, theta_key: str,
            line_style: str, plot_type: str):
        if plot_type == Chart.PLOT_XYZ:
            if z_key is not None:
                if isinstance(y_keys, str):
                    # 3D line chart with one Y.
                    if line_style == Chart.STYLE_SCATTER:
                        return Chart.make_scatter_chart_3d(data, x_key, y_keys, z_key)
                    return Chart.make_line_chart_3d(data, x_key, y_keys, z_key)
                elif isinstance(y_keys, list):
                    # 3D line chart with many Y inputs -> Choose only first one.
                    if line_style == Chart.STYLE_SCATTER:
                        return Chart.make_scatter_chart_3d(data, x_key, y_keys[0], z_key)
                    return Chart.make_line_chart_3d(data, x_key, y_keys[0], z_key)

            if line_style == Chart.STYLE_SCATTER:
                return Chart.make_scatter_chart_2d(data, x_key, y_keys)
            # Default chart type: 2D line chart
            return Chart.make_line_chart_2d(data, x_key, y_keys)
        elif plot_type == Chart.PLOT_POLAR:
            if line_style == Chart.STYLE_BAR:
                return Chart.make_bar_polar_chart(data, r_key, theta_key)
            return Chart.make_scatter_polar_chart(data, r_key, theta_key)

    @staticmethod
    def make_plot_area(
            data: pandas.DataFrame,
            x_key: str = None, y_keys: list[str] | str = None, z_key: str = None,
            r_key: str = None, theta_key: str = None,
            line_style: str = Chart.STYLE_LINE, plot_type: str = Chart.PLOT_XYZ):
        __graph = Component.make_new_chart(data, x_key, y_keys, z_key, r_key, theta_key, line_style, plot_type)
        return html.Div([
            __graph
        ])


Component = BaseComponent()


class Content:
    content = html.Div([], id='page-content')

    plot = html.Div([dbc.Container([
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

        *Component.serial_options,

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
    def unflatten(flats: list, cols: int = 3):
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
