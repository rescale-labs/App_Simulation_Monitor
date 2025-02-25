import os
import re
import logging

import pandas as pd

from utils import is_debug  # Assuming is_debug is an external utility you might use


def process_aedt_and_monitor_data(working_dir):
    """
    Combines the steps of:
    1. Finding the .aedt file,
    2. Extracting monitor data from the .aedt file,
    3. Finding matching .sd files,
    4. Mapping monitor data to .sd files.

    Returns:
        tuple:
            - Path to the .aedt file
            - Path to the .aedt results monitor files directory
            - Dictionary of extracted monitor points with their IDs
            - Dictionary mapping monitor points to matching .sd file paths
    """

    # Step 1: Find the .aedt file within the working directory
    aedtfile_path = next((os.path.join(working_dir, f) for f in os.listdir(working_dir) if f.endswith(".aedt")), None)

    # If no .aedt file is found, raise an error
    if not aedtfile_path:
        raise FileNotFoundError("No .aedt file found in the current directory.")

    # Extract the file name without extension
    aedtfile_name = os.path.splitext(os.path.basename(aedtfile_path))[0]

    # Set path to the corresponding monitor files directory
    path_monfiles = os.path.join(working_dir, f"{aedtfile_name}.aedtresults", "IcepakDesign1.results")

    # Step 2: Extract monitor data from the .aedt file
    with open(aedtfile_path, 'r', encoding='latin1') as file:
        data = file.read()

    # Regular expression to capture the monitor block and its contents
    monitor_match = re.search(
        r"\$begin 'Monitor'\s*\$begin 'IcepakMonitors'(.*?)\$end 'IcepakMonitors'\s*\$end 'Monitor'", data, re.DOTALL)

    # Raise error if the monitor block is not found
    if not monitor_match:
        raise ValueError("Monitor block or IcepakMonitors block not found in the file.")

    # Extract monitor points and their corresponding IDs from the monitor block
    monitor_items = {block.group(1): int(re.search(r"ID=(\d+)", block.group(2)).group(1))
                     for block in re.finditer(r"\$begin '(.*?)'(.*?)\$end '\1'", monitor_match.group(1), re.DOTALL)}

    # Add "Residual" entry to the monitor items dictionary
    monitor_items = {"Residual": 0, **monitor_items}

    # Step 3: Find matching .sd files in the specified directory
    if not os.path.exists(path_monfiles):
        raise FileNotFoundError(f"The specified path does not exist: {path_monfiles}")

    # List all the .sd files that match the required pattern
    list_monfiles = [os.path.join(path_monfiles, f) for f in os.listdir(path_monfiles)
                     if re.match(r"DV\d+_S\d+_MON\d+_V\d+\.sd", f)]

    if not list_monfiles:
        raise FileNotFoundError(
            "No matching .sd files found. Pre-processing is in progress, Please try again after 30 mins.")

    # Step 4: Map monitor points to matching .sd files using a regex pattern
    file_pattern = re.compile(r"DV\d+_S\d+_MON(\d+)_V\d+\.sd")

    # Create a dictionary of monitor points and their matching .sd files
    dict_monfiles = {key: next((file for file in list_monfiles if file_pattern.match(os.path.basename(file)) and
                                int(file_pattern.match(os.path.basename(file)).group(1)) == monitor_items[key]), None)
                     for key in monitor_items}

    return dict_monfiles


def parse_monfile_precise(file_path):
    """
    Parses a MON file with a flexible structure: Iteration followed by variables
    in 'Variable(Value)' format. Variable names are dynamically detected.

    Args:
        file_path (str): Path to the MON file.

    Returns:
        pd.DataFrame: A DataFrame with parsed data.
    """
    # Initialize a dictionary to store all data, including dynamically-detected variables
    data = {"Iteration": []}

    # Open the MON file and parse its content line by line
    with open(file_path, 'r') as file:
        for line in file:
            # Remove leading and trailing whitespaces
            line = line.strip()
            if not line:
                continue  # Skip empty lines

            # Split the line by the first whitespace
            # The first part is Iteration, and the rest contains variables
            parts = line.split(maxsplit=1)
            iteration = float(parts[0])  # Convert Iteration to float
            data["Iteration"].append(iteration)

            # Extract variables from the rest of the line, e.g., "VariableName(Value)"
            if len(parts) > 1:
                rest = parts[1]
                matches = re.findall(r"(\w+)\(([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)\)", rest)

                for var_name, var_value in matches:
                    var_value = float(var_value)  # Convert value to float

                    # Add variable to the dictionary if not already present
                    if var_name not in data:
                        data[var_name] = []

                    # Append the variable's value to its list
                    data[var_name].append(var_value)

            # Handle missing variables by appending None for keys that weren't found in this line
            for key in data:
                if key != "Iteration" and len(data[key]) < len(data["Iteration"]):
                    data[key].append(None)

    # Create a DataFrame from the dictionary
    df = pd.DataFrame(data)

    return df


def make_combined_df(dict_monfiles):
    """
    Combines the monitor data from different .sd files into a single DataFrame based on 'Iteration'.

    Args:
        dict_monfiles (dict): Dictionary of monitor names and corresponding .sd file paths.

    Returns:
        pd.DataFrame: A DataFrame with the combined monitor data.
    """
    df_monfiles_total = None

    # Loop over each monitor file path in the dictionary
    for monitor_name, file_path in dict_monfiles.items():
        if file_path:
            # Parse the MON file into a DataFrame
            df = parse_monfile_precise(file_path)

            # Handle the case where the monitor is "Residual"
            if monitor_name == "Residual":
                df_residual = df.copy()

                if df_monfiles_total is None:
                    df_monfiles_total = df_residual
                else:
                    df_monfiles_total = pd.merge(
                        df_monfiles_total, df_residual, on="Iteration", how="outer"
                    )
            else:
                # For non-residual monitors, rename all columns except "Iteration"
                df_non_residual = df.copy()
                new_column_names = {
                    col: f"{col}-{monitor_name}" for col in df.columns if col != "Iteration"
                }
                df_non_residual.rename(columns=new_column_names, inplace=True)

                # Merge with the existing DataFrame
                if df_monfiles_total is None:
                    df_monfiles_total = df_non_residual
                else:
                    df_monfiles_total = pd.merge(
                        df_monfiles_total, df_non_residual, on="Iteration", how="outer")

    return df_monfiles_total


def get_df():
    
    logging.basicConfig(level=logging.DEBUG)
    
    try:
        if is_debug():
            base_dir = os.getcwd()
            file_dir = os.path.join(base_dir, "tests")
            dict_monfiles = process_aedt_and_monitor_data(file_dir)
        else:
            base_dir = os.path.expanduser("~")
            working_dir = os.path.join(base_dir, "work")
            dict_monfiles = process_aedt_and_monitor_data(working_dir)

        df_monfiles_total = make_combined_df(dict_monfiles)
    except Exception as e:
        logging.debug(e)
        return pd.DataFrame()

    return df_monfiles_total
