from __future__ import print_function
import os
import json
import math

# hard code this to avoid multi-tile PROGRAM_PATH issues
SPX_TILE_PATH = "/program/sxp-interactive"

BASE_JSON = os.path.join(SPX_TILE_PATH, "util/base.json")
PYTHON_INSTALLED = os.path.join(os.getenv("HOME"), ".PYTHON_INSTALLED")
ORIG_ENV_FILE = os.path.join(os.getenv("HOME"), ".ORIG_ENV")
CUR_ENV_FILE = os.path.join(os.getenv("HOME"), ".CUR_ENV")
SHA_SUM_FILE = os.path.join(os.getenv("HOME"), ".FILES_SHA512")
YUM_FILE = os.path.join(os.getenv("HOME"), ".YUM_INSTALLS")
PROPERTY_SEPARATOR = "="

PROGRAM_PATH_FILE = os.path.join(os.getenv("HOME"), ".PROGRAM_PATH")
with open(PROGRAM_PATH_FILE, "r") as f:
    PROGRAM_PATH = f.readline().strip()

PROGRAM_PATH_SIZE_FILE = os.path.join(os.getenv("HOME"), ".PROGRAM_PATH_SIZE")
with open(PROGRAM_PATH_SIZE_FILE, "r") as f:
    PROGRAM_PATH_SIZE = float(f.readline().split()[0])

print("The program path is: ", PROGRAM_PATH)

# vars that may change in the env, but we don't really care, or they change because
# they are not defined when the orig env is extracted in setup_command
EXEMPT_VARS = [
    "SSH_CONNECTION",
    "SSH_CLIENT",
    "SSH_TTY",
    "SHLVL",
    "XDG_SESSION_ID",
    "JAVA_HOME",
    "OLDPWD",
    "PKG_CONFIG_PATH",
    "LS_COLORS",
    "JRE_HOME",
    "RESCALE_IG_RESTART_COUNT",
    "LIB_OPENMPI",
    "BIN_OPENMPI",
    "PWD",
    "XDG_RUNTIME_DIR",
    "INSTANCE_ID",
    "MPIRUN_WRAPPER_DIR",
    "TERM" "USE_MPI",
    "MPI_BUNDLE_LOCATION",
    "MPI_ROOT",
    "PROGRAM_PATH",
    "MPI_FLAVOR",
    "MPI_VERSION",
    "MPI_WRAPPER_LOCATION",
    "USE_MPIVARS_intelmpi2019",
    "RESCALE_THREADS_PER_SLOT",
    "RESCALE_INTERCONNECT",
    "RESCALE_CORES_PER_SLOT",
    "RESCALE_NODES_PER_SLOT",
    "RESCALE_GPUS_PER_SLOT",
    "RESCALE_CORE_TYPE",
    "RESCALE_THREADS_PER_NODE",
    "RESCALE_GPUS_PER_NODE",
    "RESCALE_CLUSTER_ID",
    "RESCALE_CORES_PER_NODE",
    "RESCALE_PROVIDER",
    "RESCALE_PREFERRED_REMSH",
    "RESCALE_SLOTS_PER_NODE",
    "HOSTALIASES",
    "SSH_AGENT_PID",
    "SESSION_MANAGER",
    "WINDOWID",
    "SSH_AUTH_SOCK",
    "DCV_GL_DISPLAY",
    "DCV_VIRTUAL_SESSION",
    "XAUTHORITY",
    "XDG_SESSION_TYPE",
    "DCV_SESSION_ID",
    "DBUS_SESSION_BUS_ADDRESS",
    "TERM",
]


def get_path_changes(old_path, new_path):
    added_paths = []
    old_items = old_path.split(":")
    new_items = new_path.split(":")
    for item in new_items:
        if item not in old_items:
            added_paths.append(item)
    return added_paths


def get_env_vars(fname):
    with open(fname) as f:
        env_lines = f.readlines()
    e_vars = {}
    for line in env_lines:
        var = line.split("=")[0].replace("\n", "")
        val = line.split("=")[-1].replace("\n", "")
        e_vars[var] = val
    return e_vars


# need to add some logic around MPI vars
def get_path_var(added):
    path_array = []
    base_path = PROGRAM_PATH + "/bin"
    path_array.append(base_path)
    path_array.extend(added)
    return ":".join(path_array)


# need to add some logic around MPI vars
def get_ld_path_var(added):
    path_array = []
    base_path = PROGRAM_PATH + "/lib"
    path_array.append(base_path)
    # TODO: make this not hardcoded for intel
    if os.getenv("USE_MPI"):
        path_array.append(
            PROGRAM_PATH + "/intel/impi/" + os.getenv("MPI_VERSION") + "/intel64/lib"
        )
        path_array.append(
            PROGRAM_PATH
            + "/intel/impi/"
            + os.getenv("MPI_VERSION")
            + "/intel64/lib/release"
        )
        path_array.append(
            PROGRAM_PATH
            + "/intel/impi/"
            + os.getenv("MPI_VERSION")
            + "/intel64/libfabric/lib"
        )
    path_array.extend(added)
    return ":".join(path_array)


# assume we have written the user inputs to ~/.ANALYSIS_DESCRIPTION
def read_analysis_description():
    with open(BASE_JSON) as f:
        json_data = json.load(f)

    fpath = os.path.join(os.getenv("HOME"), ".ANALYSIS_DESCRIPTION")
    if os.path.exists(fpath):
        with open(fpath) as f:
            desc = f.readlines()
            # go through and update the fields from the base json with the user input

        # TODO: make this better, less ad hoc
        for line in desc:
            var, *val = line.strip().split(PROPERTY_SEPARATOR)
            val = PROPERTY_SEPARATOR.join(val)

            if var == "code":
                json_data["package"]["name"] = val
                json_data["install"]["name"] = val
                json_data["software"]["code"] = val
            elif var == "name":
                json_data["software"]["name"] = val
            elif var == "png_thumbnail":
                json_data["software"]["pngThumbnail"] = val
            elif var == "version":
                json_data["software"]["versions"][0]["version"] = val
            elif var == "version_code":
                json_data["software"]["versions"][0]["versionCode"] = val
            elif var == "std_cmd":
                json_data["software"]["versions"][0]["stdCommand"] = val
                json_data["software"]["versions"][0]["smpCommand"] = val
                json_data["software"]["versions"][0]["mpiCommand"] = val
            elif var == "mpi_cmd":
                json_data["software"]["versions"][0]["mpiCommand"] = val
            elif var == "gpu_cmd":
                json_data["software"]["versions"][0]["gpuCommand"] = val
            elif var == "description":
                json_data["software"]["description"] = val
            elif var == "setup_command":
                json_data["software"]["versions"][0]["setupCommand"] = val
            elif var == "isInteractive":
                json_data["software"]["isInteractive"] = (
                    True if val == "True" else False
                )
    return json_data

orig_vars = get_env_vars(ORIG_ENV_FILE)
cur_vars = get_env_vars(CUR_ENV_FILE)
env_array = []

for cv in cur_vars.keys():
    if cv in orig_vars.keys():
        if not cur_vars[cv] == orig_vars[cv]:
            # tease out changes to the PATH and LD_LIBRARY_PATH
            if cv == "PATH":
                added = get_path_changes(orig_vars[cv], cur_vars[cv])
                new_path = get_path_var(added)
                env_array.append({"name": "PATH", "value": new_path})
            elif cv == "LD_LIBRARY_PATH":
                added = get_path_changes(orig_vars[cv], cur_vars[cv])
                new_ld_path = get_ld_path_var(added)
                env_array.append({"name": "LD_LIBRARY_PATH", "value": new_ld_path})
            else:
                if cv not in EXEMPT_VARS:
                    env_array.append({"name": cv, "value": cur_vars[cv]})
    else:
        if cv not in EXEMPT_VARS:
            env_array.append({"name": cv, "value": cur_vars[cv]})

# add the mpi vars, should be able to get away with letting the abstraction set MPI_ROOT
if os.getenv("USE_MPI"):
    env_array.append({"name": "MPI_FLAVOR", "value": os.getenv("MPI_FLAVOR")})

# if we installed python
if os.path.exists(PYTHON_INSTALLED):
    activate_env = (
        '"; source ' + PROGRAM_PATH + '/venv/bin/activate; ACTIVATE_USER_ENV="'
    )
    env_array.append({"name": "ACTIVATE_ENV", "value": activate_env})
    print("Adding python env var")
# check if there are variables that reference the user home,
# which won't be available on a new cluster
for env_var in env_array:
    if os.getenv("HOME") in env_var["value"]:
        print("::: WARN: You have an ENV VAR defined that references $HOME: ")
        print("          Name:  " + env_var["name"])
        print("          Value: " + env_var["value"])

# load everything into the json
json_data = read_analysis_description()
json_data["software"]["versions"][0]["env"] = env_array
json_data["software"]["versions"][0]["mountBase"] = PROGRAM_PATH
json_data["install"]["mountPoint"] = PROGRAM_PATH
json_data["install"]["volumeSize"] = math.ceil(PROGRAM_PATH_SIZE / 1e6 * 1.2)

# Assume we have the sha512sums of the files we will want to use for the
if os.path.exists(SHA_SUM_FILE):
    file_sha = []
    with open(SHA_SUM_FILE, "r") as f:
        lines = f.readlines()
        for line in lines:
            file_sha.append({"sha512": line.split()[0], "name": line.split()[1]})
    json_data["install"]["inputFiles"] = file_sha

# pull the yum installs
yum_commands = ["sudo", "yum", "install", "-y"]
pkgs = []
with open(YUM_FILE, "r") as f:
    lines = f.readlines()
    for line in lines:
        for item in line.split()[1:]:
            if item not in yum_commands:
                pkgs.append(item)

unique_pkgs = list(set(pkgs))
if unique_pkgs:
    yum_base = ["yum", "install", "-y"]
    for pkg in unique_pkgs:
        yum_base.append(pkg)
    setup_command = " ".join(yum_base)
    json_data["software"]["versions"][0]["setupCommand"] = setup_command


json_path = os.path.join(os.getenv("HOME"), "work/settings.json")
with open(json_path, "w") as settingsFile:
    json.dump(json_data, settingsFile, indent=4)
