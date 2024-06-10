from .__includes import *

MenuBar = html.Div([
    html.Div([
        dbc.NavbarSimple([
            dbc.NavItem(dbc.NavLink('Home', href='/', active='exact')),
            dbc.NavItem(dbc.NavLink('Settings', href='/settings', active='exact')),
            dbc.NavItem(dbc.NavLink('Info', href='/info', active='exact')),
            dbc.NavItem(dbc.NavLink('Visit GitHub', href='https://github.com/vtneil/vnet-ugcs',
                                    target='_blank', external_link=True)),
        ], brand=APP_TITLE, brand_href='/',
            color='dark', dark=True, fixed='top')
    ])
], id='menubar')
