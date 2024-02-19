"""This script just takes text and speaks it out load, the kill process method is used to interupt text which is currently being spoken."""

import subprocess


class Speak:
    def __init__(self):
        self.process = None

    def speak_text(self, TEXT):
        self.process = subprocess.Popen(["say", f"\"[[volm 0.1]] {TEXT}\"", "-r", "300", "-v", "Daniel"])


    def kill_process(self):
        if self.process:
            self.process.kill()
