import logging
import os

import plugins.xy_layout as xyl
from plugins.fluent_utils import get_df
from utils import is_debug

logger = logging.getLogger(__name__)


def is_applicable():
    if is_debug():
        return True
    else:
        fluent_version = os.getenv("ANSYSFLUENT_VERSION", None)
        logger.debug(f"ANSYS Fluent version: {fluent_version}")
        return True if fluent_version else False


def get_layout():
    return xyl.get_layout(get_df, "ANSYS Fluent")
