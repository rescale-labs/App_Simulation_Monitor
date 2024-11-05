import logging

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, ctx, dcc, html

from plugins.xy_utils import create_plot, get_columns

logger = logging.getLogger(__name__)


HIDDEN = {"display": "none"}
VISIBLE = {"display": "block"}


def get_axes_selector_children(columns):
    return [
        dcc.Dropdown(
            id="x-axis-selector",
            options=[{"label": col, "value": col} for col in columns],
            value=None,
            multi=False,
            placeholder="Select X-Axis",
            style={"width": "400px"},
        ),
        dcc.Dropdown(
            id="y-axis-selector",
            options=[{"label": col, "value": col} for col in columns],
            value=[],
            multi=True,
            placeholder="Select Y-Axis",
            style={"width": "800px"},
        ),
        html.Div(
            [
                dbc.Button(
                    "Plot",
                    id="add-plot-button",
                    n_clicks=0,
                    style={"marginRight": 6},
                ),
                dbc.Button(
                    "Clear All",
                    id="clear-plots-button",
                    n_clicks=0,
                    style={"marginRight": 6},
                ),
                dbc.Button(
                    "Refresh Data",
                    id="refresh-button",
                    n_clicks=0,
                    style={"marginRight": 6},
                ),
            ],
            style={"marginTop": 12},
        ),
    ]


def get_empty_axes_selector_children():
    return [
        "No values reported.",
        html.Br(),
        "Simulation is probably still to reach the first timestep.",
        html.Br(),
        "Try again in a few minutes...",
        html.Br(),
        dbc.Button(
            "Reload",
            id="reload-button",
            style={"marginTop": 12},
        ),
    ]


def get_layout(get_df, analysis_name):
    columns = get_columns(get_df())
    if columns:
        axes_selector = html.Div(
            get_axes_selector_children(columns),
            id="axes-selectors-div",
            style={"marginTop": 12},
        )
    else:
        axes_selector = html.Div(
            get_empty_axes_selector_children(),
            id="axes-selectors-div",
            style={"background": "yellow", "marginTop": 12},
        )

    layout = dbc.Container(
        [
            html.Div(
                f"Rescale {analysis_name} Simulation Monitor",
                className="text-primary fs-3",
            ),
            html.P(
                f"This web app can be used to monitor {analysis_name} jobs running on Rescale in real time.",
            ),
            axes_selector,
            html.Div(
                id="interactive-plot-div",
                style={"marginTop": 12},
            ),
            dcc.Checklist(
                id="x-scale-switch",
                options=[{"label": "X-Log", "value": "log"}],
                value=[],
                labelStyle={"display": "inline-block"},
                style=HIDDEN,
            ),
            dcc.Checklist(
                id="y-scale-switch",
                options=[{"label": "Y-Log", "value": "log"}],
                value=[],
                labelStyle={"display": "inline-block"},
                style=HIDDEN,
            ),
        ]
    )

    @callback(
        [
            Output("interactive-plot-div", "children"),
            Output("x-axis-selector", "value"),
            Output("y-axis-selector", "value"),
            Output("x-scale-switch", "value"),
            Output("y-scale-switch", "value"),
            Output("x-scale-switch", "style"),
            Output("y-scale-switch", "style"),
        ],
        Input("add-plot-button", "n_clicks"),
        Input("clear-plots-button", "n_clicks"),
        Input("refresh-button", "n_clicks"),
        Input("x-scale-switch", "value"),
        Input("y-scale-switch", "value"),
        State("x-axis-selector", "value"),
        State("y-axis-selector", "value"),
        prevent_initial_call=True,
    )
    def update_plot(
        plot_button_clicks,
        clear_button_clicks,
        refresh_button_clicks,
        x_scale_switch,
        y_scale_switch,
        x_axis_value,
        y_axis_values,
    ):
        button_id = ctx.triggered_id
        logger.debug(f"Triggered: {button_id}")

        if "log" in x_scale_switch:
            x_scale = "log"
        else:
            x_scale = "linear"

        if "log" in y_scale_switch:
            y_scale = "log"
        else:
            y_scale = "linear"

        if button_id == "clear-plots-button":
            return "", None, [], [], [], HIDDEN, HIDDEN

        elif x_axis_value is None or not y_axis_values:
            return (
                html.P(
                    "Select X, Y axes.",
                    style={"background": "yellow"},
                ),
                x_axis_value,
                y_axis_values,
                x_scale_switch,
                y_scale_switch,
                VISIBLE,
                VISIBLE,
            )
        else:
            return (
                dcc.Graph(
                    figure=create_plot(
                        get_df(), x_axis_value, y_axis_values, x_scale, y_scale
                    )
                ),
                x_axis_value,
                y_axis_values,
                x_scale_switch,
                y_scale_switch,
                VISIBLE,
                VISIBLE,
            )

    @callback(
        Output("axes-selectors-div", "children"),
        Output("axes-selectors-div", "style"),
        Input("reload-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def reload_plot(
        reload_button_clicks,
    ):
        logger.debug("Reload requested")
        columns = get_columns(get_df())
        if columns:
            return get_axes_selector_children(columns), {"marginTop": 12}
        else:
            return get_empty_axes_selector_children(), {
                "background": "yellow",
                "marginTop": 12,
            }

    return layout
