# Overview
This is the replication package associated to the paper titled: "Evaluation of MQTT Bridge Architectures in a Cross-Organizational Context" submitted to the [22nd IEEE International Conference on Software Architecture (ICSA 2025)](https://conf.researchr.org/home/icsa-2025]).

This repository contains both configuration files and logs recorded during the execution of the benchmark in 2 (virtual) host machines provissioned in a public and private cloud. The associated files are in the config and logs sub directories of the different software components part of the benchmark setup:
- IoT Gateways (MQTT Publish Clients): mqtt_clients docker container image used in docker compose file ```docker-compose-clients.yml```
- Subscriber (MQTT Subscribe Client)
- Bridge Processing Component (MQTT Bridge between a source and destination broker): ```data_transformer``` docker container image used in ```docker-compose-aut1.yml``` and ```docker-compose-aut2.yml```.

In this study we benchmark latency and relibility of two different Architectural Under Test deployment option for MQTT bridge components implemented on client side.

## Outline
This replication package contains the following content:
<pre><font color="#3465A4"><b>.</b></font>
├── <font color="#3465A4"><b>data_analysis</b> - Jupyter notebook and python scripts to reproduce result in Table IV and Figures 4-8.</font>
├── <font color="#3465A4"><b>monitoring</b></font>
│   ├── <font color="#3465A4"><b>configs</b></font>
│   │   └── <font color="#3465A4"><b>provisioning</b></font>
│   │       └── <font color="#3465A4"><b>datasources</b></font>
│   ├── <font color="#3465A4"><b>hivemq-file-rbac-extension</b></font>
│   │   ├── <font color="#3465A4"><b>conf</b></font>
│   │   └── <font color="#3465A4"><b>credentials-archive</b></font>
│   ├── <font color="#3465A4"><b>hivemq-prometheus-extension</b></font>
│   └── <span style="background-color:#4E9A06"><font color="#3465A4">prometheus_data</font></span>
├── <font color="#3465A4"><b>publisher</b></font>
│   ├── <font color="#3465A4"><b>configs</b></font>
│   ├── <font color="#3465A4"><b>data</b></font>
│   │   ├── <font color="#3465A4"><b>provider1</b></font>
│   │   │   ├── <font color="#3465A4"><b>gateway1</b></font>
│   │   │   └── <font color="#3465A4"><b>gateway2</b></font>
│   │   └── <font color="#3465A4"><b>provider2</b></font>
│   │       └── <font color="#3465A4"><b>gateway1</b></font>
│   └── <span style="background-color:#4E9A06"><font color="#3465A4">logs</font></span>
│       ├── <font color="#3465A4"><b>aut1</b></font>
│       │   ├── <font color="#3465A4"><b>qos0</b></font>
│       │   ├── <font color="#3465A4"><b>qos1</b></font>
│       │   └── <font color="#3465A4"><b>qos2</b></font>
│       ├── <font color="#3465A4"><b>aut2</b></font>
│       │   ├── <font color="#3465A4"><b>qos0</b></font>
│       │   ├── <font color="#3465A4"><b>qos1</b></font>
│       │   └── <font color="#3465A4"><b>qos2</b></font>
│       └── <font color="#3465A4"><b>aut3</b></font>
│           ├── <font color="#3465A4"><b>qos0</b></font>
│           ├── <font color="#3465A4"><b>qos1</b></font>
│           └── <font color="#3465A4"><b>qos2</b></font>
├── <font color="#3465A4"><b>results</b></font>
│   └── <font color="#3465A4"><b>Prometheus</b></font>
├── <font color="#3465A4"><b>subscriber</b></font>
│   ├── <font color="#3465A4"><b>configs</b></font>
│   └── <span style="background-color:#4E9A06"><font color="#3465A4">logs</font></span>
│       ├── <font color="#3465A4"><b>aut1</b></font>
│       │   ├── <font color="#3465A4"><b>qos0</b></font>
│       │   ├── <font color="#3465A4"><b>qos1</b></font>
│       │   └── <font color="#3465A4"><b>qos2</b></font>
│       ├── <span style="background-color:#4E9A06"><font color="#3465A4">aut2</font></span>
│       │   ├── <font color="#3465A4"><b>qos0</b></font>
│       │   ├── <font color="#3465A4"><b>qos1</b></font>
│       │   └── <font color="#3465A4"><b>qos2</b></font>
│       └── <font color="#3465A4"><b>aut3</b></font>
│           ├── <font color="#3465A4"><b>qos0</b></font>
│           ├── <font color="#3465A4"><b>qos1</b></font>
│           └── <font color="#3465A4"><b>qos2</b></font>
└── <font color="#3465A4"><b>transformer</b></font>
    ├── <font color="#3465A4"><b>configs</b></font>
    └── <span style="background-color:#4E9A06"><font color="#3465A4">logs</font></span>
        ├── <span style="background-color:#4E9A06"><font color="#3465A4">aut1</font></span>
        │   ├── <font color="#3465A4"><b>qos0</b></font>
        │   │   └── <span style="background-color:#4E9A06"><font color="#3465A4">prometheus_data</font></span>
        │   ├── <font color="#3465A4"><b>qos1</b></font>
        │   │   └── <span style="background-color:#4E9A06"><font color="#3465A4">prometheus_data</font></span>
        │   └── <span style="background-color:#4E9A06"><font color="#3465A4">qos2</font></span>
        │       ├── <font color="#3465A4"><b>figures</b></font>
        │       └── <span style="background-color:#4E9A06"><font color="#3465A4">prometheus_data</font></span>
        ├── <font color="#3465A4"><b>aut2</b></font>
        │   ├── <font color="#3465A4"><b>qos0</b></font>
        │   │   └── <span style="background-color:#4E9A06"><font color="#3465A4">prometheus_data</font></span>
        │   ├── <font color="#3465A4"><b>qos1</b></font>
        │   │   └── <span style="background-color:#4E9A06"><font color="#3465A4">prometheus_data</font></span>
        │   └── <font color="#3465A4"><b>qos2</b></font>
        │       └── <span style="background-color:#4E9A06"><font color="#3465A4">prometheus_data</font></span>
        └── <font color="#3465A4"><b>aut3</b></font>
            ├── <font color="#3465A4"><b>qos0</b></font>
            ├── <font color="#3465A4"><b>qos1</b></font>
            └── <font color="#3465A4"><b>qos2</b></font>

70 directories
</pre>


# MQTT Benchmark
Collection of scripts to automate MQTT platform benchmark.
Also collects data from experiments execution.

## Dependencies
**Running the experiments:**
- Docker container runtime engine (system docker containers needs to be requested)
- Python 3
- Any Jupyter Notebook editor (e.g. Jupiter Lab) -- for reproducing aggreated results

## Results
The results can be found in the resutls folder. Replication of the results can be obtained by running the data_analysis Jupiter Notebook in the data analysis folder. **Note that the full/absolute path to the logs in this replication package needs to be set there manually.**

## Replication of Prometheus data
Data stored in prometheus from the experiments can be visualized in the GUI at localhost:9090 after mounting the different experiment records folder as a read and write volume when running Prometheus docker container.
```
docker run -p 9090:9090  -v PATH-TO-REPLICATION-PACKAGE/transformer/logs/aut3/qos1/prometheus_data:/prometheus prom/prometheus
```

## Replication Instructions

### Execution Steps

1. Generate HiveMQ credentials files for the ingestion broker (trust boundary)
2. Define QoS benchmark parameter for clients and brokers (can be done using env variables)
2. Run monitoring sub-system (docker compose)
3. Run ingestion broker for each sensor data provider (source brokers)
2. Run AUT option (docker compose) including the generated credentials file
2. Run Clients launcher script (python)
   3. Takes the generated password as an argument for the MQTT clients launched
4. Run Load using the python script: ```run_load.py```
   
## Benchmark setup
There are different docker compose files for each one of the components used in the benchmark (described in section 3).
The load is run concurrently with the help of the python script: run_load.py
The subscriber is run manually running the associated docker image.
