from .__includes import *

MenuBar = html.Div([
    html.H1(APP_TITLE),

    html.Div([
        html.Div([
            dbc.Nav([
                dbc.NavLink('Home', href='/', active='exact'),
                dbc.NavLink('Settings', href='/settings', active='exact'),
                dbc.NavLink('Info', href='/info', active='exact'),
            ], className='gap-2', pills=True)
        ])
    ], className='p-3 bg-light rounded-4 w-100 mb-3'),
], id='menubar')
