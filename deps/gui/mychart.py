import numpy as np

from .__includes import *


class Chart:
    PLOT_XYZ = 'xyz'
    PLOT_POLAR = 'polar'
    PLOT_MESH = 'mesh'

    STYLE_LINE = 'line'
    STYLE_SCATTER = 'scatter'
    STYLE_BAR = 'bar'

    LINE_TYPES = ['line', 'scatter']
    POLAR_TYPES = ['bar', 'scatter']
    CHART_PLOT_TYPES = ['']
    MARGIN = dict(l=20, r=20, t=100, b=20)

    @staticmethod
    def make_chart_title(y: str, x: str, z: str = None):
        if z is None:
            return 'Y: [{}] - X: {}'.format(y, x)
        return '({},{},{})'.format(x, y, z)

    @staticmethod
    def make_line_chart_2d(data: pd.DataFrame, x_key: str, y_keys: list[str]):
        fig = px.line(
            data, x=x_key, y=y_keys, title=Chart.make_chart_title(','.join(y_keys), x_key),
        )
        fig.update_layout(margin=Chart.MARGIN)
        fig.update_layout(legend=dict(
            x=0.025,
            y=0.975,
            traceorder="normal",
            font=dict(
                family="sans-serif",
                size=12,
                color="black"
            )
        ))
        return Chart.__make_dcc(fig)

    @staticmethod
    def make_line_chart_3d(data: pd.DataFrame, x_key: str, y_key: str, z_key: str):
        camera = dict(
            eye=dict(x=1.5, y=2, z=0.1)
        )
        fig = px.line_3d(
            data, x=x_key, y=y_key, z=z_key, title='3D: ' + Chart.make_chart_title(y_key, x_key, z_key)
        )
        fig.update_layout(margin=Chart.MARGIN, scene_camera=camera)
        fig.update_layout(legend=dict(
            x=0.025,
            y=0.975,
            traceorder="normal",
            font=dict(
                family="sans-serif",
                size=12,
                color="black"
            )
        ))
        return Chart.__make_dcc(fig)

    @staticmethod
    def make_scatter_chart_2d(data: pd.DataFrame, x_key: str, y_keys: list[str]):
        fig = px.scatter(
            data, x=x_key, y=y_keys, title=Chart.make_chart_title(','.join(y_keys), x_key),
        )
        fig.update_layout(margin=Chart.MARGIN)
        fig.update_layout(legend=dict(
            x=0.025,
            y=0.975,
            traceorder="normal",
            font=dict(
                family="sans-serif",
                size=12,
                color="black"
            )
        ))
        return Chart.__make_dcc(fig)

    @staticmethod
    def make_scatter_chart_3d(data: pd.DataFrame, x_key: str, y_key: str, z_key: str):
        camera = dict(
            eye=dict(x=1.5, y=2, z=0.1)
        )
        fig = px.scatter_3d(
            data, x=x_key, y=y_key, z=z_key, title='3D: {}'.format(Chart.make_chart_title(y_key, x_key, z_key))
        )
        fig.update_layout(margin=Chart.MARGIN, scene_camera=camera)
        fig.update_layout(legend=dict(
            x=0.025,
            y=0.975,
            traceorder="normal",
            font=dict(
                family="sans-serif",
                size=12,
                color="black"
            )
        ))
        return Chart.__make_dcc(fig)

    @staticmethod
    def make_bar_polar_chart(data: pd.DataFrame, r: str | list[str], theta: str):
        fig = px.bar_polar(
            data, r, theta, title='Polar: r: {} - theta: {}'.format(r, theta),
        )
        fig.update_layout(margin=Chart.MARGIN)
        fig.update_layout(legend=dict(
            x=0.025,
            y=0.975,
            traceorder="normal",
            font=dict(
                family="sans-serif",
                size=12,
                color="black"
            )
        ))
        return Chart.__make_dcc(fig)

    @staticmethod
    def make_scatter_polar_chart(data: pd.DataFrame, r: str | list[str], theta: str):
        fig = px.scatter_polar(
            data, r, theta, title='Polar: r: {} - theta: {}'.format(r, theta),
        )
        fig.update_layout(margin=Chart.MARGIN)
        fig.update_layout(legend=dict(
            x=0.025,
            y=0.975,
            traceorder="normal",
            font=dict(
                family="sans-serif",
                size=12,
                color="black"
            )
        ))
        return Chart.__make_dcc(fig)

    @staticmethod
    def make_mesh_render():
        data_src = vtkRTAnalyticSource()
        data_src.Update()
        dataset = data_src.GetOutput()
        mesh_state = to_mesh_state(dataset)

        content = vtk.View([
            vtk.GeometryRepresentation([
                vtk.Mesh(state=mesh_state)
            ])
        ])

        return content

    @staticmethod
    def make_image_area(img: np.ndarray):
        fig = px.imshow(img)
        fig.update_layout(margin=Chart.MARGIN)
        return Chart.__make_dcc(fig)

    @staticmethod
    def __make_dcc(fig):
        return dcc.Graph(
            figure=fig,
            config={
                'displayModeBar': False
            }
        )

    @staticmethod
    def dict_info(*, x=None, y=None, z=None, r=None, theta=None, style=None, model=None, plot_type=None, **kwargs):
        d = dict(
            x=x,
            y=y,
            z=z,
            r=r,
            theta=theta,
            style=style,
            model=model,
            plot_type=plot_type,
            **kwargs
        )
        return d
