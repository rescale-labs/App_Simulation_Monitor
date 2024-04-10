import logging
import os

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html

from utils import is_debug

logger = logging.getLogger(__name__)


def is_applicable():
    """
    All plugins need to implement this function. The applicability logic can be
    based on input files, analysis command, job definition, etc.

    Simplictic implementation relies on existence of a specific exacutable
    call in the process_output.log

    :returns True if monitoring is applicable, False otherwise
    """

    if is_debug():
        return True
    else:
        mech_version = os.getenv("ANSYSMECH_VERSION", None)
        logger.debug(f"ANSYS Mech version: {mech_version}")
        return True if mech_version else False

        
def get_layout():
    """
    All plugins need to implement this function. It builds up the web
    application layout and associated callbacks.

    :returns root component of a Dash layout
    """

    layout = dbc.Container(
        [
            html.Div(
                "Rescale ANSYS Mechanical Simulation Monitor",
                className="text-primary fs-3",
            ),
            html.P(
                "This web app can be used to monitor ANSYS Mechanical jobs running on Rescale in real time.",
            ),
            dbc.Button("Find gst-files", id="button-find-gst", style={"marginTop": 12}),
            html.Div(
                id="gstfile-div",
                style={"marginTop": 12},
            ),
            html.Div(id="graph-div"),
        ]
    )
    return layout
"""
    @callback(
        Output("gstfile-div", "children"),
        Input("button-find-gst", "n_clicks"),
    )
"""