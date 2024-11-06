import argparse
import time
import subprocess


def run_docker_compose(compose_file):
    try:
        with subprocess.Popen(
            ["docker-compose", "-f", compose_file, "up", "-d",
             "--exit-code-from finish", "--abort-on-container-exit"]
        ) as proc:
            proc.wait()
            print("Docker Compose started successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.returncode}")
        print(e.output)


def stop_docker_compose(compose_file):
    try:
        with subprocess.Popen(
            ["docker-compose", "-f", compose_file, "down"]
        ) as proc:
            proc.wait()
            print("Docker Compose stopped successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.returncode}")
        print(e.output)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--numexecs", default=10, type=int, help="Number of executions for parameter")
    parser.add_argument("--stats", required=True, help="stats file")

    args = parser.parse_args()

    numexecs = args.numexecs

    # Verify input benchmark parameters
    assert (numexecs >= 1)

    print(f"Running {numexecs} repetitions. . .")

    # clients docker compose file
    load_docker_compose = "docker-compose-clients.yml"

    # Run docker stats
    try:
        with subprocess.Popen(
            ["/bin/bash", "record_stats.sh", args.stats]
        ) as proc:
            proc.wait()
            print("Docker stats recording started successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.returncode}")
        print(e.output)

    for exec in range(numexecs):
        try:
            # Run MQTT Clients
            run_docker_compose(load_docker_compose)
            time.sleep(30)  # time between load repetition run

        except Exception as e:
            stop_docker_compose(load_docker_compose)
            print(f'Error executing experiment containers: {e}')
        finally:
            print(f'Finished execution {exec}')


if __name__ == "__main__":
    main()