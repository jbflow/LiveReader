"""Copyright (c) 2020, Josh Ball of Flowstate Creative Solutions"""
from rumps import *
from threading import Thread
import midi_ports
import start_up
import get_keypress
import remote_script
from prelisten import turn_on_prelisten


@clicked('Quit')
def quit_but(_):
    get_keypress.stop()
    midi_ports.clean_up()
    rumps.quit_application()


def _run_startup():
    if not start_up.live_is_running():
        start_up.wait_for_start()
    else:
        start_up.wait_for_close()

background_thread = Thread(target=_run_startup)

if __name__ == "__main__":
    turn_on_prelisten()
    remote_script.copy()
    midi_ports.open()
    background_thread.start()
    get_keypress.start()
    app = rumps.App("LiveReader", title='LiveReader', quit_button=None)
    app.run()
