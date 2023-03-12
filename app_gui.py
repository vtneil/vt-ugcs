from deps import *
from deps.gui import *

app = Dash(__name__, assets_folder='deps/gui/assets')
app.title = APP_TITLE

app.layout = html.Div([
    dbc.Container([
        dcc.Location(id='url'),
        MenuBar,
        Content.content
    ], fluid=True)
], className='m-5')


@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
)
def render_content(url):
    if url == '/':
        return Content.home
    elif url == '/settings':
        return Content.settings

    return Content.page_404(url)


if __name__ == '__main__':
    app.run_server(debug=True)
