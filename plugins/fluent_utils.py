import csv
import io
import os
import re

import pandas as pd

from utils import find_file, is_debug

def parse_file(process_output_file_path):
    FIRST_CHAR_IDX = 23
    out_csv = io.StringIO()
    csv_writer = csv.writer(out_csv)

    header_pattern = r"\s+iter\s+continuity\s+x-velocity\s+y-velocity\s+z-velocity.*"
    transient_header_pattern = r"\s+step\s+flow-time.*"
    values_pattern = r"\s+\d+\s+[\d|.|e|+|-]+\s+.*"

    captured_header = None
    transient = False

    with open(process_output_file_path, "r") as f:
        while l := f.readline():
            # strip timestamps
            line = l[FIRST_CHAR_IDX:]
            if not transient and re.match(transient_header_pattern, line):
                captured_header = line.split()
                out_csv = io.StringIO()
                csv_writer = csv.writer(out_csv)
                csv_writer.writerow(captured_header)
                transient = True
            elif re.match(header_pattern, line) and not captured_header:
                captured_header = line.split()
                csv_writer.writerow(captured_header)
            elif re.match(values_pattern, line):
                val_row = line.split() if transient else line.split()[:-1]
                if len(val_row) == len(captured_header):
                    csv_writer.writerow(val_row)
            else:
                pass
    
    try:
        df = pd.read_csv(io.StringIO(out_csv.getvalue()))
        if transient:
            return df.drop_duplicates(subset=["step"])
        return df.drop_duplicates(subset=["iter"]).reset_index(drop=True)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def get_df():
    if is_debug():
        file = find_file("**/fluent_process_output.dat", "..")
        # file = find_file("**/fluent_process_output_no_values.dat", "..")
        file = find_file("**/fluent_process_output_transient.log","..")
    else:
        home_dir = os.path.expanduser("~")
        file = find_file("**/process_output.log", home_dir)

    df = parse_file(file)
    return df

if __name__ == "__main__":
    fname = r'C:\Users\ctusa\Downloads\process_output_sAvumg.log'
    print(fname)
    df = parse_file(fname)
    print(df)