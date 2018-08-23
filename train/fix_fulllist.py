flist = []
for line in open('fulllist'):
	flist.append(line.strip())
trilist = []
for line in open('triphones1'):
	trilist.append(line.strip())

for tri in trilist:
	if not(tri in flist):
		print tri
