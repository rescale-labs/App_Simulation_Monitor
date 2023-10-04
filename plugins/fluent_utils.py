import csv
import io
import os
import re

import pandas as pd

from utils import find_file, is_debug


def get_column_ranges(value_row):
    column_ranges = []

    in_value = False
    start_idx = 0
    current_idx = 0

    for c in value_row:
        if not in_value and c == " ":
            pass
        elif not in_value and c != " ":
            in_value = True
        elif in_value and (c == " " or c == "\n"):
            column_ranges.append((start_idx, current_idx))
            start_idx = current_idx + 1
            in_value = False
        elif c == ":":
            # we want to discard the last "0:01:34  499" or the "time/iter" column
            break

        current_idx += 1

    return column_ranges


def convert_to_list(line, column_ranges):
    row = []
    for s, e in column_ranges:
        row.append(line[s : e + 1].strip())
    return row


def parse_file(process_output_file_path):
    FIRST_CHAR_IDX = 23
    out_csv = io.StringIO()
    csv_writer = csv.writer(out_csv)

    header_pattern = r"\s+iter\s+continuity\s+x-velocity\s+y-velocity\s+z-velocity.*"
    values_pattern = f"\s+\d+\s+[\d|.|e|+|-]+\s+[\d|.|e|+|-]+\s+[\d|.|e|+|-]+\s+.*"

    captured_header = None
    column_ranges = None

    with open(process_output_file_path, "r") as f:
        while l := f.readline():
            # strip timestamps
            line = l[FIRST_CHAR_IDX:]
            if re.match(header_pattern, line) and not captured_header:
                captured_header = line
            elif re.match(values_pattern, line):
                if not column_ranges:
                    column_ranges = get_column_ranges(line)
                    csv_writer.writerow(convert_to_list(captured_header, column_ranges))
                csv_writer.writerow(convert_to_list(line, column_ranges))
            else:
                pass

    try:
        return pd.read_csv(io.StringIO(out_csv.getvalue()))
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def get_df():
    if is_debug():
        # file = find_file("**/fluent_process_output.dat", "..")
        file = find_file("**/fluent_process_output_no_values.dat", "..")
    else:
        home_dir = os.path.expanduser("~")
        file = find_file("**/process_output.log", home_dir)

    df = parse_file(file)
    return df
