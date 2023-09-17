import glob
import subprocess
from io import StringIO
from pathlib import Path
import os

import pandas as pd
import plotly.graph_objects as go

from utils import is_debug


def find_mon_files():
    """
    Recursively search all mon-files starting in the user's home directory.
    """

    if not is_debug():
        mon_file_pattern = "**/mon"
        mon_files = glob.glob(mon_file_pattern, recursive=True, root_dir=Path.home())

        mon_files = [os.path.join(Path.home(), f) for f in mon_files]
        return mon_files
    else:
        return [os.path.join(os.getcwd(), "tests/mon")]


def get_csv_data(mon_file, varrule):
    """
    Get the csv data for the relevant variables using the cfx5mondata command.

    :param mon_file: the mon file
    :param varrule: varrule for cfx5mondata
    :returns dataframe or empty dataframe if there are no monitoring values
    """

    if not is_debug():
        command = f'cfx5mondata -mon {mon_file} -varrule "{varrule}"'

        # When mon file exists, but there is no data stdout is empty and stderr
        # says:
        # Exporter error:
        # No monitor values could be read.

        cp = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        csv_data = cp.stdout

        try:
            return pd.read_csv(StringIO(csv_data))
        except pd.errors.EmptyDataError:
            return pd.DataFrame()
    else:
        try:
            # return pd.read_csv("tests/cfx_mon_no_values.dat")
            return pd.read_csv("tests/cfx_mon.dat")
        except pd.errors.EmptyDataError:
            return pd.DataFrame()


def create_plot(mon_file, varrule):
    """
    Find relevant variables, read the csv data and create a new plotly plot.

    :param mon_file: mon file to read
    :param varrule: varrule for cfx5mondata call
    :returns figure or None if dataframe is empty
    """

    df = get_csv_data(mon_file, varrule)
    if df.empty:
        return None

    fig = go.Figure()
    for c in df.columns[1:]:
        fig.add_trace(
            go.Scatter(
                x=df[df.columns[0]], y=df[c], mode="lines+markers", name=df[c].name
            )
        )
    fig.update_layout(title=str(mon_file), showlegend=True, height=600)
    fig.update_xaxes(range=[0.0, None], title=df.columns[0])

    return fig
