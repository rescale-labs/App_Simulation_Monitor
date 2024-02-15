import glob
import importlib
import logging
import os
import sys
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
from flask_restful import Api, Resource

import notfound_plugin
from utils import is_debug

APP_ID = "rescale_simmon"
LOCAL_CLUSTER_ID = "local"

CLUSTER_ID = os.getenv("RESCALE_CLUSTER_ID", LOCAL_CLUSTER_ID)
PREFIX = f"/notebooks/{CLUSTER_ID}/"

logger = logging.getLogger(__name__)
logging.basicConfig(filename=f"/tmp/{APP_ID}.log", filemode="w", level=logging.DEBUG)


def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical(
        "Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback)
    )


sys.excepthook = handle_unhandled_exception


def find_layout():
    """
    Function goes through all Python modules with _layout postfix stored in the
    plugins directory and returns layout of the last applicable module.

    :returns Dash root component for applicable module or a module not found
             component
    """
    layout = None

    if not is_debug():
        for file in glob.glob("plugins/*_plugin.py"):
            module_name = file[8:-3]
            module = importlib.import_module(f"plugins.{module_name}")

            if module.is_applicable():
                layout = module.get_layout()
                logger.debug(f"Module {module}: applicable")
            else:
                logger.debug(f"Module {module}: not applicable")
    else:
        logger.debug("Running with debugger attached.")

        # Import the plugin you want to test when developing locally
        from plugins.starccm_plugin import get_layout, is_applicable

        if is_applicable():
            layout = get_layout()

    return layout if layout != None else notfound_plugin.get_layout()


# We need to suppress callback exceptions as some components are created
# conditionally within callbacks.
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    routes_pathname_prefix=PREFIX,
    requests_pathname_prefix=PREFIX,
    suppress_callback_exceptions=True,
)


app.layout = find_layout()
server = app.server


# Resale App discovery endpoint
class RescaleAppDiscovery(Resource):
    def get(self):
        return {
            "name": "Simulation Monitor",
            "description": "Simulation progress monitoring tool. The following analyses are supported: ANSYS CFX.",
            "helpUrl": "https://github.com/rescale-labs/App_Simulation_Monitor",
            "icon": app.get_asset_url("app_icon.png"),
            "supportEmail": "support@rescale.com",
            "webappUrl": PREFIX,
            "isActive": True,
        }


api = Api(server)
api.add_resource(RescaleAppDiscovery, f"{PREFIX}/.rescale-app")

if __name__ == "__main__":
    app.run_server(debug=True)
