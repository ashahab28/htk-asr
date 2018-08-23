# Ganti i = 1 sesuai dengan format di hmm0/proto
for phoneme in open("../pre-process_feature-extraction/monophones1"):
	phoneme = phoneme.strip()
	i = 1
	for line in open("hmm0/proto"):
		line = line.strip()
		if(i == 1):
			print "~h \"" + phoneme + "\""
		else:
			print line	
		i += 1
