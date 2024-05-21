import signal
import atexit


def handle_exit(*args):
    try:
        with open('log.txt', 'x') as file:
            file.write('exit')
    except BaseException as exception:
        with open('logs.txt', 'x') as file:
            file.write('exit')


atexit.register(handle_exit)
signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

while True:
    pass