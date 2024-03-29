#!/usr/bin/python3

#-----------------------------------------------------------
# Author: Marco Marini, marco.marini@phd.unipi.it,
# Sheffield, 2020
# ----------------------------------------------------------
# This program helps the user to generate a textGrid file 
# that annotate a wave file. 
# It uses a pre-defined structure of folders that countains 
# all the files that it needs to work properly.
# This structure is generated by GenerateBoundaries.sh script,
# so if do not know it, please lets have a look about it before
# use this program.
# Annotator.py reads wave files one by one and plot them on a 
# GUI interface.
# Furthermore, it show the boundaries of voice and non-voice 
# within the wave form. The user can move these boundaries 
# thanks to the buttons and play the part of wave form selected
# as "Voice".
# By clicking "toTextGrid" button a textGrid file is generated
# for that wave file (the file has the same name of wave one 
# but .textgrid extension). In the textgrid file a single tier
# is genereated with boundaries of "voice" and "non-voice".
# There is also the possibility of insert a pre-define tiers
# in order to add some notes about wave files.
# For example, if the voice is truncated (e.g. insteas of 
# "house" the speaker says "hou"), by checking the "truncated"
# check box, another tier will be added on textGrid file.
# The possible pre-defined tiers are:
#  - Truncated: the speaker speech is truncated because is too
#               close to the beginning or end of record;
#  - Substitution: the speaker pronounced another word
#                 rather than the one proposed on screen;
#  - Repetition: the speaker pronounced more times the same
#                word within wave file;
#  - Corrupted: wave file present some microphone saturation
#               or glitch;
#  - Background noise: the wave file presents some background
#                      noise, like coughing, but the speech 
#                      is still understandable;
#  - Word split: the speaker makes a pause in the middle of
#                the word or tend to pronounce the word in 
#                syllabic way;
#  - General notes: is used to annotate some generic issue
#                   like if the speaker pronounces the word 
#                   longer than usual (e.g. �donnnna� instead 
#                   of �donna�).
# ----------------------------------------------------------

import matplotlib.pyplot as plt
import matplotlib
import wave
matplotlib.use('TkAgg')
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import *
import simpleaudio as sa
import os.path
import textgrid
import contextlib

def findTiers(duration, startV, endV, word):
	# case all is audio
	if (endV-startV)==duration:
		voice = [word, startV, endV]
		return [voice]
	# case voice start from begining
	elif startV==0.0:
		voice = [word, startV, endV]
		sil = ['nonspeech', endV, duration]
		return [voice, sil]
	# case voice is at the end	
	elif endV==duration:
		voice = [word, startV, endV]
		sil = ['nonspeech', 0.0, startV]
		return [sil, voice]
	# case voice is in the middle
	else:
		sil1 = ['nonspeech', 0.0, startV]
		voice = [word, startV, endV]
		sil2 = ['nonspeech', endV, duration]
		return [sil1, voice, sil2]

def playPartOfAudio(path, start, stop):
	wave_read = wave.open(path, 'rb')
	audio_data = wave_read.readframes(wave_read.getnframes())
	num_channels = wave_read.getnchannels()
	bytes_per_sample = wave_read.getsampwidth()
	sample_rate = wave_read.getframerate()

	f = bytes_per_sample*sample_rate
	startSample = int(start*f)
	stopSample = int(stop*f)
	if (stopSample-startSample)%2 == 1:
		stopSample -= 1
	print("buonderies: ["+str(startSample)+" - "+str(stopSample)+"]")
	rec = audio_data[startSample:stopSample]
	play_obj = sa.play_buffer(rec, num_channels, bytes_per_sample, sample_rate)
	play_obj.wait_done()

def addIntTierNotes(textgridFile, duration, notes):
	intTier = textgrid.IntervalTier('notes', maxTime=duration)
	textgridFile.append(intTier)
	intTier.add(0, duration, notes)

def generateTextGridFile(fileDestination, lenFile, listOfTiers, listOfCheckedNotes, substitution, otherNotes):
	# generate a TextGrid
	xmin=0
	numOfTiers = len(listOfTiers)
	duration = lenFile
	# create a Textgrid obbject, name it if required.
	textgridFile = textgrid.TextGrid('out', maxTime=duration)

	# create words tier	
	intTier = textgrid.IntervalTier('words', maxTime=duration)
	# add IntervaTier to textgrid obj
	textgridFile.append(intTier)
	for i in range(numOfTiers):
			tier = listOfTiers[i]
			# adding an interval
			intTier.add(tier[1], tier[2], tier[0])

	# generate other tiers
	for notes in listOfCheckedNotes:
		# generate 'notes' tier
		addIntTierNotes(textgridFile, duration, notes)
		if notes == 'substitution':
			# generate 'pronounced' tier
			intTier = textgrid.IntervalTier('pronounced', maxTime=duration)
			textgridFile.append(intTier)
			for i in range(numOfTiers):
				tier = listOfTiers[i]
				# adding an interval
				if tier[0]!='nonspeech':
					intTier.add(tier[1], tier[2], substitution)
				else:
					intTier.add(tier[1], tier[2], tier[0])	
		elif notes == 'general notes':
			intTier = textgrid.IntervalTier('notes', maxTime=duration)
			textgridFile.append(intTier)
			intTier.add(xmin, duration, otherNotes)

	# generate TextGrid
	textgridFile.write(fileDestination)

def plotAudio(sbplt, fileAudio, audioSignal, startVoice, endVoice, duration, word):
	#fig, ax = plt.subplots()
	sbplt.clear()
	sbplt.set_title(fileAudio)
	print(fileAudio)
	sbplt.plot(audioSignal/10000)
	sbplt.grid()
	sbplt.axis('tight')
	sbplt.set_xlim((0.0, duration))
	print(len(audioSignal))
	print(startVoice)
	print(endVoice)
	tiers = findTiers(duration, startVoice, endVoice, word)
	print(tiers)
	for t in tiers:
		print(t)
		sbplt.axvline(x=float(t[1]), color='red')
		sbplt.axvline(x=float(t[2]), color='red')
		if t[0]==word:
			col = 'red'
		else:
			col = 'green'
		sbplt.axvspan(float(t[1]), float(t[2]), facecolor=col, alpha=0.5, label=t[0], picker=True)
	sbplt.legend();
			
# open file results
def parseResultsFile(user):
	path = './out/'+str(user)+'/results'
	with open(path) as f:
		lines = f.readlines();
		waveFiles = []
		#print(lines);
		for l in lines:
			infoRec = l.split()
			waveFiles +=  [infoRec]
		return waveFiles

# generate waveFile list in case of results file is not present
def genWaveFileList(pathFolder):
	filesList = os.listdir(pathFolder)
	waveFiles = []
	for l in filesList:
		fname = pathFolder+'/'+l
		with contextlib.closing(wave.open(fname,'r')) as f:
			frames = f.getnframes()
			rate = f.getframerate()
			duration = frames / float(rate)
			#print(duration)
			waveFiles += [[fname, 0.0, 0.0, duration, '']]
	return waveFiles

# control if a file has a TextGrid files
def hasTextGrid(waveFile):
	textgridFiletmp = waveFile.replace('waves','textgrid')
	textgridFiletmp = textgridFiletmp.replace('wav','TextGrid') 
	return os.path.exists(textgridFiletmp)

# control if a file has a TextGrid files in the same folder
def hasTextGridSameFolder(waveFile):
	textgridFiletmp = waveFile.replace('wav','TextGrid') 
	return os.path.exists(textgridFiletmp)

class Application(Frame):
	def getWaveFilesList(self):
		# annotation without user code
		if self.user==-1:
			self.waveFilesList = genWaveFileList(self.pathFolderRec)
		else:
			self.waveFilesList = parseResultsFile(self.user);
		
		self.indexTrack = 0
		self.infoTrack = self.waveFilesList[self.indexTrack]

		if self.user==-1:
			if hasTextGridSameFolder(self.infoTrack[0]):
				self.nextTrack()
		else:
			if hasTextGrid(self.infoTrack[0]):
				self.nextTrack()
		#self.updateScales()
		print(self.infoTrack)
		self.scaleStartVoice["to"] = float(self.infoTrack[3])
		self.scaleEndVoice["to"] = float(self.infoTrack[3])
		self.drawGraph()

	def updateWord(self):
		self.infoTrack[4] = self.wordEntry.get()
		self.drawGraph()

	def drawGraph(self):
		with wave.open(self.infoTrack[0]) as audioFile:
			signal = audioFile.readframes(-1)
			signal = np.fromstring(signal, 'Int16')
			print("infoTrack: "+str(self.infoTrack))
			startVoice = float(self.infoTrack[1])*audioFile.getsampwidth()*audioFile.getframerate()/2
			endVoice = float(self.infoTrack[2])*audioFile.getsampwidth()*audioFile.getframerate()/2
			duration = float(self.infoTrack[3])*audioFile.getsampwidth()*audioFile.getframerate()/2
			print("len of signal "+str(len(signal)))
			print("start = "+str(startVoice))
			print("end = "+str(endVoice))
			print("duration = "+str(duration))
			self.sbplt.clear()
			#if self.user==-1:
			#	self.infoTrack[4] = self.wordEntry.get()
			plotAudio(self.sbplt, self.infoTrack[0], signal, startVoice, endVoice, duration, self.infoTrack[4])
			self.canvas.get_tk_widget().pack()
			self.canvas.draw()
			self.scaleStartVoice["to"] = float(self.infoTrack[3])
			self.scaleEndVoice["to"] = float(self.infoTrack[3])
		
	def nextTrack(self):
		# control if the file has file TextGrid already exist
		while True:
			# reset all checkBox
			for note in self.listCheckBox:
				note[0].set(0)
			self.cleanEntryRealWord()
			self.cleanEntryGeneralNotes()
			self.indexTrack += 1
			if self.indexTrack<len(self.waveFilesList):
				self.infoTrack = self.waveFilesList[self.indexTrack]
				haveNotTG = False
				if self.user==-1:
					if not(hasTextGridSameFolder(self.infoTrack[0])):
						haveNotTG = True
				else:
					if not(hasTextGrid(self.infoTrack[0])):
						haveNotTG = True
				if haveNotTG:	
					print('Next track: '+self.infoTrack[0])
					self.startVoice.set(self.infoTrack[1])
					self.endVoice.set(self.infoTrack[2])
					self.drawGraph()
					break
			else:
				print("Procedure completed")
				#self.quit()
				self.closeWindow()
				break

	def updateStartVoice(self, position):
		self.infoTrack[1] = self.startVoice.get()
		self.drawGraph()

	def updateEndVoice(self, position):
		self.infoTrack[2] = self.endVoice.get()
		self.drawGraph()

	def decreaseStartVoice(self):
		tmp = float(self.infoTrack[1])
		tmp -= 0.01
		if tmp<0.0:
			tmp = 0.0
		self.infoTrack[1] = str(tmp)
		self.startVoice.set(self.infoTrack[1])
		self.drawGraph()

	def increaseStartVoice(self):
		tmp = float(self.infoTrack[1])
		tmp += 0.01
		if tmp>float(self.infoTrack[3]):
			tmp = float(self.infoTrack[3])
		self.infoTrack[1] = str(tmp)
		self.startVoice.set(self.infoTrack[1])
		self.drawGraph()

	def decreaseEndVoice(self):
		tmp = float(self.infoTrack[2])
		tmp -= 0.01
		if tmp<0.0:
			tmp = 0.0
		self.infoTrack[2] = str(tmp)
		self.endVoice.set(self.infoTrack[2])
		self.drawGraph()

	def increaseEndVoice(self):
		tmp = float(self.infoTrack[2])
		tmp += 0.01
		if tmp>float(self.infoTrack[3]):
			tmp = float(self.infoTrack[3])
		self.infoTrack[2] = str(tmp)
		self.endVoice.set(self.infoTrack[2])
		self.drawGraph()

	def genTextGrid(self):
		dest = self.infoTrack[0]
		if self.user!=-1:
			dest = dest.replace('waves','textgrid')
		dest = dest.replace('wav','TextGrid')
		tiers = findTiers(float(self.infoTrack[3]), float(self.infoTrack[1]), float(self.infoTrack[2]), self.infoTrack[4])
		# retrive all the notes checkBox checked
		notesList = []
		for note in self.listCheckBox:
			if note[0].get()==1:
				notesList += [note[1]] 
		generateTextGridFile(dest, float(self.infoTrack[3]), tiers, notesList, self.realWordEntry.get(), self.notesEntry.get())
		# control if the file has been generated
		if self.user == -1:
			if hasTextGridSameFolder(self.infoTrack[0]):
				self.nextTrack()
				self.playAudio()
		else:
			if hasTextGrid(self.infoTrack[0]):
				self.nextTrack()
				self.playAudio()
	
	def playAudio(self):
		print("Play")
		playPartOfAudio(self.infoTrack[0], float(self.infoTrack[1]), float(self.infoTrack[2]))
		
	def cleanEntryRealWord(self):
		#if self.checkSubstitution.get()==1:
		self.realWordEntry.set("")
			
	def cleanEntryGeneralNotes(self):
		#if self.checkNotes.get()==1:
		self.notesEntry.set("")		

	def __init__(self, master, selectUser, pathFolder):
		Frame.__init__(self, master)
		self.window = master
		self.user = selectUser
		self.pathFolderRec = pathFolder
		self.createWidgets()
		self.getWaveFilesList()
		self.pack()
	
	def closeWindow(self):
		self.master.destroy()

	def createWidgets(self):
		self.waveFig = Figure(figsize=(10,4))
		self.sbplt = self.waveFig.add_subplot(111)
		self.canvas = FigureCanvasTkAgg(self.waveFig, master=self.window)
		#self.drawGraph()

		self.startVoice = StringVar()
		self.scaleStartVoice = Scale(self, variable=self.startVoice, orient=HORIZONTAL, showvalue=0, resolution=0.01)
		self.scaleStartVoice["command"] = self.updateStartVoice
		self.scaleStartVoice.grid(row=2, column=4, columnspan=2, sticky=W+E)

		self.endVoice = StringVar()
		self.scaleEndVoice = Scale(self, variable=self.endVoice, orient=HORIZONTAL, showvalue=0, resolution=0.01)
		self.scaleEndVoice["command"] = self.updateEndVoice
		self.scaleEndVoice.grid(row=3, column=4, columnspan=2, sticky=W+E)
	
		self.QUIT = Button(self)
		self.QUIT["text"] = "QUIT"
		self.QUIT["fg"]   = "red"
		self.QUIT["command"] =  self.closeWindow
		self.QUIT.grid(row=0,column=0)

		self.play = Button(self)
		self.play["text"] = "Play",
		self.play["command"] = self.playAudio
		self.play.grid(row=0,column=2)

		self.next = Button(self)
		self.next["text"] = "Next",
		self.next["command"] = self.nextTrack
		self.next.grid(row=0,column=4)

		self.xminLabel = Label(self)
		self.xminLabel["text"] = "Start"
		self.xminLabel.grid(row=2,column=0)

		self.decXmin = Button(self)
		self.decXmin["text"] = "-",
		self.decXmin["command"] = self.decreaseStartVoice
		self.decXmin.grid(row=2,column=1)

		self.xmin = Entry(self, textvariable=self.startVoice)
		#self.startVoice.set(self.infoTrack[1])
		self.xmin.grid(row=2,column=2)

		self.incXmin = Button(self)
		self.incXmin["text"] = "+",
		self.incXmin["command"] = self.increaseStartVoice
		self.incXmin.grid(row=2,column=3)

		self.xmaxLabel = Label(self)
		self.xmaxLabel["text"] = "Stop"
		self.xmaxLabel.grid(row=3,column=0)

		self.decXmax = Button(self)
		self.decXmax["text"] = "-",
		self.decXmax["command"] = self.decreaseEndVoice
		self.decXmax.grid(row=3,column=1)

		self.xmax = Entry(self, textvariable=self.endVoice)
		#self.endVoice.set(self.infoTrack[2])
		self.xmax.grid(row=3,column=2)

		self.incXmax = Button(self)
		self.incXmax["text"] = "+",
		self.incXmax["command"] = self.increaseEndVoice
		self.incXmax.grid(row=3,column=3)

		self.toTextGrid = Button(self)
		self.toTextGrid["text"] = "toTextGrid",
		self.toTextGrid["command"] = self.genTextGrid
		self.toTextGrid.grid(row=0,column=5)
		
		self.listCheckBox = []

		self.truncatedCheck = IntVar()
		self.checkTruncated = Checkbutton(self, text="truncated", variable=self.truncatedCheck).grid(row=4, column=0, columnspan=2, sticky=W)
		self.listCheckBox += [[self.truncatedCheck, 'truncated']]
		
		self.substitutionCheck = IntVar()
		self.checkSubstitution = Checkbutton(self, text="substitution", variable=self.substitutionCheck, command=self.cleanEntryRealWord).grid(row=5, column=0, columnspan=2, sticky=W)
		self.listCheckBox += [[self.substitutionCheck, "substitution"]]
		#self.checkSubstitution["command"] = self.cleanEntryRealWord
		
		self.realWordEntry = StringVar()
		self.entryRealWord = Entry(self, textvariable=self.realWordEntry).grid(row=5, column=2, columnspan=2, sticky=W)

		self.repetitionCheck = IntVar()
		self.checkRepetition = Checkbutton(self, text="repetition", variable=self.repetitionCheck).grid(row=6, column=0, columnspan=2, sticky=W)
		self.listCheckBox += [[self.repetitionCheck, "repetition"]]
		
		self.corruptedCheck = IntVar()
		self.checkCorrupted = Checkbutton(self, text="corrupted", variable=self.corruptedCheck).grid(row=7, column=0, columnspan=2, sticky=W)
		self.listCheckBox += [[self.corruptedCheck, 'corrupted']]
		
		self.backgroundCheck = IntVar()
		self.checkBackground = Checkbutton(self, text="background noise", variable=self.backgroundCheck).grid(row=8, column=0, columnspan=2, sticky=W)
		self.listCheckBox += [[self.backgroundCheck, 'background noise']]
		
		self.notUsableCheck = IntVar()
		self.checkNotUsable = Checkbutton(self, text="not usable", variable=self.notUsableCheck).grid(row=9, column=0, columnspan=2, sticky=W)
		self.listCheckBox += [[self.notUsableCheck, "not usable"]]
		
		self.splittedCheck = IntVar()
		self.checkSplitted = Checkbutton(self, text="word splitted", variable=self.splittedCheck).grid(row=10, column=0, columnspan=2, sticky=W)
		self.listCheckBox += [[self.splittedCheck, "word splitted"]]
		
		self.notesCheck = IntVar()
		self.checkNotes = Checkbutton(self, text="general notes", variable=self.notesCheck, command=self.cleanEntryGeneralNotes).grid(row=11, column=0, columnspan=2, sticky=W)
		self.listCheckBox += [[self.notesCheck, "general notes"]]
		#self.checkNotes["command"] = self.cleanEntryGeneralNotes
		
		self.notesEntry = StringVar()
		self.entryNotes = Entry(self, textvariable=self.notesEntry).grid(row=11, column=2, columnspan=3, sticky=W)

		if self.user == -1:
			self.wordEntry = StringVar()
			self.wordEntry.trace("w", lambda name, index, mode, sv=self.wordEntry: self.updateWord())
			self.entryWord = Entry(self, textvariable=self.wordEntry).grid(row=2, column=6, columnspan=2, sticky=W)
			self.wordLable = Label(self, text='Insert word pronounced: ').grid(row=0, column=6, columnspan=2, sticky=W)


class selectUser:
	def __init__(self, master):
		self.master = master
		#self.master.geometry("400x400")
		self.frame = Frame(self.master)
		self.insertComponet()
		#self.butnew("ok", "2", Win2)
		self.frame.pack()

	def insertComponet(self):
		lbl = Label(self.frame, text = "Insert user code:").grid(row=0,column=0)
		self.usr = IntVar()
		self.usrEntry = Entry(self.frame, textvariable=self.usr).grid(row=1,column=0)
		Button(self.frame, text = "Ok", command= self.new_window_usr).grid(row=2,column=0)

		lbl = Label(self.frame, text = "or the rec files folder path:").grid(row=3,column=0)
		self.recFolderPath = StringVar()
		self.folderPathEntry = Entry(self.frame, textvariable=self.recFolderPath).grid(row=4,column=0)
		Button(self.frame, text = "Use folder path", command= self.new_window_folder).grid(row=5,column=0)
 
	def new_window_usr(self):
		usr = self.usr.get()
		print(usr)
		self.new = Toplevel(self.master)
		Application(self.new, usr, '')

	def new_window_folder(self):
		pathF = self.recFolderPath.get()
		self.new = Toplevel(self.master)
		Application(self.new, -1, pathF)

root = Tk()
app = selectUser(root)
root.mainloop()
root.destroy()