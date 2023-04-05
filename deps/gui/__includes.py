import os as __os

import pandas as pd
from skimage import io as iio

import plotly.express as px
import plotly.graph_objs as go

from dash import dcc, html, Dash, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import dash_vtk as vtk
from dash_vtk.utils import to_mesh_state
from dash_vtk.utils import to_volume_state
from vtkmodules.vtkImagingCore import vtkRTAnalyticSource

from .parameters import *


# Dash Bootstrap Cheatsheet at https://dashcheatsheet.pythonanywhere.com/


def h2(text: str):
    return html.H2(text, className='mt-3')


def h3(text: str):
    return html.H3(text, className='mt-5')


def add_to_df(df: pd.DataFrame, key: str | None, value: str | int | float | None):
    df.loc[len(df)] = [key, value]


def dev_field(device_id: int | str, field_name: str):
    return 'd{}_{}'.format(device_id, field_name)
