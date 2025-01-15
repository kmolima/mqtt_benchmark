import logs_parser
import numpy as np
import os


def get_resources_np_array(logs, aut, qos):
    entries_list = list()

    # Debugging: Print the length of logs
    print(f"Number of log entries: {len(logs)}")

    for log_group in logs:
        for log in log_group:
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
                log['block_io_written_unit']
            ]
            entries_list.append(tuple(row))

    # Define a custom dtype for the structured array
    dtype = [('aut', 'U64'), ('qos', 'U64'),
             ('name', 'U64'), ('cpu', 'f8'), ('mem_percent', 'f8'),('pids', 'i4'),
             ('net_io_received', 'f8'), ('net_io_received_unit', 'U64'),
             ('net_io_transmitted', 'f8'), ('net_io_transmitted_unit', 'U64'),
             ('block_io_read', 'f8'), ('block_io_read_unit', 'U64'),
             ('block_io_written', 'f8'), ('block_io_written_unit', 'U64'), ]

    # Convert to NumPy structured array
    entries_np_array = np.array(entries_list, dtype=dtype)
    print(f"Number of NP entries: {len(entries_np_array)}")
    return entries_np_array


def get_stat_log_file(log_dir):
    for file in os.listdir(log_dir):
        if file.startswith('stats'):
            return file
    return None


if __name__ == "__main__":
    auts=['aut1_15b','aut1_29b','aut2']
    qoss = ['qos0', 'qos1', 'qos2']
    for aut in auts:
        for qos in qoss:
            host_machine1_docker_stats=f'../subscriber/logs/{aut}/{qos}/stats-aut1-qos0.txt'
            host_machine2_docker_stats=f'../transformer/logs/{aut}/{qos}/aut1.txt'

    host_machine1_docker_stats = f'../subscriber/logs/aut1_15b/qos0/stats-aut1-qos0.txt'
    host_machine2_docker_stats = f'../transformer/logs/aut1_15b/qos0/stats-aut1-qos0.txt'

    raw_data1=logs_parser.get_stats_logs(host_machine1_docker_stats)
    raw_data2=logs_parser.get_stats_logs(host_machine2_docker_stats)

    dataset1=get_resources_np_array(raw_data1,"aut1_15b","qos0")
    dataset2=get_resources_np_array(raw_data2,"aut1_15b","qos0")

    print(raw_data1[0])
    print(len(dataset1))
    print(get_stat_log_file('../subscriber/logs/aut2/qos0'))
    print(get_stat_log_file('../transformer/logs/aut2/qos0'))