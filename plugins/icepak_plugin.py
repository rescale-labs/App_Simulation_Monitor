import os
import logging

import plugins.xy_layout as xyl
from plugins.icepak_utils import get_df
from utils import is_debug

logger = logging.getLogger(__name__)

def is_applicable():
    if is_debug():
        return True
    else:
        icepak_aedt_version = os.getenv("ANSYS_HFSS_VERSION", None)
        logger.debug(f"ANSYS ICEPAK AEDT version: {icepak_aedt_version}")
        return True if icepak_aedt_version else False

def get_layout():
    return xyl.get_layout(get_df, "ANSYS Icepak AEDT")