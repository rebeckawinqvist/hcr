from voice_assistant import *
from MusicTypes import NoteInfo, Song
from Display import Display
from Note_Recognition import NoteRecognition
from NoteSynthesizer import Synth
from Hands import Hands
import MidiManager
import threading
import time
import os
import queue

NAME_OF_ROBOT = "robot"


def generate_name_list(song=True, lesson=False):
    directory = os.path.dirname(os.path.abspath(__file__))
    if lesson:
        path = os.path.join(directory, "assets/lessons")
    else:
        path = os.path.join(directory, "assets/songs")
    files = os.listdir(path)
    return [file[:-4] for file in files]


class LessonController:

    def __init__(self):
        os.system("amixer -c 1 set Mic 85%")

        self.voice_assistant = VoiceAssistant()

        # ============== Song Object ======================
        self._songObj = None
        self._songNote = None

        # ============== VA Events ========================
        self.event_list = []
        self.repeat = threading.Event()
        self.pause = threading.Event()
        self.stop = threading.Event()
        self.resume = threading.Event()
        self.start = threading.Event()
        self.what_tempo = threading.Event()
        self.name_of_song = threading.Event()
        self.show_finger_pos = threading.Event()
        self.how_to_play = threading.Event()
        self.event_list.extend((self.repeat, self.pause, self.stop, self.resume, self.start, self.show_finger_pos,
                                self.name_of_song, self.what_tempo, self.how_to_play))
        self.event_keys = ["repeat", "pause", "stop", "resume", "start", "finger", "name of", "tempo", "how do I play"]
        self.event_dict = dict(zip(self.event_keys, self.event_list))

        # ============== Display Events ===================
        self.songList = generate_name_list()
        self.lessonList = generate_name_list(lesson=True)

        self.songSelect = threading.Event()
        self.lessonSelect = threading.Event()
        self.backButton = threading.Event()
        self.stepBackButton = threading.Event()
        self.restartButton = threading.Event()
        displayEvents = [self.songSelect, self.lessonSelect, self.backButton, self.stepBackButton, self.restartButton]
        self.display = Display(displayEvents, self.lessonList, self.songList)

        # ============== Note Rec Events ==================
        self.user_note_on = threading.Event()
        self.user_note_off = threading.Event()
        noteRecEvents = [self.user_note_on, self.user_note_off]
        self.NoteRec = NoteRecognition(noteRecEvents)

        # ============== Scoring ==========================
        self.total_score = 0
        self.total_notes = 0
        self.window_score = [0.5, 0.5]

        self.hands = Hands()
        self.synth = Synth()

    def run(self):
        # ============== Create Threads ===================
        self.va_thread = threading.Thread(target=self.va_task, args=())
        self.lc_thread = threading.Thread(target=self.lc_task, args=())
        self.nr_thread = threading.Thread(target=self.nr_task, args=())
        # self.va_thread.start()
        self.lc_thread.start()

        self.nr_thread.start()
        self.display.mainloop()

    # ============== Note Recognition Thread ==============
    def nr_task(self):
        self.NoteRec.run()
        while True:
            time.sleep(0.1)

    # ============== Voice Assistant Thread ===============
    def va_task(self):
        # self.voice_assistant.speak("Hello there! To talk to me, say Hey Robot.")
        name = NAME_OF_ROBOT
        conversation = True
        # Start conversation after user greeting
        while True:
            self.voice_assistant.adjustAmbient()
            self.voice_assistant.speak("Hello there! To talk to me, say Hey Robot.")
            greeting = self.voice_assistant.recordAudio()
            # greeting = "robot"
            if name in greeting.lower():
                self.voice_assistant.speak("How can I help?")
                while (conversation):
                    data = self.voice_assistant.recordAudio()
                    key, event = self.voice_assistant.conversationFlow(data, songObject=self._songObj,
                                                                       songNote=self._songNote)
                    if event:
                        self.event_dict[key].set()

    def speak(self, text):
        self.speak_thread = threading.Thread(target=self.speak_task, args=(text,))
        self.speak_thread.start()

    def speak_task(self, text):
        self.voice_assistant.speak(text)

    # ============== Main LC Thread =======================
    def lc_task(self):
        idle = time.time()
        updateTime = time.time()

        while True:
            currentTime = time.time()
            timeDiff = time.time() - idle
            if timeDiff > 30.0:
                if currentTime - updateTime > 5.0:
                    self.display.update_emoji("sleeping")
                    updateTime = currentTime
            elif timeDiff > 10.0:
                if currentTime - updateTime > 5.0:
                    self.display.update_emoji("thinking")
                    updateTime = currentTime

            if self.lessonSelect.is_set():
                index = self.display.getSelection("LessonPage")
                lesson = MidiManager.loadSong("lessons/%s" % self.lessonList[index])
                self.teach_song(lesson)
                idle = time.time()
            if self.songSelect.is_set():
                index = self.display.getSelection("SongPage")
                song = MidiManager.loadSong("songs/%s" % self.songList[index])

                # Save song object
                self._songObj = song
                self.play_song(song)
                # Reset song object
                self._songObj = None
                idle = time.time()

            if self.pause.is_set():
                print("pause is set")
                self.pause.clear()
            # Do something, call function

            if self.resume.is_set():
                print("resume is set")
                self.resume.clear()

            if self.start.is_set():
                print("start is set")
                self.start.clear()

            if self.show_finger_pos.is_set():
                print("showing finger position")
                self.show_finger_pos.clear()

            if self.how_to_play.is_set():
                self.how_to_play.clear()

    def resetSongEvents(self):
        self.songSelect.clear()
        self.lessonSelect.clear()
        self.user_note_on.clear()
        self.user_note_off.clear()
        self.backButton.clear()
        self.stepBackButton.clear()
        self.restartButton.clear()
        self.total_score = 0
        self.total_notes = 0
        self.window_score = [0.5, 0.5]

    def teach_song(self, song):
        self.resetSongEvents()
        self.display.update_emoji("prep")

        beatTime = song.beatTime()
        index = 0
        exitSong = False
        currentTime = time.time()
        noteTime = 0 
        noteDuration = 0

        displayNotes = song.noteWindow(index)
        self.display.update_music(displayNotes)

        self.synth.render_all_notes(song)
        self.display.update_emoji("cool")

        while index < len(song.noteList) and not exitSong:
            # Set note
            newTime = time.time()
            if newTime - noteTime > noteDuration:
                note = song.noteList[index]
                self._songNote = note.decodeNote()[0]
                displayNotes = song.noteWindow(index)

                self.display.update_music(displayNotes)
                self.hands.actuate_motors(note.note)
                self.synth.play_note(index)

                noteTime = newTime
                noteDuration = note.duration() * beatTime
                index += 1
            # ============== Events =======================
            if self.stop.is_set():
                self.stop.clear()
                exitSong = True
                break
            if self.backButton.is_set():
                self.backButton.clear()
                exitSong = True
                break
            if self.repeat.is_set():
                self.repeat.clear()
                index = index - 1 if (index > 0) else 0
            if self.stepBackButton.is_set():
                self.stepBackButton.clear()
                index = index - 1 if (index > 0) else 0
            if self.restartButton.is_set():
                self.restartButton.clear()
                index = 0

        if not exitSong:
            self.display.musicFinish()
        if exitSong:
            self.display.show_frame("LessonPage")
        self.resetSongEvents()
        print("Song Exit")

    def play_song(self, song):
        self.resetSongEvents()
        self.display.update_emoji("smile_small")

        index = 0
        exitSong = False
        while index < len(song.noteList) and not exitSong:

            target_note = song.noteList[index]
            # Set song note
            self._songNote = target_note.decodeNote()[0]
            displayNotes = song.noteWindow(index)
            self.display.update_music(displayNotes)
            self.hands.actuate_motors(target_note.note)
            # ============== Note Recognition =================
            user_note = 0
            last_user_note = 0
            attempts = 0
            exitNote = False
            while user_note != target_note.note and not exitNote:
                if self.stop.is_set():
                    self.stop.clear()
                    exitSong = True
                    exitNote = True
                    break
                if self.backButton.is_set():
                    self.backButton.clear()
                    exitSong = True
                    exitNote = True
                    break

                if self.repeat.is_set():
                    self.repeat.clear()
                    index = index - 1 if (index > 0) else 0
                    exitNote = True
                    break
                if self.stepBackButton.is_set():
                    self.stepBackButton.clear()
                    index = index - 1 if (index > 0) else 0
                    exitNote = True
                    break
                if self.restartButton.is_set():
                    self.restartButton.clear()
                    index = 0
                    exitNote = True
                    self.total_score = 0
                    break

                if self.user_note_on.is_set():
                    self.display.update_user_note(NoteInfo(self.NoteRec.note, 0, 0))
                    self.user_note_on.clear()

                if self.user_note_off.is_set():
                    self.display.update_user_note(NoteInfo(self.NoteRec.note, 0, 0))

                    if self.NoteRec.duration >= 0.05:
                        print('Note [midi]: ', self.NoteRec.note, '\\Pitch acc [cents]: ', self.NoteRec.pitch,
                              '\\Starttime [Unix]: ', self.NoteRec.start_time, '\\Duration [s]: ',
                              self.NoteRec.duration)
                        last_user_note = user_note
                        user_note = self.NoteRec.note
                    else:
                        print("Short Note")

                    self.NoteRec.note = 0
                    self.user_note_off.clear()

                if last_user_note != user_note:
                    attempts += 1

            print("Note Complete")
            if not exitNote:
                self.score(1.0 / attempts)
                index += 1

        if not exitSong:
            self.score(0, True)
            self.display.musicFinish()
        else:
            self.display.show_frame("SongPage")
        self.resetSongEvents()
        self._songNote = None
        print("Song Exit")

    def score(self, score, finish=False):
        if not finish:
            self.total_score += score
            self.total_notes += 1
            self.window_score.append(score)
            self.window_score.pop(0)

            emojiScore = sum(self.window_score) / len(self.window_score)
        else:
            emojiScore = self.total_score / self.total_notes

        print(emojiScore)
        if emojiScore > 0.7:
            self.display.update_emoji("heart")
        elif emojiScore > 0.5:
            self.display.update_emoji("smile_big")
        elif emojiScore > 0.3:
            self.display.update_emoji("smile_small")
        else:
            self.display.update_emoji("unhappy")

        if finish:
            self.speak("Well done")


if __name__ == "__main__":
    lc = LessonController()
    lc.run()

    print("Exit main thread")
