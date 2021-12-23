#!/usr/bin/env python

import sys

from argparse import ArgumentParser

parser = ArgumentParser()

parser.add_argument("-i", "--input", dest="input_file",
                    help="input Music Maiancs DXF", metavar="FILE")	
parser.add_argument("-o", "--output", dest="output_file",
					help="destination text file with asm code", metavar="FILE")
parser.add_argument("-GI20", "--twenty",
                    action="store_true", dest="GI20", default=False,
                    help="Convert for GI20 format instead of GI30F")

args = parser.parse_args()

					
if args.input_file==None:
	print "No Input file specified!  Exiting..."
	sys.exit()
	
input_file=args.input_file
	
if args.output_file==None:
	print "No output file name specified, using input file name"
	output_file = input_file[:-4]
	output_file=output_file+".mbc"
	print output_file
else:
	output_file=args.output_file

StripName=output_file+"(converted dxf)"

FoundNotes=0
LastNoteTime=0
xlist=[]
ylist=[]
EnglishToMetricScalar=25.4

DXF2MBCTSlope=0.06232163 #formula to convert DXF note values to MBC note values
DXF2MBCTIntercept=-0.61735808

DXF2MBCNSlope=0.49857305 #formula to convert DXF time values to MBC time values
DXF2MBCNIntercept=-2.84934498

DXF2MBCT20Slope=1.06311
DXF2MBCT20Intercept=-0.4146

DXF2MBC20NSlope=8.50492
DXF2MBC20NIntercept=-1.91361

with open(input_file, 'r') as f: #search for .txt file and import all into an array, separated by each line
	Lines = f.read().splitlines()	

LineCount=len(Lines) #find total length of the file
print "File has",LineCount,"total lines"

print "Searching for note data..."

for n in range(LineCount): #each note occurrs as a "CIRCLE" object in the DXF.  Load in position data every time the script finds the text "CIRCLE"
	CurRowString=Lines[n]
	if CurRowString=="CIRCLE":
		FoundNotes=FoundNotes+1
		xlist.append(Lines[n+4])
		ylist.append(Lines[n+6])

		
print "Found a total of",FoundNotes,"notes"

w, h = 2, len(xlist) #Declares an array, 2 wide (note and time), and as many rows as there are notes
notearray = [[0 for x in range(w)] for y in range(h)]

if args.GI20==0:

	for n in range(len(xlist)): #Loads array, and first converts inches to mm, then uses the formulas to convert to MBC note position (0-29) and time values
		notearray[n][0]=round((float(xlist[n])*EnglishToMetricScalar*DXF2MBCTSlope+DXF2MBCTIntercept),4)
		notearray[n][1]=int(float(ylist[n])*EnglishToMetricScalar*DXF2MBCNSlope+DXF2MBCNIntercept)
		if notearray[n][0]>LastNoteTime:
			LastNoteTime=notearray[n][0]
		

	notearray.sort(key=lambda x: x[0]) #sorts array from first note to last, since they aren't always in order in the DXF
	print "sorted notearray is:", notearray
	print len(notearray)

	LastNoteTime=LastNoteTime+5 #adds an arbitrary amount of time to the end of the strip, just for whitespace
	print "LastNoteTime is:",LastNoteTime

	#information that's contained in the header of the MBC file. "\n" means newline
	dxfheader_string="FileVersion=1.0\nPlaybackSpeed=1\nnoteTextureIndex=0\nStripName=XXX\nStripCredits=\nStripContact=\nStripInfo=\nDoLoopPublish=1\nAllowEditingPublish=0\nAutoPlayPublish=1\nstripSize=30\nstripLength=YYY\nNoteCount=ZZZ"
		
	dxfheader_string=dxfheader_string.replace("XXX",str(StripName)) #replace value for Name
	dxfheader_string=dxfheader_string.replace("YYY",str(LastNoteTime)) #replace value for strip length
	dxfheader_string=dxfheader_string.replace("ZZZ",str(FoundNotes)) #replace value for total notes


	#declar mbc_data list
	mbc_data_out=[]

	for n in range(FoundNotes): #scan through the array from earlier and start populating the list
		mbc_data_out.append("p="+str(notearray[n][1]))
		mbc_data_out.append("t="+str(('{0:.4f}'.format(abs(notearray[n][0])))))  #converts float to string with 4 trailing decimal places
		mbc_data_out.append("v=1")
		mbc_data_out.append("s=0")
		mbc_data_out.append("a=1")
		mbc_data_out.append("i=0")
		
	#declar final mbc container
	mbc_out=[]
	mbc_out.append(dxfheader_string) #first add in header
	mbc_out=mbc_out + mbc_data_out #then add in the data

	#write total mbc_out to a file
	with open(output_file, 'w') as f:
				for item in mbc_out:
					print >> f, item
					
	print "Conversion complete!  Data written to",output_file


if args.GI20==1:

	for n in range(len(xlist)): #Loads array, and first converts inches to mm, then uses the formulas to convert to MBC note position (0-29) and time values
		notearray[n][0]=round((float(xlist[n])*DXF2MBCT20Slope+DXF2MBCT20Intercept),4)
		notearray[n][1]=int(round((float(ylist[n])*DXF2MBC20NSlope+DXF2MBC20NIntercept)))
		if notearray[n][0]>LastNoteTime:
			LastNoteTime=notearray[n][0]

		ReinterpretedNote=notearray[n][1]
		if ReinterpretedNote==0:
			notearray[n][1]=0
		elif ReinterpretedNote==1:
			notearray[n][1]=2
		elif ReinterpretedNote==2:
			notearray[n][1]=4
		elif ReinterpretedNote==3:
			notearray[n][1]=5
		elif ReinterpretedNote==4:
			notearray[n][1]=7
		elif ReinterpretedNote==5:
			notearray[n][1]=9
		elif ReinterpretedNote==6:
			notearray[n][1]=11
		elif ReinterpretedNote==7:
			notearray[n][1]=12
		elif ReinterpretedNote==8:
			notearray[n][1]=14
		elif ReinterpretedNote==9:
			notearray[n][1]=16
		elif ReinterpretedNote==10:
			notearray[n][1]=17
		elif ReinterpretedNote==11:
			notearray[n][1]=19
		elif ReinterpretedNote==12:
			notearray[n][1]=21
		elif ReinterpretedNote==13:
			notearray[n][1]=23
		elif ReinterpretedNote==14:
			notearray[n][1]=24
		elif ReinterpretedNote==15:
			notearray[n][1]=26
		elif ReinterpretedNote==16:
			notearray[n][1]=28
		elif ReinterpretedNote==17:
			notearray[n][1]=29
		elif ReinterpretedNote==18:
			notearray[n][1]=31
		elif ReinterpretedNote==19:
			notearray[n][1]=33
		else:
			print "Oh god you shouldn't see this, something went wrong"
			print "Note was:", notearray[n][1]
			sys.exit()

	notearray.sort(key=lambda x: x[0]) #sorts array from first note to last, since they aren't always in order in the DXF
	print "sorted notearray is:", notearray
	print len(notearray)

	LastNoteTime=LastNoteTime+5 #adds an arbitrary amount of time to the end of the strip, just for whitespace
	print "LastNoteTime is:",LastNoteTime

	#information that's contained in the header of the MBC file. "\n" means newline
	dxfheader_string="FileVersion=1.0\nPlaybackSpeed=1\nnoteTextureIndex=0\nStripName=XXX\nStripCredits=\nStripContact=\nStripInfo=\nDoLoopPublish=1\nAllowEditingPublish=0\nAutoPlayPublish=1\nstripSize=20\nstripLength=YYY\nNoteCount=ZZZ"
		
	dxfheader_string=dxfheader_string.replace("XXX",str(StripName)) #replace value for Name
	dxfheader_string=dxfheader_string.replace("YYY",str(LastNoteTime)) #replace value for strip length
	dxfheader_string=dxfheader_string.replace("ZZZ",str(FoundNotes)) #replace value for total notes


	#declar mbc_data list
	mbc_data_out=[]

	for n in range(FoundNotes): #scan through the array from earlier and start populating the list
		mbc_data_out.append("p="+str(notearray[n][1]))
		mbc_data_out.append("t="+str(('{0:.4f}'.format(abs(notearray[n][0])))))  #converts float to string with 4 trailing decimal places
		mbc_data_out.append("v=1")
		mbc_data_out.append("s=0")
		mbc_data_out.append("a=1")
		mbc_data_out.append("i=0")
		
	#declar final mbc container
	mbc_out=[]
	mbc_out.append(dxfheader_string) #first add in header
	mbc_out=mbc_out + mbc_data_out #then add in the data

	#write total mbc_out to a file
	with open(output_file, 'w') as f:
				for item in mbc_out:
					print >> f, item
					
	print "Conversion complete!  Data written to",output_file
	