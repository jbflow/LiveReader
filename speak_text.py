"""This script just takes text and speaks it out load, the kill process function is used to interupt. Copyright (c)
2020, Josh Ball of Flowstate Creative Solutions"""

import accessible_output2.outputs.auto
speech = accessible_output2.outputs.auto.Auto()

def speak_text(TEXT):
    speech.speak(TEXT, interrupt=True)





