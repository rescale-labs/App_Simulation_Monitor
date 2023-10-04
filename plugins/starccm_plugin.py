import logging
import os

import plugins.xy_layout as xyl
from plugins.starccm_utils import get_df
from utils import is_debug

logger = logging.getLogger(__name__)


def is_applicable():
    if is_debug():
        return True
    else:
        starccm_version = os.getenv("STARCCM_VERSION", None)
        logger.debug(f"Star-CCM+ version: {starccm_version}")
        return True if starccm_version else False


def get_layout():
    return xyl.get_layout(get_df, "Star-CCM+")
