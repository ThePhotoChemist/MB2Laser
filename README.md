# MB2Laser
A tool to convert DXF/MBC files to Gcode (30 note punch strips) or SVG files (Mr. Christmas disks)

An example of a laser cutter using my punch strip code can be found here:
https://www.youtube.com/watch?v=etWETnmRU74

An example of a laser-cut disk playing on a "Mr. Christmas" disk player can be found here:
https://www.youtube.com/watch?v=Sm_uzP-zMU4

Making Punch Strings
To make a punch strip, use "python mb2laser.py -i "your file".  This will output the gcode into a file called "program_out.txt", which can then be cut out on such a machine.  The program supports 30-Note MBC (MusicBoxComposer) files or GI30F DXF (MusicBoxManiacs) exports.

Making Mr. Christmas Disks
To make a disk, use "python mb2laser.py -i "your file" -C.  This will create a file called "disk_out.svg" Supported formats are 20-Note MBC files from MusicBoxComposer or "GI20" DXF exports from MusicBoxManiacs.  Note that due to the disk runtime being only about 26 seconds, the song must be fairly short.  The script will find the last note and assume that to be at the 26 second position, and will scale the rest of the notes accordingly. 

To convert DXF files to MBC, useful for exporting songs from MusicBoxManiacs into MusicBoxComposer, use:
python dxf2mbc.py -i "your_dxf_30f_file.dxf" or
python dxf2mbc.py -GI20 -i "your_dxf_GI20_file.dxf"
