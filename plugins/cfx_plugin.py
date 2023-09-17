from shutil import which

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html
from plugins.cfx_utils import create_plot, find_mon_files

from utils import is_debug


def is_applicable():
    """
    All plugins need to implement this function. The applicability logic can be
    based on input files, analysis command, job definition, etc.

    For CFX, a simplistic implementation checks for the existence of the
    cfx5mondata executable.

    :returns True if monitoring is applicable, False otherwise
    """

    if is_debug():
        return True
    else:
        return which("cfx5mondata") is not None


def get_layout():
    """
    All plugins need to implement this function. It builds up the web
    application layout and associated callbacks.

    :returns root component of a Dash layout
    """

    layout = dbc.Container(
        [
            html.Div(
                "Rescale ANSYS CFX Simulation Monitor",
                className="text-primary fs-3",
            ),
            html.P(
                "This web app can be used to monitor ANSYS CFX jobs running on Rescale in real time.",
            ),
            html.Button(
                "Find mon-files", id="button-find-mon", style={"marginTop": 12}
            ),
            html.Div(
                id="monfile-div",
                style={"marginTop": 12},
            ),
            html.Div(id="graph-div"),
        ]
    )

    @callback(
        Output("monfile-div", "children"),
        Input("button-find-mon", "n_clicks"),
    )
    def update_mon_options(n_clicks):
        """
        Populate mon-file dropdown when the user clicks Find mon-files.

        :returns mon-file selection dropdown component and varrule selection
                 components or a component informing the user about mon-files
                 not found.
        """

        mon_files = find_mon_files()
        if not mon_files:
            return html.Div(
                [
                    "No mon files found.",
                    html.Br(),
                    "Simulation is probably still starting.",
                    html.Br(),
                    "Try again in a few minutes...",
                ],
                style={"background": "yellow"},
            )
        else:
            return [
                "Select mon-file",
                dcc.Dropdown(
                    id="mon-dropdown",
                    style={"width": "800px"},
                    options=mon_files,
                    value=mon_files[0] if len(mon_files) == 1 else None,
                ),
                html.Div(
                    [
                        "Varrule to plot",
                        html.Br(),
                        dcc.Input(
                            id="varrule-input",
                            value="CATEGORY = USER POINT",
                            type="text",
                            style={"width": "400px"},
                        ),
                    ],
                    style={"marginTop": 12},
                ),
                html.Button(
                    "Reload",
                    id="button-reload",
                    style={"marginTop": 12},
                ),
            ]

    @callback(
        Output("graph-div", "children"),
        [
            Input("button-reload", "n_clicks"),
            State("mon-dropdown", "value"),
            State("varrule-input", "value"),
        ],
        prevent_initial_call=True,
    )
    def update_graph(n_clicks, mon_file, varrule):
        """
        Update the graph when the user clicks the Reload button.

        :returns a graph of variable values matching varrule or a component
                 informing the user of missing timesteps.
        """

        fig = create_plot(mon_file, varrule)

        if fig:
            return dcc.Graph(figure=fig, id="graph")
        else:
            return html.Div(
                [
                    "No monitor values reported.",
                    html.Br(),
                    "Simulation is probably still to reach the first timestep.",
                    html.Br(),
                    "Try again in a few minutes...",
                ],
                style={"background": "yellow"},
            )

    return layout
