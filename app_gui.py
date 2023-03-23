import os
import threading

import time
from deps import *
from deps.gui import *
from deps.gui import Chart

APP_NAME = __name__
USE_DEBUG = False
USE_MOCK = False
ALL_BAUD_OPT = [{'label': k, 'value': k} for k in ALL_BAUD_STR]


class ProgramGUI(Program):
    app = Dash(
        APP_NAME,
        assets_folder='deps/gui/assets',
        meta_tags=[{'name': 'viewport',
                    'content': 'width=device-width, initial-scale=1'}],
        prevent_initial_callbacks=True,
        suppress_callback_exceptions=True,
        title=APP_TITLE
    )

    def __init__(self):
        # Flask App
        self.app.layout = html.Div([
            dbc.Container([
                dcc.Location(id='url'),
                MenuBar,
                html.Div([
                    Content.content
                ], className='mt-5 pt-5 pb-5'),
                Component.interval_slow,
                Component.interval_fast,
                Component.interval_once
            ], fluid=True),
            html.Div([], id='hidden-div', style={'display': 'none'}),
            html.P('', id='data-counter', style={'display': 'none'}),
            html.Footer([html.P(FOOTER_TEXT, id='footer')]),
        ], className='m-5')

        # Backend: General Components
        self.settings = PreferencesTree.from_file(os.path.abspath('settings.json'))
        self.data_format_dict = PreferencesTree.from_file(os.path.abspath('data_format.json'))
        self.header = self.settings['header']
        self.file_name = self.settings['file_name']
        self.extension = self.settings['file_extension']
        self.key_lat = self.settings['lat_key']
        self.key_lon = self.settings['lon_key']
        self.key_alt = self.settings['alt_key']
        self.to_plot: dict = self.settings['plot']
        self.trim_length = self.settings['data_points']
        self.all_charts = []
        self.all_plots = []

        # Generating information, keys for referencing
        self.data_format_mod = ['d{}_{}'.format(k, e) for k, v in self.data_format_dict.tree.items() for e in v]
        self.data_options = [{'label': k, 'value': k} for k in self.data_format_mod]
        for dev_id, plot_list in self.to_plot.items():
            for plot_item in plot_list:
                if 'x' in plot_item:
                    plot_item['x'] = 'd{}_{}'.format(dev_id, plot_item['x'])
                if 'y' in plot_item:
                    plot_item['y'] = ['d{}_{}'.format(dev_id, e) for e in plot_item['y']]
                if 'z' in plot_item:
                    plot_item['z'] = 'd{}_{}'.format(dev_id, plot_item['z'])
                if 'r' in plot_item:
                    plot_item['r'] = 'd{}_{}'.format(dev_id, plot_item['r'])
                if 'theta' in plot_item:
                    plot_item['theta'] = 'd{}_{}'.format(dev_id, plot_item['theta'])

        # Backend: Serial Components
        self.serial_port = SerialPort()
        self.port_name = ''
        self.port_baud = 115200
        self.serial_reader = SerialReader(self.serial_port)
        self.queue_serial = Queue()

        # Backend: Device 0 Data Parser and File Writer Components
        self.parser = StringParser(self.data_format_mod)
        self.writer = FileWriter(__file__, self.file_name, self.extension)
        self.queue_csv = Queue()
        self.queue_coord = Queue()

        # Serial Device 0 Thread
        self.serial_thread = ThreadSerial(
            self.serial_reader, self.parser, self.queue_serial
        )

        # File Writer Thread
        self.writer_thread = ThreadFileWriter(
            self.writer, self.queue_csv, self.queue_coord
        )

        # Program DataFrame
        self.data = Data(self.data_format_mod)
        self.data_no = 0
        self.first_load = True

        # Initialize Dash callbacks
        self.__init_callbacks()

        # Backend Thread (Main program)
        self.backend_status = True
        self.backend_thread = threading.Thread(
            target=self.__backend, daemon=True
        )

        # Misc Variables
        self.serial_connection = False

    def __init_callbacks(self):
        app = self.app

        # Render Data table
        @app.callback(
            Output(Component.sidebar_dataframe, 'children'),
            Input(Component.interval_fast, 'n_intervals')
        )
        def render_table(_intervals):
            latest_data = pd.DataFrame({
                'key': self.data_format_mod,
                'value': self.data.back().to_list() if self.data.available() else [None] * len(self.data_format_mod)
            })

            # BEGIN USER ADD OPTIONAL DATA SECTION
            add_to_df(latest_data, 'azimuth', 'test_text')
            # END USER ADD OPTIONAL DATA SECTION

            return dbc.Table.from_dataframe(
                latest_data,
                bordered=True, responsive=True, hover=True, striped=True
            )

        # Render Page Content Section on URL change
        @app.callback(
            Output(Content.content, 'children'),
            Input('url', 'pathname'),
        )
        def render_content(url):
            if url == '/':
                return Content.plot
            elif url == '/settings':
                return Content.settings

            return Content.page_404(url)

        # Refresh Serial port dropdown options
        @app.callback(
            [
                Output(Component.dropdown_port, 'options'),
                Output(Component.dropdown_baud, 'options')
            ],
            Input(Component.interval_slow, 'n_intervals')
        )
        def render_serial_options(_interval):
            self.serial_port.refresh()
            all_ports = self.serial_port.port_pair.keys()
            new_opt = [{'label': k, 'value': k} for k in all_ports]
            return new_opt, ALL_BAUD_OPT

        # Lock serial elements on connection and disconnection
        @app.callback(
            [
                Output(Component.btn_connect, 'className'),
                Output(Component.btn_disconnect, 'className'),
                Output(Component.dropdown_port, 'disabled'),
                Output(Component.dropdown_baud, 'disabled'),
            ],
            [
                Input(Component.btn_connect, 'n_clicks'),
                Input(Component.btn_disconnect, 'n_clicks'),
                Input(Component.interval_slow, 'n_intervals'),
            ],
            [
                State(Component.dropdown_port, 'value'),
                State(Component.dropdown_baud, 'value')
            ]
        )
        def btn_serial_connect(_connect, _disconnect, _intervals, serial_port, serial_baud):
            btn_clicked = ctx.triggered_id
            if btn_clicked == Component.btn_connect.id:
                self.port_name = serial_port or self.port_name
                self.port_baud = self.port_baud if serial_baud is None else int(serial_baud)
                self.__connect_serial()
                self.__start()
            elif btn_clicked == Component.btn_disconnect.id:
                self.__stop()
                self.__disconnect_serial()

            if self.serial_connection:
                return (
                    'mx-1 btn-primary disabled',
                    'mx-1 btn-danger',
                    True, True
                )
            else:
                return (
                    'mx-1 btn-primary',
                    'mx-1 btn-danger disabled',
                    False, False
                )

        # Refresh Data View Dropdown
        @app.callback(
            [
                Output(Component.dropdown_plot_x, 'options'),
                Output(Component.dropdown_plot_y, 'options'),
                Output(Component.dropdown_plot_z, 'options'),
                Output(Component.dropdown_plot_r, 'options'),
                Output(Component.dropdown_plot_theta, 'options'),
                Output(Component.dropdown_plot_xyz_type, 'options'),
                Output(Component.dropdown_plot_rt_type, 'options'),
            ],
            [
                Input(Component.interval_slow, 'n_intervals'),
            ]
        )
        def render_data_view_options(_interval):
            return self.data_options, self.data_options, self.data_options, self.data_options, self.data_options, \
                Chart.LINE_TYPES, Chart.POLAR_TYPES

        # Render charts
        @app.callback(
            [
                Output(Component.plot_col1, 'children'),
                Output(Component.plot_col2, 'children'),
                Output(Component.plot_col3, 'children'),
            ],
            [
                Input(Component.interval_once, 'n_intervals'),
                Input(Component.interval_slow, 'n_intervals'),
                Input(Component.btn_add_chart_xyz, 'n_clicks'),
                Input(Component.btn_add_chart_polar, 'n_clicks'),
            ],
            [
                State(Component.dropdown_plot_x, 'value'),
                State(Component.dropdown_plot_y, 'value'),
                State(Component.dropdown_plot_z, 'value'),
                State(Component.dropdown_plot_r, 'value'),
                State(Component.dropdown_plot_theta, 'value'),
                State(Component.dropdown_plot_xyz_type, 'value'),
                State(Component.dropdown_plot_rt_type, 'value'),
            ]
        )
        def render_chart(_intervals_1, _intervals_2, _clicks_xyz, _clicks_polar,
                         x_val, y_vals, z_val, r_val, theta_val, line_type, polar_type):
            event = ctx.triggered_id

            event_first_load = (event == Component.interval_once.id and self.first_load)
            event_click_xyz = (event == Component.btn_add_chart_xyz.id and x_val and y_vals and line_type)
            event_click_polar = (event == Component.btn_add_chart_polar.id and r_val and theta_val and polar_type)
            event_polling = (event == Component.interval_slow.id and not self.first_load)

            # First Load
            if event_first_load:
                self.first_load = False
                for device_id, device_plot_list in self.to_plot.items():
                    for plot_item in device_plot_list:
                        plot_type = plot_item['plot_type']
                        if plot_type == Chart.PLOT_XYZ:
                            __z_key = plot_item['z'] if 'z' in plot_item else None
                            __new_chart = Component.make_plot_area(
                                data=self.data.df.tail(self.trim_length),
                                x_key=plot_item['x'],
                                y_keys=plot_item['y'],
                                z_key=__z_key,
                                line_style=plot_item['style'],
                                plot_type=plot_type
                            )
                            self.all_charts.append(Chart.dict_info(
                                x=plot_item['x'],
                                y=plot_item['y'],
                                z=__z_key,
                                style=plot_item['style'],
                                plot_type=plot_item['plot_type']
                            ))
                            self.all_plots.append(__new_chart)
                        elif plot_type == Chart.PLOT_POLAR:
                            __new_chart = Component.make_plot_area(
                                data=self.data.df.tail(self.trim_length),
                                r_key=plot_item['r'],
                                theta_key=plot_item['theta'],
                                line_style=plot_item['style'],
                                plot_type=plot_type
                            )
                            self.all_charts.append(Chart.dict_info(
                                r=plot_item['r'],
                                theta=plot_item['theta'],
                                style=plot_item['style'],
                                plot_type=plot_item['plot_type']
                            ))
                            self.all_plots.append(__new_chart)
                        elif plot_type == Chart.PLOT_MESH:
                            __new_chart = Chart.make_mesh_render()
                            self.all_charts.append(Chart.dict_info(
                                model='',
                                plot_type=plot_item['plot_type']
                            ))
                            self.all_plots.append(__new_chart)

            # When Click Add XYZ Chart
            elif event_click_xyz:
                __new_chart = Component.make_plot_area(
                    data=self.data.df.tail(self.trim_length),
                    x_key=x_val,
                    y_keys=y_vals,
                    z_key=z_val,
                    line_style=line_type,
                    plot_type=Chart.PLOT_XYZ
                )
                self.all_charts.append(Chart.dict_info(
                    x=x_val,
                    y=y_vals,
                    z=z_val,
                    style=line_type,
                    plot_type=Chart.PLOT_XYZ
                ))
                self.all_plots.append(__new_chart)

            # When Click Add Polar Chart
            elif event_click_polar:
                self.all_charts.append(Chart.dict_info(
                    r=r_val,
                    theta=theta_val,
                    style=polar_type,
                    plot_type=Chart.PLOT_POLAR
                ))
                __new_chart = Component.make_plot_area(
                    data=self.data.df.tail(self.trim_length),
                    r_key=r_val,
                    theta_key=theta_val,
                    line_style=polar_type,
                    plot_type=Chart.PLOT_POLAR
                )
                self.all_plots.append(__new_chart)

            # Data Polling/Updating
            elif event_polling:
                for i, __chart in enumerate(self.all_charts):
                    if __chart['plot_type'] in [Chart.PLOT_XYZ, Chart.PLOT_POLAR]:
                        self.all_plots[i] = Component.make_plot_area(
                            data=self.data.df.tail(self.trim_length),
                            x_key=__chart['x'],
                            y_keys=__chart['y'],
                            z_key=__chart['z'],
                            r_key=__chart['r'],
                            theta_key=__chart['theta'],
                            line_style=__chart['style'],
                            plot_type=__chart['plot_type']
                        )
                    elif __chart['plot_type'] == Chart.PLOT_POLAR:
                        print('render')
                        self.all_plots[i] = Chart.make_mesh_render()

            layout = Content.unflatten(self.all_plots)
            return layout

        @app.callback(
            Output('hidden-div', 'children'),
            Input(Component.btn_pop_chart, 'n_clicks')
        )
        def pop_data(_clicks):
            if self.data.available():
                self.data.pop()
            return []

    def __start(self):
        """
        Start the backend

        :return:
        """
        if not self.serial_connection:
            return

        self.serial_thread.start()
        self.writer_thread.start()

    def __stop(self):
        self.serial_thread.stop()
        self.writer_thread.stop()

    def __connect_serial(self):
        self.serial_connection = self.serial_port.connect(
            self.port_name, self.port_baud,
            auto_reconnect=True
        )
        return self.serial_connection

    def __disconnect_serial(self):
        self.serial_port.disconnect()
        self.serial_connection = False

    def __backend_mock(self):
        i = 0
        while self.backend_status:
            dat = [
                0.5 * i ** 2 + 0.8 * j ** 2 if j > 1 else (0 if j == 0 else i)
                for j in range(len(self.data_format_mod))
            ]
            dat[2] = dat[2] % 360
            self.data.push(dat)
            i += 1
            time.sleep(0.100)

    def __backend(self):
        # Uncomment to use mock backend loop for testing
        if USE_MOCK:
            self.__backend_mock()

        while self.backend_status:
            if self.queue_serial.available():
                dat_dict: dict = self.queue_serial.pop()
                dat = list(dat_dict.values())

                self.data.push(dat)
                self.queue_coord.push(
                    GeoCoordinate(dat_dict[self.key_lat], dat_dict[self.key_lon], dat_dict[self.key_alt])
                )
                self.queue_csv.push(dat)

                self.data_no += 1

            time.sleep(0.100)

    def start(self):
        """
        Start the program (global, flask app)

        :return:
        """
        import logging
        logging.getLogger('werkzeug').setLevel(logging.ERROR)

        self.backend_thread.start()
        self.app.run_server(debug=USE_DEBUG)

    def stop(self):
        self.__stop()
        self.serial_port.disconnect(destructor=True)

        self.backend_status = False
        self.backend_thread.join(timeout=2.000)
        self.backend_thread = None


def main():
    program = ProgramGUI()
    program.start()
    program.stop()


if __name__ == '__main__':
    main()
