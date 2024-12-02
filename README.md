# Simulation Monitor Rescale App

Simulation Monitor is an example of a Secondary Rescale App – a web application
that augments the main simulation. The job (cluster) lifecycle is defined by the
main simulation process. A Secondary App starts in the background and can be
used to interact with the simulation process and its outputs. Example
applications include simulation progress monitoring, intermediate results
visualization or on-demand check-pointing.

## How it works

The details of the technology are provided in the [Hello World Rescale
App](https://github.com/rescale-labs/App_HelloWorld_Flask/) repository. The only
difference here stems from the fact that the App is a secondary process that
should be started, independently of the main simulation, in the background. This
is achieved by starting the web server as a
[daemon](https://en.wikipedia.org/wiki/Daemon_(computing)). See the last line in
[spub_launch.sh](spub/spub_launch.sh-templ)

```
gunicorn --daemon --certfile $CERT --keyfile $CKEY -b 0.0.0.0:8888 app:server
```

The CFX monitoring module uses the `cfx5mondata` utility to extract data from
the `mon` file. Data is then visualized in a web browser by a web application
developed using the [Dash](https://dash.plotly.com/) web framework.

## Deployment

For the best user experience, publish the Simulation Monitor Rescale App using
[Software
Publisher](https://rescale.com/documentation/main/platform-guides/bring-your-own-software-with-rescale-software-publisher/).
The procedure is identical to what was described for the [Hello World Rescale
App](https://github.com/rescale-labs/App_HelloWorld_Flask/tree/main#publishing-a-rescale-app-using-the-rescale-software-publisher).
See the [build.sh](spub/build.sh) for automated steps.

## Usage

Rescale Apps rely on the `jupyter4all` flag. Make sure this flag is enabled for
your organization or specific Workspaces into which the App was deployed.

When specifying a Job, the Simulation Monitor application needs to be attached
as the first tile (software commands are executed left to right). The
application to be monitored is attached as the following tile and requires a
valid command. The command executed in the context of the Simulation Monitor
will return immediately (start as a daemon) and the main simulation command will
be executed.

Once the cluster is started, navigate to the Job Detail page, click on the
Status page and look for a Notebook URL in the Logs section. Open the URL in a
new tab and start interacting with the web application.

![](README.images/app_simulation_monitor.gif)

For the CFX monitoring specifically, the user may need to wait until the
simulation properly starts. The CFX module will inform the user when the `mon`
file is not yet available and when the `mon` file does not yet contain usable
progress information.

## Introduction to the Dash framework and development of custom monitors

First step to local development is to clone the repository

```
$ git clone https://github.com/rescale-labs/App_Simulation_Monitor.git
```

Start with setting up a virtual environment and installing all the dependencies.

```
$ cd App_Simulation_Monitor/
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

To simplify local development, the code uses `utils.py#is_debug()` function to
switch between _local_ and _cluster_ contexts.

To run locally from the command line, execute the following.

```
$ DEBUG=true python app.py
```

Using an IDE provides better debugger experience. To run the application from
VSCode with debugging:

* Open `app.py` and hit F5, 

The first operation the code dows is to find applicable plugin. This is done by
the `app.py#find_layout()` function.

In the _cluster_ context (debug not set) it will load all modules matching the
`plugins/*_plugin.py` pattern and call `is_applicable()` for each module. The
first module that returns `true` will be asked to provide the webapp layout (by
responding to `get_layout()` function call).

In the _local_ context, a developer can hardwire the plugin to be used. The
`is_applicable()` function in the _local_ context will usually return `true`
unless there is a need to test some complex logic of this function. For example,
to force loading of the Fluent module: 

```
from plugins.fluent_plugin import get_layout, is_applicable

if is_applicable():
    layout = get_layout()
```

In the _cluster_ context, the `is_applicable()` function will determine whether
Simulation Monitor is attached to a supported analysis, currently this is
determined by the existence of analysis specific environmental variables (see
fluent_plugin.py#is_applicable()).

In the _local_ context, we need to provide samples of output files to test.
These are included in the `test/` directory. Remember to test for corner cases
like: output file does not exist yet, output file does not contain simulation
data yet.

Currently, by convention we look for the local test files by detecting the
_local_ context. For example the `fluent_utils.py#get_df()` will eater look for
files in the cluster filesystem, or load file from the local `test/` directory.

To add new plugin, a new `*_plugin.py` module needs to be developed and stored
in the `plugins/` directory. The plugin needs to provide two functions:

* `is_applicable()` - which checks whether a plugin is applicable in the Job context
* `get_layout()` - which returns a [Dash](https://dash.plotly.com/) layout
  component (our examples use [Dash Bootstrap
  Components](https://dash-bootstrap-components.opensource.faculty.ai/))

Most of the webapp generation is abstracted away in generic XY layout (see
[`xy_layout.py`](plugins/xy_layout.py) and
[`xy_utils.py`](plugins/xy_utils.py)). The main work is to write code that will
find a file to parse and write a parser that will output a
[DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)
with columns that can be selected as X,Y axes (see
[`fluent_utils.py`](plugins/fluent_utils.py)).

Some tools will require calling an external command to generate parsable status
files (see CFX plugin).

The above description applies to plugins using the generic `xy_layout.py`
implementation. CFX plugin is a custom implementation, which uses similar
techniques.

## What next?

Contribute! The modular design of the Simulation Monitoring application allows
for independent plug-in development. If the solver you're using is currently
unsupported, and you know how to extract progress data (either via a tool or by
parsing output files) – copy one of the sample modules and tune it to your
needs. Get in touch with us at support@rescale.com to become a contributor.

## About authors and Rescale

[Rescale™](https://rescale.com) is a technology company that builds cloud
software and services that enable organizations of every size to deliver
engineering and scientific breakthroughs that enrich humanity.

[Robert Bitsche](https://www.linkedin.com/in/robertbitsche/) is a Senior
Customer Success Engineer at Rescale with a background in mechanical
engineering, numerical simulation, and renewable energy. Robert believes that
engineering can create a better world. He also believes that the function of an
expert is not to be more right than other people, but to be wrong for more
sophisticated reasons.

[Bartek Dobrzelecki](https://linkedin.com/in/bardobrze) is a Senior Customer
Success Engineer at Rescale with a background in High Performance Computing and
Software Engineering. He is always keen to share his knowledge, demystify
technology and democratize computational thinking. He strongly believes that no
technology should be indistinguishable from magic.

[Sushanth Madabushi
Venugopal](https://www.linkedin.com/in/sushanth-madabushi-venugopal-aaab9485/)
is a Customer Success Engineer at Rescale with a background in Aerospace
Engineering , Numerical Methods and HPC. Sushanth is passionate about harnessing
cloud technology to transform engineering workflows, enabling accelerated
innovation across industries. He believes that true expertise lies in distilling
complexity, ensuring that technology empowers rather than mystifies.