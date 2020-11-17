import multiprocessing
import signal
import time
import sys
import subprocess

from crawlers.crawler_manager import file_downloader_process, \
    file_descriptor_process

# GLOBAL VARIABLES

stop_processes = False
process_exception = None
n_processes_running = 0
global_lock = multiprocessing.Lock()

# END GLOBAL VARIABLES

# FUNCTIONS THAT SHOULD BE EXECUTED BY PROCESSES

N_FUNCTIONS = 3


def run_django():
    # Runs django repassing cli parameters
    subprocess.run(["python", "manage.py", "runserver"] + sys.argv[1:])


def run_file_downloader():
    file_downloader_process()


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
        [run_django, []],
        [run_file_downloader, []],
        [runn_file_descriptor, []],
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
        pool.terminate()
        pool.join()

    except Exception as e:
        # re-raises process exception and stop processes, printing traceback
        print("A process failed, terminating processes...")
        pool.terminate()
        pool.join()
        raise e

    else:
        # stop processes
        pool.terminate()
        pool.join()


if __name__ == "__main__":
    run()
