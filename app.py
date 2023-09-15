import glob
import importlib
import logging
import os

import dash
import dash_bootstrap_components as dbc
from flask_restful import Api, Resource

import notfound_plugin

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(name)s %(levelname)s: %(message)s"
)

APP_ID = "com_rescale_simulation_monitor"

PREFIX = f"/notebooks/{os.getenv('RESCALE_CLUSTER_ID')}/"


def init_layout():
    layout = None
    for file in glob.glob("plugins/*_plugin.py"):
        module_name = file[8:-3]
        module = importlib.import_module(f"plugins.{module_name}")
        if module.is_applicable():
            layout = module.get_layout()

    return layout if layout != None else notfound_plugin.get_layout()


# We need to suppress exceptions as some components are created dynamically
# within callbacks
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    routes_pathname_prefix=PREFIX,
    requests_pathname_prefix=PREFIX,
    suppress_callback_exceptions=True,
)


app.layout = init_layout()
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
    app.run_server(debug=False)
