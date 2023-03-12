from .__includes import *


def _h2(text: str):
    return html.H2(text, className='mt-3')


def _h3(text: str):
    return html.H3(text, className='mt-5')


class Content:
    content = html.Div([], id='page-content')

    home = html.Div([
        dbc.Container([
            _h2('Live Plot'),
            html.Hr()
        ], fluid=True)
    ])

    settings = html.Div([
        dbc.Container([
            _h2('Settings'),
            html.Hr(),

            html.P('Settings page for serial port management and customization.', className='lead'),

            _h3('Connection'),

            dbc.Label('Serial Device Port', html_for='dropdown-port'),
            dcc.Dropdown([
            ], id='dropdown-port'),
            html.Br(),
            dbc.Label('Baud Rate', html_for='dropdown-baud'),
            dcc.Dropdown([
            ], id='dropdown-baud'),
            html.Br(),
            html.Div([
                dbc.Button('Connect', className='mx-1'),
                dbc.Button('Disconnect', className='mx-1 btn-danger disabled'),
            ]),

            _h3('File'),

            dbc.Label('File Saving Options', html_for='checklist-file'),
            dbc.Checklist([
                {'label': 'Write data to file?', 'value': 1},
                {'label': 'Write Google Earth KML?', 'value': 2},
            ], [1, 2], id='checklist-file', switch=True),

            html.P(str(State('checklist-file', 'value').to_dict()))
        ])
    ])

    @staticmethod
    def page_404(url):
        return dbc.Container([
            html.H1('404: Not found!', className='text-danger'),
            html.Hr(),
            html.P('The pathname {} was not recognised...'.format(url), className='lead'),
        ], fluid=True, className="py-3")
