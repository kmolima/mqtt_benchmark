# Overview
This is the replication package associated to the paper titled: "Evaluation of MQTT Bridge Architectures in a Cross-Organizational Context" submitted to the [22nd IEEE International Conference on Software Architecture (ICSA 2025)](https://conf.researchr.org/home/icsa-2025]).

In this study we benchmark latency and relibility of two different Architectural Under Test deployment option for MQTT bridge components implemented on client side.

This repository contains both configuration files and logs recorded during the execution of the benchmark in 2 (virtual) host machines provissioned in a public and private cloud. The associated files are in the config and logs sub directories of the different software components part of the benchmark setup:
- IoT Gateways (MQTT Publish Clients): mqtt_clients docker container image used in docker compose file ```docker-compose-clients.yml```
- Subscriber (MQTT Subscribe Client): mqtt_clients docker container image using the entrypoint ```python3``` and  ```command: ["subscriber.py", "--configfile", "/app/config.yml", "--logfile", "logs/subscriber.log"]```
- Bridge Processing Component (MQTT Bridge between a source and destination broker): ```data_transformer``` docker container image used in ```docker-compose-aut1.yml``` and ```docker-compose-aut2.yml```.
- HiveMQ-CE (Community Edition of HiveMQ MQTT Broker): hivemq-ce [container image](https://hub.docker.com/r/hivemq/hivemq-ce), version 2024.7.
- Monitoring components (Prometheus + Grafana): docker compose file ```docker-compose-monitoring.yml```.

The docker compose files contains the orchestration of the benchmark software components described above, having the needed deployment configurations setup there.

## Package Structure Outline
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
            │   └── <span style="background-color:#4E9A06"><font color="#3465A4">prometheus_data</font></span>
            ├── <font color="#3465A4"><b>qos1</b></font>
            │   └── <span style="background-color:#4E9A06"><font color="#3465A4">prometheus_data</font></span>
            └── <font color="#3465A4"><b>qos2</b></font>
                └── <span style="background-color:#4E9A06"><font color="#3465A4">prometheus_data</font></span>

73 directories
</pre>

## Benchmark setup
There are different docker compose files for each one of the components used in the benchmark (described in section 3 of the paper).
The load is run concurrently with the help of the python script: run_load.py
The subscriber is run manually running the associated docker image.

# Requirements and Dependencies

## Experiments Logs Analysis
- Any Jupyter Notebook editor (e.g. Jupiter Lab) -- for reproducing aggreated results
    - Instructions to install Jupyter can be found [here](https://jupyter.org/install)
- Python 3

## Running the experiment
- Docker container runtime engine (AUT docker containers needs to be recreated based on transformation of benchmark sample data into a uniform data model)
- Python 3

## Results
The results can be found in the resutls folder. Replication of the results can be obtained by running the data_analysis Jupiter Notebook in the data analysis folder. **Note that the full/absolute path to the logs in this replication package needs to be set there manually.**
The Jupyter Notebook incrementally builds up the results depicted in Table IV and Figures 4-9 of the paper, starting by parsing the logs in this repository and building the necessary numpy array data structures. Firstly the global results are generated, followed by the in depth analysis of the results filtering the dataset by MQTT payload sizes (small - provider 2, gateway 1, medium and large - provider 1, gateways 2 and 1 respectively).

The generated plots are also saved into the results folder and an spreadsheet converted to PDF named ```MQTT_Benchmark_results_overview_per_gateway.pdf```  is also provided with the extraction of values used in the results section.

## Replication of Prometheus data
Data stored in prometheus from the experiments can be visualized in the GUI at localhost:9090 after mounting the different experiment records folder as a read and write volume when running Prometheus docker container. As an example for AUT1, 29 bytes topic overhead (AUT 3).

```
docker run -p 9090:9090  -v PATH-TO-REPLICATION-PACKAGE/transformer/logs/aut3/qos1/prometheus_data:/prometheus prom/prometheus
```

## Replication Instructions

### Recreation of AUT Bridge Component
To recreate the data transformation component, a subcriber and publisher client must be implemented in this component for bridging heterogeneous data ingested by the different sensor data providers to the following unifying data model:
![Common Data Model](https://smartoceanplatform.github.io/sodataformat.png)

This component must be configured using the configuration parameters under the transformation/configs folder for each benchmark setup used.

### Benchmark Execution Steps

1. Generate configure HiveMQ [monitoring](https://github.com/hivemq/hivemq-prometheus-extension) and [credentials](https://github.com/hivemq/hivemq-file-rbac-extension) plugins for the source and destination brokers:
   - Fetch and configure the plugins by running the script under ```script/setup-hiveMQ.sh```. 
   - The script in ```script/generate_rbac_file.py``` can be used to generate the needed credentials that are saved into the env variables after the execution of the script. 
3. Define QoS benchmark parameter for clients and brokers (can be done using env variables or directly in the docker compose QOS variable)
2. Run monitoring sub-system (```docker-compose-monitoring.yml``` docker compose file)
3. Run ingestion broker for each sensor data provider (```docker-compose-ingestion.yml``` source brokers docker compose file)
2. Run AUT option (docker compose files ```docker-compose-aut1.yml``` and ```docker-compose-aut2.yml```) including the generated credentials file in scripts/
2. Run the subscriber
4. Run Load using the python script: ```run_load.py```

All the log files outlines above were bound from the host machine when running the experiment using docker engine.

