import glob
from pathlib import Path
from utils import is_debug


def find_gst_file():
    """
    Find the uncleaned GST file produced by non-linear simulation
    """
    if not is_debug():
        gst_file_pattern = "**/*.gst"
        gst_file = glob.glob(
                             gst_file_pattern, 
                             recursive=True,
                             root_dir=Path.home()
                             )
        return gst_file
    else:
        return "tests/mech_out.gst"