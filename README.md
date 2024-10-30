# MQTT Benchmark
Collection of scripts to automate MQTT platform benchmark.
Also collects data from experiments execution.

## Execution Steps

1. Generate HiveMQ credentials files for the ingestion broker (connected to external network)
2. Define QoS benchmark parameter for clients and brokers (env variable)
2. Run monitoring sub-system (docker compose)
3. Run ingestion broker for each sensor data provider
2. Run AUT option (docker compose) including the generated credentials file
2. Run Clients launcher script (python)
   3. Takes the generated password as an argument for the MQTT clients launched
