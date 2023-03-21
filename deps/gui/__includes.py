import os as __os
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from dash import dcc, html, Dash, Input, Output, State, ctx
from .parameters import *


# Dash Bootstrap Cheatsheet at https://dashcheatsheet.pythonanywhere.com/


def h2(text: str):
    return html.H2(text, className='mt-3')


def h3(text: str):
    return html.H3(text, className='mt-5')
