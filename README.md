# Annotator
Author: Marco Marini, Sheffield, 2020, marco.marini@phd.unipi.it

How to use Annotator:

The Annotator is able to generate a TextGrid file (Praat style) for wav file.
It exploits the KALDI Voice Activity Detector (VAD) to extract tiers of "voice"
and "unvoice". 
For each "voice" tiers the label of the word pronounced is generated.
So the entire program is composed by 2 algorithms. 
 1 - GenerateBoundaries.sh: take in input the speaker code, and generate for
                            a "results" file in which there are stored the 
                            boundaries of voice for each wav file (see .sh 
                            file for more details). Furthermore, it converts
			                      each file in mono-channel, 16kHz sample rate and
			                      16bit codification. All the converted files are
			                      stored 
 2 - Annotator.py: given the code of speaker, parse the "results" file generated
                   by the previous program, and plot the wave signal with all the
                   tiers. 
		   The user can:
			- play the voiced part of file
			- change the boundaries of voice
      - add pre defined tires (see comment at the beginig of Annotator.py)
			- confirm the tiers by clicking "toTextGrid" button
			- skip that file by "Next" button

The software 1 generate a folder (the name is given by user) in which are stored
the files for each user (e.g. ./out/{23, 24, ..} where the numbers are the user code).
All the files that GenerateBoundaries.sh needs to run properly are described within itself. 
The software 2 generate a "textgrid" folder in which are stored all the TextGrid files
for each wav files listed in "results" file.

Example of use: 
"./GenerateBoundaries.sh 26 out" generates out/26 folder that countains all data from Kaldi VAD.
In particolar, in ./out/26/waves you can find all wave files of user 26 converted in 16kHz etc.
Then run "./Annotator.py", give the user code (in this case 26) and it generates a ./out/26/textgrid
that contains all texgrid file generated. Exam: for the file ./out/26/waves/house.wav there is its 
textgrid file associated in ./out/26/textgrid/house.textgrid
