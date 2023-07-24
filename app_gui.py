import os
import sys
import threading

import time
from deps import *
from deps.gui import *
from deps.gui import Chart

pd.set_option("display.max_colwidth", None)

HOME_LATITUDE, HOME_LONGITUDE = 13.023548, 101.450420
HOME_ALTITUDE = 20

APP_NAME = __name__
USE_DEBUG = False
USE_MOCK = False
ALL_BAUD_OPT = [{'label': k, 'value': k} for k in ALL_BAUD_STR]

if sys.version_info < (3, 10):
    raise AssertionError('Required Python 3.10 or newer, please install appropriate version!')

if HOME_LATITUDE is None:
    raise ValueError('Please define the station\'s latitude!')

if HOME_LONGITUDE is None:
    raise ValueError('Please define the station\'s longitude!')

if HOME_LONGITUDE is None:
    raise ValueError('Please define the station\'s altitude!')

HOME_GEO = GeoCoordinate(HOME_LATITUDE, HOME_LONGITUDE, HOME_ALTITUDE)


class ProgramGUI(Program):
    app = Dash(
        APP_NAME,
        assets_folder='deps/gui/assets',
        meta_tags=[{'name': 'viewport',
                    'content': 'width=device-width, initial-scale=1'}],
        prevent_initial_callbacks=True,
        suppress_callback_exceptions=True,
        title=APP_TITLE,
        update_title=None
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
        self.settings = PreferencesTree.from_file(os.path.abspath('settings.json'), 'json')
        self.data_format_dict = PreferencesTree.from_file(os.path.abspath('data_format.json'), 'json')
        self.header = self.settings['header']
        self.file_name = self.settings['file_name']
        self.extension = self.settings['file_extension']

        self.kml_keys = {
            dev_id: {
                'lat': self.settings['kml_keys'][dev_id]['lat'],
                'lon': self.settings['kml_keys'][dev_id]['lon'],
                'alt': self.settings['kml_keys'][dev_id]['alt']
            } for dev_id in self.settings['kml_keys']
        }

        self.to_plot: list = self.settings['plot']
        self.trim_length = self.settings['data_points']
        self.all_charts = []
        self.all_plots = []
        self.data_ready = False

        # Generating information, keys for referencing
        self.id_to_index = {
            dev_id: i for i, dev_id in enumerate(self.data_format_dict.tree)
        }

        self.index_id_list = [dev_id for dev_id in self.data_format_dict.tree]
        self.index_to_id = lambda index: self.index_id_list[index] if index < len(self.index_id_list) else -1

        self.data_format_mod = [
            dev_field(dev_id, e) for dev_id, data_list in self.data_format_dict.tree.items() for e in data_list
        ]

        self.data_options = [{'label': k, 'value': k} for k in self.data_format_mod]

        # Modify keys for each item to plot, prefix them with device prefix
        # for dev_id, plot_list in self.to_plot.items():
        #     for plot_item in plot_list:
        for plot_item in self.to_plot:
            if 'x' in plot_item:
                for dev_id in plot_item['x']:
                    plot_item['x'] = dev_field(dev_id, plot_item['x'][dev_id])
            if 'y' in plot_item:
                tmp_y = []
                for dev_id in plot_item['y']:
                    if isinstance(plot_item['y'][dev_id], list):
                        tmp_y.extend(dev_field(dev_id, e) for e in plot_item['y'][dev_id])
                    elif isinstance(plot_item['y'][dev_id], str):
                        tmp_y.append(dev_field(dev_id, plot_item['y'][dev_id]))
                plot_item['y'] = tmp_y
            if 'z' in plot_item:
                for dev_id in plot_item['z']:
                    plot_item['z'] = dev_field(dev_id, plot_item['z'][dev_id])
            if 'r' in plot_item:
                for dev_id in plot_item['r']:
                    plot_item['r'] = dev_field(dev_id, plot_item['r'][dev_id])
            if 'theta' in plot_item:
                for dev_id in plot_item['theta']:
                    plot_item['theta'] = dev_field(dev_id, plot_item['theta'][dev_id])

        # Backend: Serial Components
        self.serial_ports = [SerialPort() for _ in range(NUM_SERIAL)]
        self.port_names = [''] * NUM_SERIAL
        self.port_bauds = [115200] * NUM_SERIAL
        self.serial_readers = [SerialReader(self.serial_ports[i]) for i in range(NUM_SERIAL)]
        self.queue_serials = [Queue() for _ in range(NUM_SERIAL)]

        # Backend: Device 0 Data Parser and File Writer Components
        self.parsers = [
            StringParser(self.data_format_dict[str(i)])
            if str(i) in self.data_format_dict.tree else None
            for i in range(NUM_SERIAL)
        ]
        self.writers = [FileWriter(__file__, self.file_name, self.extension, device_id=i) for i in range(NUM_SERIAL)]
        self.queue_csvs = [Queue() for _ in range(NUM_SERIAL)]
        self.queue_coords = [Queue() for _ in range(NUM_SERIAL)]

        # Serial Device 0 Thread
        self.serial_threads = [ThreadSerial(
            reader, parser, q_ser
        ) for reader, parser, q_ser in zip(self.serial_readers, self.parsers, self.queue_serials)]

        # File Writer Thread
        self.writer_threads = [ThreadFileWriter(
            writer, q_csv, q_coord
        ) for writer, q_csv, q_coord in zip(self.writers, self.queue_csvs, self.queue_coords)]

        # Program DataFrame
        self.data = Data(self.data_format_mod)
        self.data_len = tuple(len(self.data_format_dict.tree[e]) for e in self.data_format_dict.tree)
        self.data_back = [0] * len(self.data_format_mod)
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
        self.serial_connections = [False] * NUM_SERIAL
        self.serial_connected_lut = set()

        self.azimuth = [0.0, 0.0]
        self.elevation = [0.0, 0.0]
        self.los = [0.0, 0.0]
        self.hcd = [0.0, 0.0]

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
            for i in [1, 0]:
                latest_data = add_front_df(latest_data, f'[{i}] Elevation', f'{self.elevation[i]}°')
                latest_data = add_front_df(latest_data, f'[{i}] Azimuth', f'{self.azimuth[i]}°')
                latest_data = add_front_df(latest_data, f'[{i}] Line of Sight', f'{self.los[i]} m')
                latest_data = add_front_df(latest_data, f'[{i}] Ground Distance', f'{self.hcd[i]} m')

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
                *(Output(dropdown_port, 'options') for dropdown_port in Component.dropdown_ports),
                *(Output(dropdown_baud, 'options') for dropdown_baud in Component.dropdown_bauds)
            ],
            Input(Component.interval_slow, 'n_intervals')
        )
        def render_serial_options(_interval):
            self.serial_ports[0].refresh()
            all_ports = self.serial_ports[0].port_pair.keys()
            new_opt = [{'label': k, 'value': k} for k in all_ports]
            return [*([new_opt] * NUM_SERIAL), *([ALL_BAUD_OPT] * NUM_SERIAL)]

        # Lock serial elements on connection and disconnection
        @app.callback(
            [
                *(Output(btn_connect, 'className') for btn_connect in Component.btn_connects),
                *(Output(btn_disconnect, 'className') for btn_disconnect in Component.btn_disconnects),
                *(Output(dropdown_port, 'disabled') for dropdown_port in Component.dropdown_ports),
                *(Output(dropdown_baud, 'disabled') for dropdown_baud in Component.dropdown_bauds),
            ],
            [
                Input(Component.interval_slow, 'n_intervals'),
                *(Input(btn_connect, 'n_clicks') for btn_connect in Component.btn_connects),
                *(Input(btn_disconnect, 'n_clicks') for btn_disconnect in Component.btn_disconnects),
            ],
            [
                *(State(dropdown_port, 'value') for dropdown_port in Component.dropdown_ports),
                *(State(dropdown_baud, 'value') for dropdown_baud in Component.dropdown_bauds)
            ]
        )
        def btn_serial_connect(*args):
            # Unused, leave commented.
            # btn_connects = args[1:1 + NUM_SERIAL]
            # btn_disconnects = args[1 + NUM_SERIAL:1 + 2 * NUM_SERIAL]

            serial_ports = args[1 + 2 * NUM_SERIAL:1 + 3 * NUM_SERIAL]
            serial_bauds = args[1 + 3 * NUM_SERIAL:1 + 4 * NUM_SERIAL]

            btn_clicked = ctx.triggered_id

            for i, (serial_port, serial_baud) in enumerate(zip(serial_ports, serial_bauds)):
                if btn_clicked == Component.btn_connects[i].id:
                    if not serial_port or serial_port in self.serial_connected_lut:
                        continue
                    self.port_names[i] = serial_port or self.port_names[i]
                    self.port_bauds[i] = self.port_bauds[i] if serial_baud is None else int(serial_baud)

                    self.__connect_serial(i)
                    self.__start(i)
                elif btn_clicked == Component.btn_disconnects[i].id:
                    self.__stop(i)
                    self.__disconnect_serial(i)

            ret_val1 = []
            ret_val2 = []
            ret_val3 = []
            ret_val4 = []

            for i in range(NUM_SERIAL):
                if self.serial_connections[i]:
                    ret_val1.append('mx-1 btn-primary disabled')
                    ret_val2.append('mx-1 btn-danger')
                    ret_val3.append(True)
                    ret_val4.append(True)
                elif i >= len(self.data_format_dict):
                    ret_val1.append('mx-1 btn-primary disabled')
                    ret_val2.append('mx-1 btn-danger disabled')
                    ret_val3.append(True)
                    ret_val4.append(True)
                else:
                    ret_val1.append('mx-1 btn-primary')
                    ret_val2.append('mx-1 btn-danger disabled')
                    ret_val3.append(False)
                    ret_val4.append(False)

            return [*ret_val1, *ret_val2, *ret_val3, *ret_val4]

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
                for plot_item in self.to_plot:
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
                        pass
                        # __new_chart = Chart.make_mesh_render()
                        # self.all_charts.append(Chart.dict_info(
                        #     model='',
                        #     plot_type=plot_item['plot_type']
                        # ))
                        # self.all_plots.append(__new_chart)

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
            elif event_polling and self.data_ready:
                for i, __chart in enumerate(self.all_charts):
                    if __chart['plot_type'] in [Chart.PLOT_XYZ, Chart.PLOT_POLAR]:
                        # then plot
                        plot_data = self.data.df.tail(self.trim_length)
                        try:
                            self.all_plots[i] = Component.make_plot_area(
                                data=plot_data,
                                x_key=__chart['x'],
                                y_keys=__chart['y'],
                                z_key=__chart['z'],
                                r_key=__chart['r'],
                                theta_key=__chart['theta'],
                                line_style=__chart['style'],
                                plot_type=__chart['plot_type']
                            )
                        except ValueError as e:
                            print(plot_data.dtypes)
                            for yk in __chart['y']:
                                print(plot_data[yk])

                    elif __chart['plot_type'] == Chart.PLOT_MESH:
                        pass
                        # self.all_plots[i] = Chart.make_mesh_render()

            return Content.unflatten(self.all_plots)

        @app.callback(
            Output('hidden-div', 'children'),
            Input(Component.btn_pop_chart, 'n_clicks')
        )
        def pop_data(_clicks):
            if self.data.available():
                self.data.pop()
            return []

    def __start(self, i):
        """
        Start the backend

        :return:
        """
        if not self.serial_connections[i]:
            return

        self.serial_threads[i].start()
        self.writer_threads[i].start()

    def __stop(self, i):
        self.serial_threads[i].stop()
        self.writer_threads[i].stop()

    def __connect_serial(self, i):
        self.serial_connections[i] = self.serial_ports[i].connect(
            self.port_names[i], self.port_bauds[i],
            auto_reconnect=True
        )
        if self.serial_connections[i]:
            self.serial_connected_lut.add(self.port_names[i])
        return self.serial_connections[i]

    def __disconnect_serial(self, i):
        self.serial_ports[i].disconnect()
        if self.port_names[i] in self.serial_connected_lut:
            self.serial_connected_lut.remove(self.port_names[i])
        self.serial_connections[i] = False

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
            for i in range(NUM_SERIAL):
                if self.queue_serials[i].available():
                    dat_dict: dict = self.queue_serials[i].pop()
                    dat = list(dat_dict.values())
                    if i == 0:
                        start_idx = 0
                    else:
                        start_idx = self.data_len[i - 1]
                    for j, x in enumerate(dat, start_idx):
                        self.data_back[j] = x
                    self.data.push(self.data_back)

                    print(f'{i}: {self.data_back}')

                    if str(i) in self.kml_keys:
                        curr_coord = GeoCoordinate(
                            dat_dict[self.kml_keys[str(i)]['lat']],
                            dat_dict[self.kml_keys[str(i)]['lon']],
                            dat_dict[self.kml_keys[str(i)]['alt']]
                        )
                        coord_pair = GeoPair(HOME_GEO, curr_coord)

                        self.queue_coords[i].push(
                            curr_coord
                        )

                        if str(i) == "0":
                            self.los[0] = coord_pair.line_of_sight
                            self.hcd[0] = coord_pair.ground_distance
                            self.azimuth[0] = coord_pair.azimuth
                            self.elevation[0] = coord_pair.elevation_approx
                        else:
                            self.los[1] = coord_pair.line_of_sight
                            self.hcd[1] = coord_pair.ground_distance
                            self.azimuth[1] = coord_pair.azimuth
                            self.elevation[1] = coord_pair.elevation_approx

                    self.queue_csvs[i].push(dat)

                    self.data_no += 1

            self.data_ready = False

            for i, __chart in enumerate(self.all_charts):
                if __chart['plot_type'] in [Chart.PLOT_XYZ, Chart.PLOT_POLAR]:
                    # check for data validity before plot
                    while self.data.available():
                        check_bool = True

                        if __chart['x'] is not None:
                            check_bool &= not isinstance(self.data.back()[__chart['x']], str)
                        if __chart['y'] is not None:
                            for y_key in __chart['y']:
                                check_bool &= not isinstance(self.data.back()[y_key], str)
                        if __chart['z'] is not None:
                            check_bool &= not isinstance(self.data.back()[__chart['z']], str)
                        if __chart['r'] is not None:
                            check_bool &= not isinstance(self.data.back()[__chart['r']], str)
                        if __chart['theta'] is not None:
                            check_bool &= not isinstance(self.data.back()[__chart['theta']], str)

                        if check_bool:
                            break
                        else:
                            if self.data.available():
                                self.data.pop()

            self.data_ready = True

            time.sleep(0.010)

    def start(self):
        """
        Start the program (global, flask app)

        :return:
        """
        import logging
        logging.getLogger('werkzeug').setLevel(logging.ERROR)

        self.backend_thread.start()
        self.app.run(host='localhost',
                     port=8050,
                     debug=USE_DEBUG)

    def stop(self):
        for i in range(NUM_SERIAL):
            self.__stop(i)
            self.serial_ports[i].disconnect(destructor=True)

        self.backend_status = False
        self.backend_thread.join(timeout=2.000)
        self.backend_thread = None


def main():
    program = ProgramGUI()
    program.start()
    program.stop()


if __name__ == '__main__':
    main()
