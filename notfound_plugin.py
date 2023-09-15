import dash_bootstrap_components as dbc
from dash import html


def get_layout():
    """
    Returns default layout with information
    """
    return dbc.Container(
        [
            html.Div(
                "Monitoring module not found",
                className="text-primary fs-3",
                style={"margin-bottom": "1em"},
            ),
            html.Div(
                "Supported analyses: ANSYS CFX",
                className="text-info fs-6",
                style={"margin-bottom": "1em"},
            ),
        ],
        fluid=True,
    )
