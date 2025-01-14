# imports
import numpy as np
import re
import os
import datetime

# Experiment Parameters
NUM_RUNS=10
NUM_PUB=3  # (GATEWAYS)
NUM_QOS_CONFIG=3
NUM_MSG=1000
NUM_PROVIDERS=2
NUM_HUBS=4
total_expected_messages = NUM_MSG * NUM_HUBS * NUM_RUNS


# Define the regular expression pattern for a log entry
global sub_log_pattern
sub_log_pattern = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{4})" # Timestamp
    r"\[(?P<level>[A-Z]+)\],"                      # Log LEVEL, e.g. INFO
    r"(?P<uuid>[0-9a-fA-F]{64}),"                  # UUID: 64 hexadecimal characters
    r"(?P<send_time>\d+\.\d+),"                    # Received Time: floating point number
    r"(?P<received_time>\d+\.\d+),"                # Send Time: floating point number
    r"(?P<topic>[^\s,]+),"                        # Topic: non-whitespace, non-comma characters
    r"(?P<size>\d+),"                              # Payload Size: integer
    r"(?P<tsize>\d+),"                            # Topic Size: integer
    r"(?P<order>\d+)"                             # Transmission Order in Gateway: integer
)

# Define the regular expression pattern for blocks of docker stats reading in the stats file
# Blocks divided by this header: CONTAINER ID                                                       NAME                       CPU %     MEM USAGE / LIMIT     MEM %     NET I/O           BLOCK I/O         PIDS
global header_pattern
header_pattern = re.compile(
    r"CONTAINER ID\s+"
    r"NAME\s+"
    r"CPU %\s+"
    r"MEM USAGE / LIMIT\s+"
    r"MEM %\s+"
    r"NET I/O\s+"
    r"BLOCK I/O\s+"
    r"PIDS"
)

# Regular expression pattern
global transformer_pattern
transformer_pattern = re.compile(
    r'''
    (?P<time_transformer>\d{2}:\d{2}:\d{2})\[INFO\]:Transformer\s+\[User\ data\]\s+<class\s+'paho\.mqtt\.properties\.Properties'>:\s+\[UserProperty\s*:\s+
    \[(?P<properties>[^]]+)\]\]\n
    (?P<time_queue_transform>\d{2}:\d{2}:\d{2})\[INFO\]:Transformer\s+\[Queue:transform\]\n
    (?P<time_transformer_in>\d{2}:\d{2}:\d{2})\[INFO\]:(?:AADI|WSense)\s+node\s+transformer\s+in\s*:\s*(?P<transformer_in>\d+)\s+bytes\n
    (?P<time_transformer_out>\d{2}:\d{2}:\d{2})\[INFO\]:(?:AADI|WSense)\s+node\s+transformer\s+out\s*:\s*(?P<transformer_out>\d+)\s+bytes
    ''',
    re.VERBOSE
)

# Sample: 480caafe8eb6013bb304c4500652db04ca28aa698c7cc688ceb5f21e9f5a41dc   ingestion-hivemq-broker1   0.51%     537.1MiB / 15.61GiB   3.36%     346MB / 19MB      28.7kB / 138MB    95
global stats_log_pattern
stats_log_pattern = re.compile(
    r"(?P<container_id>[0-9a-fA-F]{64})\s+"                                    # CONTAINER ID: 64-character hex string
    r"(?P<name>[^\s]+)\s+"                                                     # NAME: non-whitespace characters
    r"(?P<cpu>[\d.]+)%\s+"                                                     # CPU %: floating-point number followed by "%"
    r"(?P<mem_usage>[\d.eE+-]+[a-zA-Z]+)\s*/\s*(?P<mem_limit>[\d.eE+-]+[a-zA-Z]+)\s+"  # MEM USAGE / LIMIT with units and scientific notation  # MEM USAGE / LIMIT
    r"(?P<mem_percent>[\d.]+)%\s+"                                             # MEM %: floating-point number followed by "%"
    r"(?P<net_io_received_value>[\d.eE+-]+)\s*(?P<net_io_received_unit>[a-zA-Z]*)\s*/\s*"           # NET I/O received value and unit
    r"(?P<net_io_transmitted_value>[\d.eE+-]+)\s*(?P<net_io_transmitted_unit>[a-zA-Z]*)\s+"         # NET I/O transmitted value and unit
    r"(?P<block_io_read_value>[\d.eE+-]+)\s*(?P<block_io_read_unit>[a-zA-Z]*)\s*/\s*"               # BLOCK I/O read value and unit
    r"(?P<block_io_written_value>[\d.eE+-]+)\s*(?P<block_io_written_unit>[a-zA-Z]*)\s+"             # BLOCK I/O written value and unit
    r"(?P<pids>\d+)"                                                           # PIDS: integer
)

def get_resources_np_array(logs, aut, qos):
    entries_list = list()

    for i,log_group in enumerate(logs):
        for log in log_group:
            # Cleanup malformed data
            if log['name'].endswith('ingestion-hivemq-broker2'):
                log['name']='ingestion-hivemq-broker2'
            row = [
                aut,
                qos,
                log['name'],
                log['cpu'],
                log['mem_percent'],
                log['pids'],
                log['net_io_received_value'],
                log['net_io_received_unit'],
                log['net_io_transmitted_value'],
                log['net_io_transmitted_unit'],
                log['block_io_read_value'],
                log['block_io_read_unit'],
                log['block_io_written_value'],
                log['block_io_written_unit'],
                i
            ]
            entries_list.append(tuple(row))

    # Define a custom dtype for the structured array
    dtype = [('aut', 'U64'), ('qos', 'U64'),
             ('name', 'U64'), ('cpu', 'f8'), ('mem_percent', 'f8'),('pids', 'i4'),
             ('net_io_received', 'f8'), ('net_io_received_unit', 'U64'),
             ('net_io_transmitted', 'f8'), ('net_io_transmitted_unit', 'U64'),
             ('block_io_read', 'f8'), ('block_io_read_unit', 'U64'),
             ('block_io_written', 'f8'), ('block_io_written_unit', 'U64'), 
             ('entry_id','i4')]

    # Convert to NumPy structured array
    entries_np_array = np.array(entries_list, dtype=dtype)
    return entries_np_array


def get_stat_log_file(log_dir):
    for file in os.listdir(log_dir):
        if file.startswith('stats'):
            return file
    return None

# Load log entries from aut / qos folder
def get_sub_logs(log_path:str) -> list:
    # Store parsed log entries
    filtered_messages = list()

    discarded_logs=0

    if not os.path.isdir(log_path):
        raise Exception(f'{log_path} is not a directory')

    # Process each directory / config
    for file in os.listdir(log_path):
        log_file=os.path.join(log_path,file)
        if os.path.isfile(log_file) and file.startswith('subscriber.log'):
            with open(log_file, 'r') as file:
                for line in file:
                    _line=line.strip()
                    match = sub_log_pattern.match(_line)
                    # Filter log messages
                    if match:
                        log_entry = match.groupdict()
                        filtered_messages.append(log_entry)
                    elif "site1/provider" in line and "Received message on topic:" not in line:
                        print(line)
                        discarded_logs+=1
    print(f'Log entries: {len(filtered_messages)}')
    print(f'Discarded log entries: {discarded_logs}')
    return filtered_messages


def get_lost_messages(logs:list):
    return total_expected_messages-len(logs)


# Create numpy array with columns from filtered logs
# Sample: 2024-11-08T16:01:12+0000[INFO],59deb5b4a8e0cac1812dd5e65e7f526c41c76879b26b8135673513b0834727c1,1731046681182.7021,1731046681396.9114,site1/provider1,9131,15,602
# From the implementation: sub.log(mid, send_time, recv_time, msg.topic, len(msg.payload), len(msg.topic), order)
def get_numpy_array(logs, t_np_array, dates_bounds):
    entries_list = list()
    for log in logs:
        timestamp = log['timestamp']
        send_time = log['send_time']
        rcv_time  = log['received_time']
        delay = float(float(rcv_time) - float(send_time))
        if 'site1/provider2' in log['topic'] or int(log['size']) == 518 or int(log['size']) == 1523:
            gateway = 'provider2.gateway1'
        elif log['topic'] == 'site1/provider1/gateway1/hub1' or int(log['size']) == 11076:
            gateway = 'provider1.gateway1'
        elif log['topic'] == 'site1/provider1/gateway2/hub1' or int(log['size']) == 9131:
            gateway = 'provider1.gateway2'
        else:
            match = get_gateway_per_bound(dates_bounds,np.datetime64(timestamp),log['topic'])
            if match:
                gateway = match
            else:
                gateway = get_gateway_by_uuid(t_np_array,log['uuid'])
        row = [
            np.datetime64(timestamp),  # Column 1 (index 0) Timestamp
            log['uuid'],               # Column 2 (index 1) UUID
            delay,                     # Column 3 (index 2 and 3) Received Time - Send Time
            log['topic'],              # Column 4 (index 4) Topic
            int(log['size']),          # Column 5 (index 5) Payload size in bytes
            int(log['tsize']),         # Column 6 (index 6) Topic size in bytes
            int(log['order']),         # Column 7 (index 7) Sent Order
            gateway                    # Column 8 (index 8) Gateway
        ]
        entries_list.append(tuple(row))
            
    # Define a custom dtype for the structured array
    dtype = [('timestamp','datetime64[s]'), ('uuid', 'U64'), ('latency', 'f8'), ('topic', 'U64'), ('payload_size', 'i4'),
             ('topic_size', 'i4'), ('order', 'i4'),('gateway','U64')]
    
    # Convert to NumPy structured array
    entries_np_array = np.array(entries_list, dtype=dtype)
    
    return entries_np_array


def get_gateway_per_bound(d, time, topic):
    result = None
    topic_provider = topic.split('/')
    for k,entry in enumerate(d.items()):
        provider = entry[0]
        if topic_provider[1] not in provider:
            continue
        for i, timestamp in enumerate(entry[1]):
            assert len(entry[1]) == NUM_RUNS
            if i < (len(entry[1])-1):
                if timestamp <= time <= entry[1][i + 1]:
                    return provider
            else:
                if timestamp <= time <= (timestamp + datetime.timedelta(milliseconds=400)):
                    return provider

    return result


def get_bounded_sub_logs(narray, start_interval, end_interval=None):
    # Last execution doesn't have upper bound
    if end_interval:
        return narray[(narray['timestamp'] >= start_interval) & (narray['timestamp'] < end_interval)]
    else:
        return narray[(narray['timestamp'] >= start_interval)]


def extract_datetime_from_filename(filename: str):
    # Define the regular expression pattern to match the date and time
    pattern = re.compile(r"(\d{8})_(\d{6})")
    match = pattern.search(filename)

    if match:
        date_str, time_str = match.groups()
        # Combine the date and time strings
        datetime_str = f"{date_str}{time_str}"
        # Parse the combined string into a datetime object
        log_datetime = datetime.datetime.strptime(datetime_str, "%Y%m%d%H%M%S")
        return log_datetime
    else:
        raise ValueError("Filename does not contain a valid datetime pattern")


def get_pub_exec_datetimes(logs):
    '''
    Get a tuple with datetimes for the execution of each experiment repetition
    :param logs: logs path for a specific AUT and QoS
    :return: tuple with list of datetimes per provider
    '''
    times=dict()
    if os.path.isdir(logs):
        for entry in os.listdir(logs):
            file = os.path.join(logs, entry)
            if os.path.isfile(file) and entry.startswith("provider"):
                provider = entry[:18]
                t = extract_datetime_from_filename(entry)
                ts = times.setdefault(provider, list())
                ts.append(t)
                ts.sort()

    return times


def get_trans_logs(log_path):
    # Store parsed log entries
    entries_list = list()

    # Regular expression for getting the transformer id from the log file name
    pattern = re.compile(r'log-([^\.]+)\.log')
    if not os.path.isdir(log_path):
        raise Exception(f'{log_path} is not a directory')

    # Process each directory / config
    for file_name in os.listdir(log_path):
        is_log=pattern.search(file_name)
        if is_log:
            transformer_id = is_log.group(1)
            log_file = os.path.join(log_path, file_name)
            if os.path.isfile(log_file):
                with open(log_file, 'r') as file:
                    lines= file.read()
                    matches = transformer_pattern.findall(lines)
                    for match in matches:
                        if match:
                            properties_match = re.search(
                                r"""unique_message_id',\s*'(?P<unique_message_id>[^']+)'.*'order',\s*'(?P<order>\d+)'""",
                                match[1]
                            )
                            if properties_match:
                                unique_message_id = properties_match.group('unique_message_id')
                                transformer_in = match[4]
                                transformer_out = match[6]
                                order = properties_match.group('order')
                                row = [
                                    transformer_id,     # Column 1  Timestamp
                                    unique_message_id,  # Column 2  UUID
                                    transformer_in,     # Column 3  amount of bytes from ingestion
                                    transformer_out,    # Column 4 amount of bytes to core
                                    order               # Column 5 sent order
                                ]
                                entries_list.append(tuple(row))
        else:
            continue

    # Define a custom dtype for the structured array
    dtype = [('id', 'U64'), ('uuid', 'U64'), ('bytes_in', 'i4'), ('bytes_out', 'i4'), ('order', 'i4')]

    # Convert to NumPy structured array
    entries_np_array = np.array(entries_list, dtype=dtype)

    return entries_np_array


def get_gateway_by_uuid(nparray, uid) -> str:

    in_size = nparray[nparray['uuid'] == uid]['bytes_in']

    if in_size >= 125000 :
        return 'provider1.gateway1'
    elif in_size >= 35703:
        return 'provider1.gateway2'
    elif in_size >= 1500:
        return 'provider2.gateway1'
    else:
        raise RuntimeError(f"Unrecognized Gateway, for UUDI:{uid}\n Log: {nparray[nparray['uuid'] == uid]}")

def get_stats_logs(file_path: str):
    # Block of logs
    log_block=0
    log_group=list()
    # Parse each line
    parsed_logs = list()
    invalid_log_lines=0
    # Split the log block into lines and parse each log entry
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            for _line in file:
                # Strip leading and trailing whitespace from the line
                line = _line.strip()
                # Skip empty lines
                if not line:
                    continue

                if not header_pattern.match(line):
                    match = stats_log_pattern.match(line.strip())
                    if match:  # beginning of block of samples
                        log_data = match.groupdict()
                        parsed_logs.append(log_data)
                    else:
                        # print(f"Log entry does not match the pattern: {line}")
                        invalid_log_lines+=1

                # Header match -> beginning of new block of samples
                if header_pattern.match(line):
                    log_block += 1
                    # Change block and reset log entry structure
                    if len(parsed_logs) > 0:
                        log_group.append(parsed_logs)
                        parsed_logs = list()
                    
    print(f"Loaded {len(log_group)} groups of log entries and discarded {invalid_log_lines} invalid entries from: {file_path}.")
    return log_group


def get_execs_bounds(d):

    # sanity check
    for v in d.values():
        assert len(v) == NUM_RUNS
    execs_boundaries = list()
    for execution in range(NUM_RUNS):
        for key in d.keys():
            start_time = d[key][execution]
            if len(execs_boundaries) > execution:
                if execs_boundaries[execution] < start_time:  # we want the load execution that finished later
                    execs_boundaries[execution] = start_time
            else:
                execs_boundaries.append(start_time)

    assert len(execs_boundaries) == NUM_RUNS

    return execs_boundaries


def get_np_stats(narray):

    result = dict()
    avg   = np.mean(narray)
    stdev = np.std(narray)
    max_arg = np.argmax(narray)
    min_arg = np.argmin(narray)

    result['avg']=avg
    result['stdev']=stdev
    result['max']=narray[max_arg]
    result['min']=narray[min_arg]
    result['max_arg']=max_arg
    result['min_arg']=min_arg

    return result

def main():
    load = get_sub_logs('/home/keila/smartoceanplatform/mqtt_benchmark/subscriber/logs/aut2/qos2')
    print(f"Number of log entries: {len(load)}")
    print(load[0])

    lost_msgs=get_lost_messages(load)
    np_array=get_numpy_array(load)
    dims=np.ndim
    dates = get_pub_exec_datetimes('/home/keila/smartoceanplatform/mqtt_benchmark/publisher/logs/aut2/qos2')

    execs_bounds=get_execs_bounds(dates)

    print(dates)
    print(execs_bounds)

    sub_logs_per_execution_sets=list()
    for i, bound in enumerate(execs_bounds):
        if i < (len(execs_bounds)-1):
            sub_logs_per_execution_sets.append(get_bounded_sub_logs(np_array,bound,execs_bounds[i+1]))
        else:
            sub_logs_per_execution_sets.append(get_bounded_sub_logs(np_array, bound))

        #print(len(sub_logs_per_execution_sets[i]))
        #print(sub_logs_per_execution_sets[i])

    print(len(sub_logs_per_execution_sets))

    delay = get_np_stats(np_array['latency'])

    rcv_msgs = len(np_array)
    lost_msgs = get_lost_messages(load)

    avg_rcv_msgs = rcv_msgs / NUM_RUNS
    avg_lost_msg = lost_msgs / NUM_RUNS

    topic_size = get_np_stats(np_array['topic_size'])

    # avg_payload_size_provider1
    uniques = np.sum(np.unique_counts(np_array['uuid']).counts)
    duplicates_count = rcv_msgs - uniques
    print(uniques)
    avg_duplicates   = duplicates_count / NUM_RUNS

    print(f'Setup\tDelay\tReceived Msg\tLost Msg\tDuplicated\tTopic')
    print(f'AUT2/QOS2:\t{delay["avg"]}\t{avg_rcv_msgs}\t{avg_lost_msg}\t{avg_duplicates}\t{topic_size["avg"]}')

    # Global Payload sizes
    payload=get_np_stats(np_array['payload_size'])

    print(f'stdev_delay: {delay["stdev"]}')
    print(f'max_delay {delay["max"]}')
    print(f'min_delay {delay["min"]}')
    print(f'max_topic_size: {topic_size["max"]}')
    print(f'min_topic_size {topic_size["max"]}')
    print(f'avg_payload: {payload["avg"]}')
    print(f'p_stdev_payload: {payload["stdev"]}')
    print(f'p_max: {payload["max"]}')
    print(f'p_min: {payload["min"]}')


if __name__ == "__main__":
    trans_array = get_trans_logs('/home/keila/smartoceanplatform/mqtt_benchmark/transformer/logs/aut1/qos1')
    print(len(trans_array))
    print(trans_array[156])
    print(trans_array[4])

    #print(get_gateway_by_uuid(trans_array,'ce167b58422f3eca447f07d2215d0117ae324ff0fce8c09401e63cc109c98443'))

    dates = get_pub_exec_datetimes('/home/keila/smartoceanplatform/mqtt_benchmark/publisher/logs/aut1/qos1')

    load = get_sub_logs('/home/keila/smartoceanplatform/mqtt_benchmark/subscriber/logs/aut1/qos1')

    lost_msgs=get_lost_messages(load)
    print(f"Number of log entries: {len(load)}")
    np_array=get_numpy_array(load, trans_array, dates)
    print(np_array[0])











