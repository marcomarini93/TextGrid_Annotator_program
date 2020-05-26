#!/bin/bash

#-----------------------------------------------------------
# Author: Marco Marini, marco.marini@phd.unipi.it,
# Sheffield, 2020
# ----------------------------------------------------------
# The best structure for this script is:
# database/disease/{male,female}/speaker/single/words/*.wav
# where: 
# 	disease = name of disease
#	speaker = name or code of speaker
#	words   = each folder has the name of word pronounced
#
# Example of execution
# ./GenerateBoundaries.sh 26 out
# The program generates the folder "./out" in which will be stored
# all the file needed for Annotator.py program
#
# Link needed:
#  - sid: $(KALDI_ROOT)/egs/callhome_diarization/v2/sid
#  - diarization: $KALDI_ROOT/egs/callhome_diarization/v2/diarization
#  - steps: $(KALDI_ROOT)/egs/wsj/s5/steps
#  - utils: $(KALDI_ROOT)/egs/wsj/s5/utils
# You need also all the files within conf folder
#
# NB: in order to tune better the VAD response, it could be
# useful play a little bit with ./conf/vad.conf file.
# Specially, the "--vad-energy-threshold" parameter is very
# important. If you set it lower the VAD tends to select
# more noise as a voice, on the other hand if you set it
# higher, VAD become more selective. 
# ---------------------------------------------------------

if [[ $1 && $2 && $3 && $4 ]]; then
	speaker=$1
	database=$2
	out_dir=$3
	out_spk=$out_dir/$speaker
	out_wav=$out_spk/waves
	out_textgrid=$out_spk/textgrid
	KALDI_ROOT=$4

	# make out put dir ready ..
	mkdir -p $out_dir $out_spk $out_wav $out_textgrid

	sh path.sh

	# make links
	ln -s -f $KALDI_ROOT/egs/callhome_diarization/v2/sid
	ln -s -f $KALDI_ROOT/egs/callhome_diarization/v2/diarization
	ln -s -f $KALDI_ROOT/egs/wsj/s5/steps
	ln -s -f $KALDI_ROOT/egs/wsj/s5/utils

	# modify all the file as mono and rate 16kHz
	for x in $database/*/*/$speaker/single/*/*.wav; do 
		sox $x -c 1 -b 16 -t wav -r 16000 $out_wav/$(basename $x)
	done
	

	for x in $database/*/*/$speaker/single/*/*.wav; do echo $x;done > $out_spk/wav.names

	awk -v s="$speaker" '{k=split($1,a,"/");gsub(".wav","",a[k]);print s"_"a[k], a[k-1]}'  $out_spk/wav.names > $out_spk/text

	head $out_spk/text

	awk '{split($1,a,"_");print $1,a[1]}' $out_spk/text > $out_spk/utt2spk

	head $out_spk/utt2spk

	awk -v s="$speaker" -v ow="$out_wav" '{k=split($1,a,"/");gsub(".wav","",a[k]);uid=s"_"a[k];print uid, ow"/"a[k]".wav"}' $out_spk/wav.names > $out_spk/wav.scp
	
	head $out_spk/wav.scp

	utils/fix_data_dir.sh $out_spk

	# use kaldi to extract the feature
	mkdir -p $out_spk/data
	steps/make_mfcc.sh --nj 10 $out_spk  $out_spk/data/make_mfcc  $out_spk/data/mfcc

	sid/compute_vad_decision.sh --nj 1 $out_spk  $out_spk/data/make_vad  $out_spk/data/vad

	diarization/vad_to_segments.sh --nj 1 $out_spk $out_spk/segmentation

	awk '{ if($2 in s==0) s[$2]=$3; e[$2] = $4;
	}
	END{ for(x in s) print x,s[x],e[x];		
	}' $out_spk/segmentation/segments | sort > $out_spk/vad_boud
	
	while IFS= read -r wav_file
	do 
	 	duration=`sox $wav_file -n stat 2>&1 | sed -n 's#^Length (seconds):[^0-9]*\([0-9.]*\)$#\1#p'`
		name=`echo $wav_file | awk -v s="$speaker" '{k=split($1,a,"/");gsub(".wav","",a[k]);print s"_"a[k]}'`
		echo "${out_wav}/$(basename $wav_file) $name $duration"
	done < $out_spk/wav.names > $out_spk/durations

	awk 'NR==FNR{d[$2]=$3;p[$2]=$1;next}{split($1,a,"_");w=a[2];print p[$1],$2,$3,d[$1],w}' $out_spk/durations $out_spk/vad_boud > $out_spk/results

else
	echo "usage $0 <speaker> <main_database> <output_dir> <KALDI_ROOT>"
	echo "e.g. $0 ..."
fi
