import multiprocessing
import os
import shutil
import signal
import socket
import subprocess
import sys
import time

from crawlers.crawler_manager import file_descriptor_process

import crawling_utils.crawling_utils as crawling_utils

# GLOBAL VARIABLES

stop_processes = False
process_exception = None
n_processes_running = 0
global_lock = multiprocessing.Lock()

# END GLOBAL VARIABLES

# FUNCTIONS THAT SHOULD BE EXECUTED BY PROCESSES

N_FUNCTIONS = 5


def wait_for_port(port):
    # Wait until the process is running in a port
    a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    location = ("127.0.0.1", port)

    while a_socket.connect_ex(location):
        time.sleep(1)
        a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    a_socket.close()


def run_django():
    signal.signal(signal.SIGCHLD, lambda _, __: os.wait())
    wait_for_port(9092)

    # Runs django repassing cli parameters
    subprocess.run(["python", "manage.py", "runserver"] + sys.argv[1:])

def run_zookeeper():
    crawling_utils.check_file_path("crawlers/log/")
    os.chdir('kafka_2.13-2.4.0')

    # Starts zookeeper server with overriten properties
    subprocess.run(['bin/zookeeper-server-start.sh',
                    'config/zoo.properties'],
                   stdout=open(f"../crawlers/log/zookeeper.out", "a", buffering=1),
                   stderr=open(f"../crawlers/log/zookeeper.err", "a", buffering=1))


def run_kafka():
    wait_for_port(2181)
    crawling_utils.check_file_path("crawlers/log/")
    os.chdir('kafka_2.13-2.4.0')

    # Starts kafka server
    subprocess.run(['bin/kafka-server-start.sh',
                    'config/server.properties',
                    '--override',
                    'log.dirs=kafka-logs'],
                   stdout=open(f"../crawlers/log/kafka.out", "a", buffering=1),
                   stderr=open(f"../crawlers/log/kafka.err", "a", buffering=1))

def runn_file_descriptor():
    file_descriptor_process()


# END FUNCTIONS THAT SHOULD BE EXECUTED BY PROCESSES

def init_process():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def signal_done(r):
    global global_logk, n_processes_running
    with global_lock:
        n_processes_running -= 1


def signal_stop(e):
    global stop_processes, process_exception
    stop_processes = True
    process_exception = e


def run():
    global stop_processes, process_exception, n_processes_running, global_lock

    print("Initializing processes")
    pool = multiprocessing.Pool(
        processes=N_FUNCTIONS,
        initializer=init_process,
    )

    # List functions that will be executed by processes
    functions = [
        [run_zookeeper, []],
        [run_kafka, []],
        [run_django, []],
        [runn_file_descriptor, []],
        # [run_file_downloader, []],
    ]

    # N_FUNCTIONS must be equal to len(functions)
    with global_lock:
        n_processes_running = N_FUNCTIONS

    for (f, args) in functions:
        pool.apply_async(
            func=f,
            args=args,
            callback=signal_done,
            error_callback=signal_stop,
        )

    # end list function
    try:
        while True:
            with global_lock:
                # stop processes if any of them stopped running
                if n_processes_running != N_FUNCTIONS:
                    print("A process ended, terminating processes...")
                    break

            time.sleep(5)
            if stop_processes:
                # re-raise an excetion raised by one of the processes
                raise process_exception

    except KeyboardInterrupt:
        # stop process on KeyboardInterrupt
        print("KeyboardInterrupt, terminating processes...")

    except Exception as e:
        # re-raises process exception and stop processes, printing traceback
        print("A process failed, terminating processes...")
        raise e

    finally:
        # stop kafka and zookeeper:
        os.chdir('kafka_2.13-2.4.0')
        subprocess.run(['bin/kafka-server-stop.sh'])
        subprocess.run(['bin/zookeeper-server-stop.sh'])
        shutil.rmtree('zookeeper')
        shutil.rmtree('kafka-logs')

        # stop processes
        pool.terminate()
        pool.join()


if __name__ == "__main__":
    run()
