#!/usr/bin/env python

import sys

import math

import copy

from argparse import ArgumentParser

parser = ArgumentParser()

parser.add_argument("-i", "--input", dest="input_file",
                    help="input Music Maiancs DXF", metavar="FILE")	
parser.add_argument("-o", "--output", dest="output_file", default="program_out.txt",
					help="destination text file with gcode", metavar="FILE")
parser.add_argument("-C", "--circle",
                    action="store_true", dest="diskmode", default=False,
                    help="Create SVG for Mr. Christmas format")
parser.add_argument("-T", "--time", dest="tcutoff", default=25,
					help="Cutoff time for Mr. Christmas disk", metavar="INTEGER")

NValOffset=120
TValOffset=90

MoveSpeed=3000.0
FeedRate=150.0
LaserIntensity=12000
PaperAdvanceSpeed=2500

CircleSizeMultiplier=1.0

FinalAdvanceDistance=200


args = parser.parse_args()

FoundNotes=0
DXFMode=0
MBCMode=0

EnglishToMetricScalar=25.4

MBC2DXFMMTSlope=16.04579310
MBC2DXFMMTIntercept=9.906

MBC2DXFMMNSlope=2.00572414
MBC2DXFMMNIntercept=5.715

DXF2MBCT20Slope=1.06311
DXF2MBCT20Intercept=-0.4146

DXF2MBC20NSlope=8.50492
DXF2MBC20NIntercept=-1.91361

StripSectionLengthIn=8
LaserNoteOffset=0
LaserTimeOffset=0

xlist=[]
ylist=[]


if args.input_file==None:
	print "No Input file specified!  Exiting..."
	sys.exit()

#Read in file -i and -o arguments into variables
input_file=args.input_file
output_file=args.output_file

extension=input_file[-3:]
print "extension is", extension

if extension=="mbc":
	MBCMode=1
if extension=="dxf":
	DXFMode=1
if DXFMode==0 and MBCMode==0:
	print "extension not recognized, defaulting to dxf mode"
	DXFMode=1



with open(input_file, 'r') as f: #search for .txt file and import all into an array, separated by each line
	Lines = f.read().splitlines()	

LineCount=len(Lines)
print "File has",LineCount,"total lines"


if DXFMode==1:
	print "Searching for note data..."
	for n in range(LineCount):
		CurRowString=Lines[n]
		if CurRowString=="CIRCLE":
			FoundNotes=FoundNotes+1
			xlist.append(Lines[n+4])
			ylist.append(Lines[n+6])

			
	print "Found a total of",FoundNotes,"notes"

	w, h = 2, len(xlist)
	notearray = [[0 for x in range(w)] for y in range(h)]

	if args.diskmode==0:
		for n in range(len(xlist)):
			notearray[n][0]=round((float(xlist[n])*EnglishToMetricScalar),4)
			notearray[n][1]=round((float(ylist[n])*EnglishToMetricScalar),4)
	else:
		for n in range(len(xlist)):
			notearray[n][0]=round((float(xlist[n])*DXF2MBCT20Slope+DXF2MBCT20Intercept),4)
			notearray[n][1]=round((float(ylist[n])*DXF2MBC20NSlope+DXF2MBC20NIntercept),4)

	notearray.sort(key=lambda x: x[0])
	print "sorted notearray is:", notearray
	print len(notearray)
	
if MBCMode==1:
	print "Searching for note data..."	
	for n in range(LineCount):
		CurRowString=Lines[n]
		CurRowTest=CurRowString[0:2]
		if CurRowTest=="p=":
			FoundNotes=FoundNotes+1
			xlist.append(Lines[n+1].replace("t=",""))
			ylist.append(Lines[n].replace("p=",""))
	print "Found a total of",FoundNotes,"notes"

	w, h = 2, len(xlist)
	notearray = [[0 for x in range(w)] for y in range(h)] 
	
	if args.diskmode==0:
		for n in range(len(xlist)):
			notearray[n][0]=round(((float(xlist[n]))*MBC2DXFMMTSlope+MBC2DXFMMTIntercept),4)
			notearray[n][1]=round(((float(ylist[n]))*MBC2DXFMMNSlope+MBC2DXFMMNIntercept),4)
	else:
		for n in range(len(xlist)):
			notearray[n][0]=round(((float(xlist[n]))),4)
			notearray[n][1]=round(((float(ylist[n]))),4)
		
	notearray.sort(key=lambda x: x[0])
	print "sorted notearray is:", notearray
	print len(notearray)

StripSectionLength=StripSectionLengthIn*EnglishToMetricScalar

LastNoteTime=notearray[FoundNotes-1][0]

print "Last Note occurs at T=",LastNoteTime

if args.diskmode==0:
	print "Using a strip section length of",StripSectionLengthIn,"(",StripSectionLength,")"

	NumStrips=int(math.ceil(LastNoteTime/StripSectionLength))

	print "Splitting the song into",NumStrips,"parts"

	GcodeList=[]

	GcodeList.append("G90;")
	GcodeList.append("M5;")
	GcodeList.append("G21;")
	GcodeList.append("M5;")
	GcodeList.append("G10 P0 L20 Z0")


	for n in range(NumStrips):
		LowerBound=n*StripSectionLength
		UpperBound=(n+1)*StripSectionLength
		
		print "New LowerBound is",LowerBound,"and new UpperBound is",UpperBound
		
		for i in range(len(notearray)):
			CurrentNoteTime=notearray[i][0]
			if CurrentNoteTime>=LowerBound and CurrentNoteTime<UpperBound:
				#do gcode compilation stuff here

				TVal=CurrentNoteTime-LowerBound*CircleSizeMultiplier+TValOffset
				NVal=notearray[i][1]*CircleSizeMultiplier+NValOffset
				
				GcodeString="G0 F"+str(MoveSpeed)+" X"+str(0.971823*CircleSizeMultiplier+NVal)+" Y"+str(0.0*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeList.append("M3 S"+str(LaserIntensity)+";")
				GcodeString="G1 F"+str(FeedRate)+" X"+str(0.934116*CircleSizeMultiplier+NVal)+" Y"+str(-0.26808*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				
				GcodeString="G1 F"+str(FeedRate)+" X"+str(0.934116*CircleSizeMultiplier+NVal)+" Y"+str(-0.26808*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeString="G1 F"+str(FeedRate)+" X"+str(0.823922*CircleSizeMultiplier+NVal)+" Y"+str(-0.515358*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeString="G1 F"+str(FeedRate)+" X"+str(0.649791*CircleSizeMultiplier+NVal)+" Y"+str(-0.722643*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeString="G1 F"+str(FeedRate)+" X"+str(0.425236*CircleSizeMultiplier+NVal)+" Y"+str(-0.873851*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeString="G1 F"+str(FeedRate)+" X"+str(0.167682*CircleSizeMultiplier+NVal)+" Y"+str(-0.957248*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeString="G1 F"+str(FeedRate)+" X"+str(0*CircleSizeMultiplier+NVal)+" Y"+str(-0.971824*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeString="G1 F"+str(FeedRate)+" X"+str(-0.26808*CircleSizeMultiplier+NVal)+" Y"+str(-0.934117*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeString="G1 F"+str(FeedRate)+" X"+str(-0.515357*CircleSizeMultiplier+NVal)+" Y"+str(-0.823922*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeString="G1 F"+str(FeedRate)+" X"+str(-0.722642*CircleSizeMultiplier+NVal)+" Y"+str(-0.649791*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeString="G1 F"+str(FeedRate)+" X"+str(-0.87385*CircleSizeMultiplier+NVal)+" Y"+str(-0.425236*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeString="G1 F"+str(FeedRate)+" X"+str(-0.957247*CircleSizeMultiplier+NVal)+" Y"+str(-0.167682*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeString="G1 F"+str(FeedRate)+" X"+str(-0.971823*CircleSizeMultiplier+NVal)+" Y"+str(0*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeString="G1 F"+str(FeedRate)+" X"+str(-0.934116*CircleSizeMultiplier+NVal)+" Y"+str(0.26808*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeString="G1 F"+str(FeedRate)+" X"+str(-0.823921*CircleSizeMultiplier+NVal)+" Y"+str(0.515357*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeString="G1 F"+str(FeedRate)+" X"+str(-0.64979*CircleSizeMultiplier+NVal)+" Y"+str(0.722642*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeString="G1 F"+str(FeedRate)+" X"+str(-0.425235*CircleSizeMultiplier+NVal)+" Y"+str(0.87385*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeString="G1 F"+str(FeedRate)+" X"+str(-0.167682*CircleSizeMultiplier+NVal)+" Y"+str(0.957247*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeString="G1 F"+str(FeedRate)+" X"+str(0*CircleSizeMultiplier+NVal)+" Y"+str(0.971823*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeString="G1 F"+str(FeedRate)+" X"+str(0.26808*CircleSizeMultiplier+NVal)+" Y"+str(0.934116*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeString="G1 F"+str(FeedRate)+" X"+str(0.515357*CircleSizeMultiplier+NVal)+" Y"+str(0.823922*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeString="G1 F"+str(FeedRate)+" X"+str(0.722642*CircleSizeMultiplier+NVal)+" Y"+str(0.649791*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeString="G1 F"+str(FeedRate)+" X"+str(0.87385*CircleSizeMultiplier+NVal)+" Y"+str(0.425236*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeString="G1 F"+str(FeedRate)+" X"+str(0.957247*CircleSizeMultiplier+NVal)+" Y"+str(0.167682*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeString="G1 F"+str(FeedRate)+" X"+str(0.971823*CircleSizeMultiplier+NVal)+" Y"+str(0*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeString="G1 F"+str(FeedRate)+" X"+str(0.971823*CircleSizeMultiplier+NVal)+" Y"+str(0*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeString="G1 F"+str(FeedRate)+" X"+str(0.934116*CircleSizeMultiplier+NVal)+" Y"+str(-0.26808*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeString="G1 F"+str(FeedRate)+" X"+str(0.823922*CircleSizeMultiplier+NVal)+" Y"+str(-0.515358*CircleSizeMultiplier+TVal)+";"
				GcodeList.append(GcodeString)
				GcodeList.append("M5;")
				
				
				
				
				
		
		#Paper Advance
		GcodeList.append("")
		GcodeString="G91 G1 Z"+str(StripSectionLength)+"F"+str(PaperAdvanceSpeed)+";"
		print "Z Advance Code is",GcodeString
		GcodeList.append(GcodeString)
		#Park the laser behind the start of the new section, to avoid weird a malformed circle on the first note
		GcodeList.append("G90G0X100Y70")
		GcodeList.append("")
		
	GcodeString="G91 G1 Z"+str(FinalAdvanceDistance)+"F"+str(PaperAdvanceSpeed)+";"
	GcodeList.append(GcodeString)	
	GcodeList.append("G90G0X100y100")
		
	with open(output_file, 'w') as f:
				for item in GcodeList:
					print >> f, item



if args.diskmode:
	
	cx_offset=90.124901
	cy_offset=206.87508
	
	print "Rescaling time values to degrees"
	
	Time2DegMultiplier=340/LastNoteTime
	DistanceMultiplier=3
	DistanceIntercept=24
	
	for n in range(len(xlist)):
			notearray[n][0]=round(((float(notearray[n][0]))*Time2DegMultiplier),4)
			
			if MBCMode==1:
				ReinterpretedNote=notearray[n][1]
				if ReinterpretedNote==0:
					notearray[n][1]=0
				elif ReinterpretedNote==2:
					notearray[n][1]=1
				elif ReinterpretedNote==4:
					notearray[n][1]=2
				elif ReinterpretedNote==5:
					notearray[n][1]=3
				elif ReinterpretedNote==7:
					notearray[n][1]=4
				elif ReinterpretedNote==9:
					notearray[n][1]=5
				elif ReinterpretedNote==11:
					notearray[n][1]=6
				elif ReinterpretedNote==12:
					notearray[n][1]=7
				elif ReinterpretedNote==14:
					notearray[n][1]=8
				elif ReinterpretedNote==16:
					notearray[n][1]=9
				elif ReinterpretedNote==17:
					notearray[n][1]=10
				elif ReinterpretedNote==19:
					notearray[n][1]=11
				elif ReinterpretedNote==21:
					notearray[n][1]=12
				elif ReinterpretedNote==23:
					notearray[n][1]=13
				elif ReinterpretedNote==24:
					notearray[n][1]=14
				elif ReinterpretedNote==26:
					notearray[n][1]=15
				elif ReinterpretedNote==28:
					notearray[n][1]=16
				elif ReinterpretedNote==29:
					notearray[n][1]=17
				elif ReinterpretedNote==31:
					notearray[n][1]=18
				elif ReinterpretedNote==33:
					notearray[n][1]=19
				else:
					print "Oh god you shouldn't see this, something has gone terribly wrong"
					print "Note was:", notearray[n][1]
					sys.exit()
				
			
			
			notearray[n][1]=round(((float(notearray[n][1]))*DistanceMultiplier+DistanceIntercept),4)
			
	print "Reinterpreted Notes are..."

	
	note_template=[]
	svg_out=[]
	CurrentNote=[]
	
	with open("svg_header.txt", 'r') as f: #search for .txt file and import all into an array, separated by each line
		svg_header = f.read().splitlines()

	with open("svg_footer.txt", 'r') as f: #search for .txt file and import all into an array, separated by each line
		svg_footer = f.read().splitlines()
	
	with open("note_template.txt", 'r') as f: #search for .txt file and import all into an array, separated by each line
		note_template = f.read().splitlines()
		
	svg_out=svg_out + svg_header
	
	for n in range(len(xlist)):
		Degrees=notearray[n][0]
		Radius=notearray[n][1]
		
		NoteStarOffset=3.5
		
		DegreeOffset=(math.atan(NoteStarOffset/Radius)*(180/math.pi))
		
		Radian=(Degrees-DegreeOffset)*(math.pi/180)
		
		#print "Degrees is",Degrees, "Degrees Offset is", DegreeOffset, " and Radius is", Radius
		CurrentNote = copy.deepcopy(note_template)
		
		#x_position=math.cos(Degrees)*Radius+cx_offset
		#y_position=math.sin(Degrees)*Radius+cy_offset
		
		x_position=math.cos(Radian)*Radius+cx_offset
		y_position=math.sin(Radian)*Radius+cy_offset
		
		CurrentNote[3]=CurrentNote[3].replace("X_POSITION", str(x_position))
		CurrentNote[4]=CurrentNote[4].replace("Y_POSITION", str(y_position))
		
		svg_out=svg_out+CurrentNote
		
	svg_out=svg_out+svg_footer
	
	with open("disk_out.svg", 'w') as f:
			for item in svg_out:
				print >> f, item
		
	print "done!"

	print "Conversion complete!  Data written to disk_out.svg"