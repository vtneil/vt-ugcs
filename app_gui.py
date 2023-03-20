import os
import threading

import time
from deps import *
from deps.gui import *

APP_NAME = __name__
USE_DEBUG = True
ALL_BAUD_OPT = [{'label': k, 'value': k} for k in ALL_BAUD_STR]


class ProgramGUI(Program):
    app = Dash(
        APP_NAME,
        assets_folder='deps/gui/assets',
        prevent_initial_callbacks=True,
        suppress_callback_exceptions=True,
    )

    def __init__(self):
        # Flask App
        self.app.title = APP_TITLE
        self.app.layout = html.Div([
            dbc.Container([
                dcc.Location(id='url'),
                MenuBar,
                Content.content,
                Component.interval_slow,
                Component.interval_fast,
                Component.interval_once
            ], fluid=True),
            html.Div([], id='hidden-div', style={'display': 'none'}),
            html.P('', id='data-counter', style={'display': 'none'})
        ], className='m-5')

        # Backend: General Components
        self.settings = PreferencesTree.from_file(os.path.abspath('settings.json'))
        self.data_format = PreferencesTree.from_file('data_format.json')
        self.header = self.settings['header']
        self.file_name = self.settings['file_name']
        self.extension = self.settings['file_extension']

        # Backend: Serial Components
        self.serial_port = SerialPort()
        self.port_name = ''
        self.port_baud = 115200
        self.serial_reader = SerialReader(self.serial_port)
        self.queue_serial = Queue()

        # Backend: Device 0 Data Parser and File Writer Components
        self.parser = StringParser(self.data_format['0'])
        self.writer = FileWriter(__file__, self.file_name, self.extension)
        self.queue_csv = Queue()
        self.queue_coord = Queue()

        # More Threads
        self.serial_thread = ThreadSerial(
            self.serial_reader, self.parser, self.queue_serial
        )
        self.writer_thread = ThreadFileWriter(
            self.writer, self.queue_csv, self.queue_coord
        )

        # Program DataFrame
        self.data = Data(self.data_format['0'])
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
            data = pd.DataFrame({
                'Key': self.data_format['0'],
                'Value': self.data.back().to_list() if self.data.available() else [None] * len(self.data_format['0'])
            })
            return dbc.Table.from_dataframe(
                data,
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
        def render_serial_port(_interval):
            self.serial_port.refresh()
            all_ports = self.serial_port.port_pair.keys()
            new_opt = [{'label': k, 'value': k} for k in all_ports]
            return new_opt, ALL_BAUD_OPT

        # Change backend serial information on dropdown input change
        @app.callback(
            Output('hidden-div', 'children'),
            [
                Input(Component.dropdown_port, 'value'),
                Input(Component.dropdown_baud, 'value')
            ]
        )
        def read_serial_opt(serial_port, serial_baud):
            self.port_name = serial_port or self.port_name
            self.port_baud = self.port_baud if serial_baud is None else int(serial_baud)
            return []

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
            ]
        )
        def btn_serial_connect(_connect, _disconnect, _intervals):
            btn_clicked = ctx.triggered_id
            if btn_clicked == Component.btn_connect.id:
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

        # Render initial charts
        @app.callback(
            Output(Component.plot_area, 'children'),
            [
                Input(Component.interval_once, 'n_intervals'),
                Input(Component.btn_add_chart, 'n_clicks'),  # todo
            ]
        )
        def add_chart(_intervals, _clicks):
            event = ctx.triggered_id
            if event == Component.interval_once.id and self.first_load:
                self.first_load = False
                Component.plot_area.children.append(Component.frame_chart(self.data.data, 'a', 'b'))
            elif event == Component.btn_add_chart.id:
                Component.plot_area.children.append(Component.frame_chart(self.data.data, 'a', 'b'))
            return Component.plot_area.children

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

    def __backend(self):
        while self.backend_status:
            if self.queue_serial.available():
                dat_dict: dict = self.queue_serial.pop()
                dat = list(dat_dict.values())
                self.data.push(dat)
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
