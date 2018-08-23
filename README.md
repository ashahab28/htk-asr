Pre-process
----------------

1. HParse gram wordnet // Create the language model (Grammar)
2. Creating the dictionary using: HDMan -m -w wlist -n monophones1 -l dlog dict beep names
3. Record the data. Check the grammar and dict : HSGen -l -n 200 wdnet dict > testprompts
4. Create the label
		perl prompts2mlf words.mlf {word level MLF}
		HLEd -l ’*’ -d dict -i phones0.mlf mkphones0.led word.mlf {phone level MLF}

		phones0.mlf => label for each utterance in the phoneme format. This format deletes silence(sp) from the prompts
5. Extract the mfcc feature with HTK
		create the config file with MFCC_0_D_A {}
		HCopy -T 1 -C config -S codetr.scp
6. Build the monophone HMM
   HCompV -C config -f 0.01 -m -S train.scp -M hmm0 proto
   HERest -C config -I ../pre-process_feature-extraction/phones0.mlf -t 250.0 150.0 1000.0 -S train.scp -H hmm0/macros -H hmm0/hmmdefs -M hmm1 ../pre-process_feature-extraction/monophones1

   Run HEREst twice more with -H as input and -M as output
   Output: hmm2 & hmm3
7. Add sp model in hmm4
	HHEd -H hmm4/macros -H hmm4/hmmdefs -M hmm5 sil.hed monophones1

	>new monophones in train directory: because added sp

	Run HEREst twice more with (added sp)
	HERest -C config -I phones1.mlf -t 250.0 150.0 1000.0 -S train.scp -H hmm5/macros -H hmm5/hmmdefs -M hmm6 monophones1
	output: hmm6 & hmm7
8. Realigning the training data
	Add 'silence sil' in the new dict

    HVite -l ’*’ -o SWT -b silence -C config -a -H hmm7/macros \
	  -H hmm7/hmmdefs -i aligned.mlf -m -t 250.0 -y lab \
	  -I word.mlf -S train.scp  dict monophones1

	Run HEREst twice more
	HERest -C config -I aligned.mlf -t 250.0 150.0 1000.0 -S train.scp -H hmm7/macros -H hmm7/hmmdefs -M hmm8 monophones1

9. Making triphones from monophone
	Create the latter
		HLEd -n triphones1 -l ’*’ -i wintri.mlf mktri.led aligned.mlf
	Cloning of the model
		HHEd -B -H hmm9/macros -H hmm9/hmmdefs -M hmm10	mktri.hed monophones1
		but first we generate mktri using: perl maketrihed monophones1 mktri.hed
	Normal HERest to get hmm11/
		HERest -C config -I wintri.mlf -t 250.0 150.0 1000.0 -S train.scp -H hmm10/macros -H hmm10/hmmdefs -M hmm11 triphones1
	Re-estimation the model using wintri
		HERest -B -C config -I wintri.mlf -t 250.0 150.0 1000.0 -s stats \
		    -S train.scp -H hmm11/macros -H hmm11/hmmdefs -M hmm12 triphones1

10. Making tied-states triphones
	grep "[jq]\|zh\|th\|aw\|ax\|en\|dh|ng|zh" bigdict.txt > bigdict2.txt;	
	Decision tree state tying
	HDMan -b sp -n fulllist -g global.ded -l flog beep-tri beep

	HHEd -B -H hmm12/macros -H hmm12/hmmdefs -M hmm13 \
        tree.hed triphones1 > log

    HERest twice with tiedlist!
    HERest -C config -I wintri.mlf -t 250.0 150.0 1000.0 -S train.scp -H hmm13/macros -H hmm13/hmmdefs -M hmm14 tiedlist

11. Evaluation
HVite -H hmm15/macros -H hmm15/hmmdefs -S test.scp \
          -l ’*’ -i recout.mlf -w wdnet \
          -p 0.0 -s 5.0 dict tiedlist
HResults -I testref.mlf tiedlist recout.mlf

Running live:

HVite -H hmm15/macros -H hmm15/hmmdefs -C config_live -w ../pre-process_feature-extraction/wordnet -p 0.0 -s 5.0 dict tiedlist
