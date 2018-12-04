import speech_recognition as sr
import pyaudio
import datetime
import time
import os
from gtts import gTTS
import pyttsx3

import conversation

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceAssistant(object):

    def __init__(self):
        self._mic = sr.Microphone()
        self._recognizer = sr.Recognizer()

        # self._offline_tts = pyttsx3.init()

        # Setting the properties of the offline Text To Speech
        # self._offline_tts.setProperty('voice', 'en+f2')
        # self._offline_tts.setProperty('rate', 120)

    def speak(self, audioString):
        # Adjust for ambient noise
        print(audioString)
        try:
            # Try online TTS
            tts = gTTS(text=audioString, lang='en')
            logger.info("tts is done")
            start = time.time()
            tts.save("audio.mp3")
            save_time = time.time()
            logger.info('Took %s sec to save file' % (save_time - start))
            os.system("mpg321 -a hw:1,0 -q audio.mp3")
            logger.info('Took %s sec to play sound' % (time.time() - save_time))
            time.sleep(0.5)
        except AssertionError:
            logger.info("AssertionError occurred.")
        except Exception as e:
            print("Online TTS unavailable (%s)" % str(e))
            # Use offline TTS
            os.system('espeak "%s" -v en+f2 -s 130 --stdout | aplay -D "sysdefault:CARD=Device"' % audioString)
            # self._offline_tts.say(audioString)
            # self._offline_tts.runAndWait()
            pass

    def trySphinx(self, audio):
        data = ""
        # This offline speech-to-text is called when Google-STT fails
        try:
            data = self._recognizer.recognize_sphinx(audio)
            print(data + " (sphinx)")
        except sr.UnknownValueError:
            self.speak("I'm sorry. Please say that again.")
        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))
        return data

    def adjustAmbient(self):
        with self._mic as source:
            try:
                # calibrate energy threshold for ambient noise
                logger.info("Adjusting for ambient noise.... ")
                self._recognizer.adjust_for_ambient_noise(source)
                if self._recognizer.energy_threshold < 1000.0:
                    self._recognizer.energy_threshold = 1000.0
            except:
                logger.info("Ambient noise adjustment Error")

    def recordAudio(self):
        # Record Audio
        with self._mic as source:
            try:
                time.sleep(1)
                print("Say something: ", end='', flush=True)
                # record audio
                logger.info("Listening....")
                audio = self._recognizer.listen(source, timeout=5, phrase_time_limit=6)
                logger.info("Done listening.")
            except sr.WaitTimeoutError:
                print("Timed out. Please try again.")
                return "Try again."

        # Speech recognition using Google Speech Recognition
        data = ""
        try:
            # Uses the default API key
            data = self._recognizer.recognize_google(audio, language='en-GB')
        except:
            # If Google Speech Recognition fails, try using PocketSphinx
            data = self.trySphinx(audio)
        print("You said: " + str(data))
        return data

    def conversationFlow(self, keyword, songObject=None, songNote=None):
        # should keyword be a list/dictionary of things? easier to just send
        # need to group keywords to make it easier to choose conversation type

        key, response, event = conversation.dictionaries(keyword, songObject, songNote)

        if response is not None:
            self.speak(response)

        return key, event


# Initialisation: PyAudio has a list of warning messages
def initialise():
    # Initialisation: PyAudio has a list of warning messages
    print("{}\n  Initialising... \n{}".format('--' * 20, '--' * 20))
    m = sr.Microphone()
    del m
    print("{}\nInitialisation complete\n{}\n\n".format('--' * 20, '--' * 20))


if __name__ == "__main__":
    initialise()
    voiceAssistant = VoiceAssistant()
    voiceAssistant.speak("Hello there! To talk to me, say Hey Robot.")
    talk = True
    # Start conversation only after user greeting (e.g. "Hey _ _ _ _")
    while (talk):
        data = voiceAssistant.recordAudio()
        if "robot" in data.lower():
            voiceAssistant.speak("Hello! What can I do for you?")
            # Start conversation
            while (talk):
                data = voiceAssistant.recordAudio()
                talk = voiceAssistant.conversationFlow(data)
