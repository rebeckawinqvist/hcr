import random
import speech_recognition as sr
import pyaudio
import datetime
import time
import os
from gtts import gTTS

NO_SONG = "You are not playing a song at the moment."

class song_Obj:
	def __init__(self):
		self._name = '!.!.'
		self._tempo = 1000000

	@property
	def name(self):
		return self._name
	@property
	def tempo(self):
		return self._tempo

def dictionaries(keyword, songObject, request = None):

	songObject1 = songObject
	if songObject1 is None:
		songObject1 = song_Obj()
	else:
		print(songObject.name)
	name123 = "Student"

	
	instructions = {
		"repeat": "Repeating song {}".format(songObject1.name),
		"stop": "Lesson stopped.",
		"pause": "Lesson paused.",
		"resume": "Resuming lesson.",
		"start": "Starting lesson.",
		#"speed up": "Speeding up.",
		#"slow down": "Slowing down.",
		"how do I play": "This is how you play {}".format(request) if request is not None else NO_SONG,
		"finger": "This is how you place your finger for note {}".format(request) if request is not None else NO_SONG,
		"tempo": "The tempo is {}".format(int(songObject1.tempo)) if songObject1.name !='!.!.' else NO_SONG,
		"name of": "This piece is called {}".format(songObject1.name) if songObject1.name !='!.!.' else NO_SONG
	}

	casualConversation = {
		# init - start conversation
		"init": ["Hello! What's your name?"],

		# Hi and Bye 
		# multiple sentences cause fun, randomizing what sentences is returned
		"greeting": ["Hi, {}! How are you? My name is Instru-Mentor and I'm going to be your recorder tutor".format(name123), 
					 "Nice to meet you, {}. Are you ready to play some tunes?".format(name123)],
		"how are you": "I'm good thanks. And ready for some music playing!",
		"what do you do": "I am a music tutor. At the moment, I teach the recorder.",
		"who are you": "My name is Instru-Mentor. I am a music tutor. At the moment, I teach the recorder",
		"what's your name": "My name is Instru-Mentor",
		"bye": ["Goodbye {}! Keep practising.".format(name123), 
				"See you later, {}!".format(name123)],

		# Small-talk
		"mood": ["I'm fine, thank you!", 
				 "Excited to play some tunes!"],
		"birth": ["I was born in 2018 at Imperial College."], 
		"joke": ["Why did the chicken cross the road? To get to the other side."],
		"trivia": ["Did you know that the recorder is first documented in Europe in the Middle Ages?",
				   "Did you know that Vivaldi has written for the recorder?"],

	}

	evaluation = {
		"rate": "How did you like the song?",
		"difficulty": "How difficult did you find the song?",
		"recommend": "Would you recommend this to a friend?"
	}

	for e in [instructions, casualConversation, evaluation]:
		for key in e:
			if key in keyword:
				if isinstance(e[key], list):
					return key, random.choice(e[key]), False
				elif key in instructions:
					return key, e[key], True
				else:
					return key, e[key], False
	return None, None, False

'''
def instructions(instruction, songObject = song_Obj(), request = ""):
	"""
		instruction: instruction
		songObject: current song being practised
		request: requsted from student. e.g. if student asks "How to play ___" request
				  would be a note 	
	"""
	for e in instructions:
		if e in instruction:
			return True, instructions[e]
	
	return False, None


def casualConversation(keyword, name = ""):
	"""
		keyword: keyword specifying type of convo, key in dictionary
		name: name of student
		Returns string to be said by robot
	"""
	try:
		return True, random.choice(casualConversation[keyword])

	except KeyError:
		return False, None


def inLesson(question, song, reqNote = "", spec = ""):
	# question act as key to dictionary. For example "What is the name of this piece?" -> "nameOf"
	# reqNote - specific note the student wants to learn "how do I play ___?"
	# spec - specific question, like "what does ___ mean? (piano, forte, crescendo etc)"

	# here for clarification, remove later
	
	tempo = song.tempo
	name = song.name
	#note = song._note
	#key = song.key
	#diff = song.diff
	


	# please rephrase if it sounds weird
	# don't know yet how to solve the more specific questions. Might need
	# if-statement for that 



def feedback(playedNote, actualNote, name = ""):
	""" 
	Gives the student feedback. Returns a feeback-string.
	playedNote: note the student played
	actualNote: note the student was asked to play 
	"""

	correct = (playedNote == actualNote)
	feedbackDictionary = {
		True: ["Well done, {}!".format(name),
			   "Good job!",
			   "Keep up the good work!"],
		False: ["Wrong note. You played {} instead of {}. Try again!".format(playedNote, actualNote),
				"Almost. Try again!"]
	}

	return random.choice(feedbackDictionary[correct])


def evaluation(keyword, songObject):
	return evaluation[keyword]

'''

# just using to test stuff right now, remove later
if __name__ == "__main__":
	string = feedback("a", "a", "Rebecka")
	print(string)