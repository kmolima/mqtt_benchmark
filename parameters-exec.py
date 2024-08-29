import argparse
import time
import os
from datetime import datetime
import docker
import threading


def wait_stop_docker(sut_container, publishers, subscribers, broker_container_name:str):
    try:
        # Wait for all publishers to finish
        for container in publishers:
            container.reload()
            if container.status == 'created':
                print(f"Publisher docker image {container.image} with ID: {container.short_id} created.")
            elif container.status == 'running':
                print(f'Waiting for publisher container {container.short_id} to finish publishing load.')
                container.wait()
            container.reload()
            if container.status == 'exited':
                print(f"Docker image {container.image} with ID: {container.short_id} exited.\nRemoving . . .")
                container.remove()

            else:
                print(f"Docker image {container.image} with ID: {container.short_id} status: {container.status}.")

        # Once all publishers have exit, stop all subscribers
        for container in subscribers:
            container.stop(timeout=5)
            print(f"Subscriber docker image {container.image} with ID: {container.short_id} stopped.")

        # Stop broker container image
        sut_container.stop(timeout=10)
        print("Docker image stopped successfully.")
    except KeyboardInterrupt:
        print(f"Interrupting experiment execution")
        sut.stop()
        [c.stop() for c in publishers]
        [c.stop() for c in subscribers]
    except Exception as e:
        print(f"Error stopping docker image: {e}")


def get_ports_for_broker(broker: str) -> dict:
    result = dict()

    result['1883'] = 1883
    result['8080'] = 8080

    return result


def get_volumes_for_broker(broker: str) -> list:
    result = list()
    return result


def run_subscribers(client, n:int, np: int, qos:int, config:int, file_path:str, l_path:str, topic_prefix:str):
    mqtt_clients_image='mqtt_clients:latest'

    # Define environment variables dict
    environment_variables_subscribers = dict()
    environment_variables_subscribers["QOS"] = qos

    if config == 1:
        log_path = '/'.join((l_path,'config1/'))
    else:
        log_path = '/'.join((l_path, 'config2/'))

    # Define volume mappings
    volumes = {
        file_path: {
            'bind': f'/app/configs/subscriber.yml',
            'mode': 'ro',
        },
        log_path: {
            'bind': '/app/logs/',
            'mode': 'rw',
        },
    }

    containers = list()
    for i in range(n):
        try:
            if config == 1:
                topic = topic_prefix  # '/'.join((topic_prefix, f'node{str(i+1)}'))
            elif config == 2:
                topic = '/'.join((topic_prefix, '#'))
            environment_variables_subscribers["TOPIC"] = topic

            client_id = '-'.join(('subscriber', str(i + 1)))
            environment_variables_subscribers["CLIENT_ID"] = client_id

            logfile_prefix = '-'.join((datetime.now().strftime("%d%m%Y%H%M%S"), 'sub', str(i+1),
                                       'config', str(config), "qos", str(qos)))
            logfile_name = '.'.join((logfile_prefix, "log"))
            logfile_path = '/'.join(("/app", "logs", logfile_name))

            environment_variables_subscribers["LOG_FILE"] = logfile_path

            if config == 1:
                cmd = ['subscriber.py', '--configfile', '/app/configs/subscriber.yml', '--logfile',
                       logfile_path, '--ntopics', str(np)]
            elif config == 2:
                cmd = ['subscriber.py', '--configfile', '/app/configs/subscriber.yml', '--logfile',
                       logfile_path]

            # Run the container
            container = client.containers.run(
                image=mqtt_clients_image,
                environment=environment_variables_subscribers,
                extra_hosts={'host.docker.internal': 'host-gateway'},
                network_mode='bridge',
                volumes=volumes,
                entrypoint='python',
                command=cmd,
                mem_limit='4g',
                cpuset_cpus='5-8',
                detach=True  # Run in the background
            )
            containers.append(container)
            print(f'Subscriber container {i + 1} started with ID: {container.short_id}')

        except Exception as e:
            print(f'Error starting subscriber container {i + 1}: {e}')
            container.stop()
            container.remove()

    return containers


def run_publishers(client, n:int, qos:int, file_path:str, log_path:str, topic_prefix:str, payload_path:str):
    mqtt_clients_image = 'mqtt_clients:latest'

    # Define environment variables dicts
    environment_variables_publishers = dict()

    environment_variables_publishers["QOS"] = qos

    cmd=['main.py','--configfile','/app/configs/publisher.yml']

    volumes = {
        f'{file_path}': {
            'bind': f'/app/configs/publisher.yml',
            'mode': 'ro',
        },
        payload_path: {
            'bind': '/app/data',
            'mode': 'ro',
        },
        log_path: {
            'bind': '/app/logs',
            'mode': 'rw',
        },
    }

    containers = list()
    for i in range(n):
        try:
            topic = '/'.join((topic_prefix, f'node{str(i + 1)}'))
            environment_variables_publishers["TOPIC"] = topic

            client_id = '-'.join(('publisher', str(i + 1)))
            environment_variables_publishers["CLIENT_ID"] = client_id

            # Run the container
            container = client.containers.run(
                image=mqtt_clients_image,
                environment=environment_variables_publishers,
                volumes=volumes,
                entrypoint='python',
                network_mode='bridge',
                extra_hosts={'host.docker.internal':'host-gateway'},
                mem_limit='1g',
                cpuset_cpus='0-3',
                command=cmd,
                detach=True  # Run in the background
            )
            containers.append(container)
            print(f'Publisher container {i + 1} started with ID: {container.short_id}')
        except Exception as e:
            print(f'Error starting publisher container {i + 1}: {e}')
            container.stop()
            container.remove()

    return containers


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment_num", type=int, required=True, default=10, help="Numbers of executions per experiment")
    parser.add_argument("--payload",default=None,type=str,help="Payload file path to use")
    parser.add_argument('--publishers', type=int, required=True, help='Number of MQTT publishers clients')
    parser.add_argument('--subscribers', type=int, required=True, help='Number of MQTT subscribers clients')
    parser.add_argument('--publishers_config', type=str, required=True, help='MQTT publishers clients config')
    parser.add_argument('--subscribers_config', type=str, required=True, help='MQTT subscribers clients config')
    parser.add_argument('--publishers_logs', type=str, required=True, help='MQTT publishers clients log folder')
    parser.add_argument('--subscribers_logs', type=str, required=True, help='MQTT subscribers clients log folder')
    args = parser.parse_args()

    qoss = [0, 1, 2]
    mqtt_brokers = ['hivemq/hivemq4', 'emqx']  # single node
    topic_prefix = 'topic/structure'

    if not os.path.isdir(args.payload):
        print(f"Error JSON payload folder not found. Make sure the paths are correct.")
        exit()

    if not os.path.isfile(args.publishers_config):
        print(f"Error MQTT publisher client config file not found. Make sure the paths are correct.")
        exit()

    if not os.path.isfile(args.subscribers_config):
        print(f"Error MQTT subscriber client config file not found. Make sure the paths are correct.")
        exit()

    if not os.path.isdir(args.publishers_logs):
        print(f"Error MQTT publisher client log folder not found. Make sure the paths are correct.")
        exit()

    if not os.path.isdir(args.subscribers_logs):
        print(f"Error MQTT subscriber client log folder not found. Make sure the paths are correct.")
        exit()

    client = docker.from_env()

    for config in range(1,3):  # 2
        for mqtt_broker in mqtt_brokers:  # 2
            for qos in qoss:  # 3
                for experiment in range(args.experiment_num):  # 5

                    # Run SUT
                    ports = get_ports_for_broker(mqtt_broker)
                    mounts = get_volumes_for_broker(mqtt_broker)
                    broker_name = '-'.join((mqtt_broker.replace('/','-'), str(qos),str(config)))

                    # Remove older images
                    # client.containers.get(broker_name).stop()
                    # client.containers.get(broker_name).remove()

                    environment_variables_broker = dict()

                    try:
                        sut = client.containers.run(image=mqtt_broker, command='', publish_all_ports=True, volumes=mounts,
                                                name=broker_name, network_mode='bridge', ports=ports, mem_limit='12g',
                                                environment=environment_variables_broker, detach=True, remove=True,
                                                cpuset_cpus='10-19',
                                                auto_remove=True)
                        print(f'SUT container MQTT Broker {broker_name} started with ID: {sut.short_id}')

                        time.sleep(5)

                        # Run MQTT Clients -- Subscribers
                        sub_containers = run_subscribers(client, n=args.subscribers, np=args.publishers, qos=qos,
                                                         config=config, topic_prefix=topic_prefix,
                                                         file_path=args.subscribers_config, l_path=args.subscribers_logs)

                        time.sleep(5)

                        # Run MQTT Clients -- Publishers
                        pub_containers = run_publishers(client, n=args.publishers, qos=qos, topic_prefix=topic_prefix,
                                                        file_path=args.publishers_config, payload_path=args.payload,
                                                        log_path=args.publishers_logs)

                        threading.Thread(target=wait_stop_docker, name='wait_stop_docker',
                                         args=(sut, pub_containers, sub_containers, broker_name)).start()

                        sut.wait()  # container is stopped when MQTT clients finish publishing configured load in wait_stop_docker method

                        time.sleep(30)  # waits 1 min between experiments execution
                    except Exception as e:
                        # for c in client.containers.list():
                        #     c.stop()
                        #     c.remove()
                        print(f'Error executing experiment containers: {e}')
                        if sut is not None:
                            if sut.status == 'running':
                                sut.stop(timeout=10)
                    finally:
                        print(f'Finished execution for parameters:\t'
                              f'QoS: {qos}\t'
                              f'Config: {config}\t'
                              f'Broker: {mqtt_broker}')
