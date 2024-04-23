#!/home/guillaume/anaconda3/bin/python3

import sys
import os
import subprocess
import threading
import glob
import exiftool


#take a liste of SLC, a master ref and procced to the coregistration of all SLC to the master geometry

###
	create_offset ./20230903/20230903.IW1.slc.par ./20230810/20230810.IW1.slc.par 20230903_20230810.off 1 - - 0
	init_offset_orbit ./20230903/20230903.IW1.slc.par ./20230810/20230810.IW1.slc.par 20230903_20230810.off

	init_offset_orbit ./20230903/20230903.IW1.slc ./20230810/20230810.IW1.slc  ./20230903/20230903.IW1.slc.par ./20230810/20230810.IW1.slc.par 20230903_20230810.off 1 2
	init_offset ./20230903/20230903.IW1.slc ./20230810/20230810.IW1.slc  ./20230903/20230903.IW1.slc.par ./20230810/20230810.IW1.slc.par 20230903_20230810.off 1 2

	offset_pwr ./20230903/20230903.IW1.slc ./20230810/20230810.IW1.slc  ./20230903/20230903.IW1.slc.par ./20230810/20230810.IW1.slc.par 20230903_20230810.off offs ccp 64 64 offsets 1 32 32 0.15
	offset_fit offs ccp 20230903_20230810.off  coffs coffsets 0.15 4 0

	SLC_interp ./20230810/20230810.IW1.slc  ./20230903/20230903.IW1.slc.par ./20230810/20230810.IW1.slc.par 20230903_20230810.off slave.rslc slave.rslc.par
	SLC_intf ./20230903/20230903.IW1.slc slave.rslc ./20230903/20230903.IW1.slc.par slave.rslc.par 20230903_20230810.off 20230903_20230810.int 1 5 - - 1 1

	base_init ./20230903/20230903.IW1.slc.par slave.rslc.par 20230903_20230810.off 20230903_20230810.int 20230903_20230810.base 0
	base_perp 20230903_20230810.base ./20230903/20230903.IW1.slc.par 20230903_20230810.off > 20230903_20230810.base.perp

	cc_wave 20230903_20230810.int - - coherence.int 22084
	disdt_pwr coherence.int - 22084 - - 0.2 1 - grey.cm - - -
	
#-----------------------------------------------------------------
def test_fichier(path):

	try:
 		with open(path): pass
 		print("file "+ path +" exist")
 		return 1
	except IOError:
 		print("Erreur! file "+path+" doesn't exist or not found")
 		return 0
###
def compute_offset(master, slave):
	return(0)
def coregistration(master,slave,directory="./RSLC"):

	
	return(0)

def main(SLC_tab,master_ind, directory="./RSLC"):

	if(!test_fichier(directory)):
		os.makedirs(directory)

	file_in =open(SLC_tab,'r')
	
	ind=1
	for line in file_in:
		if(ind==master_ind):
			master_slc,master_par=line.split(" ")
			print("master SLC:", master_SLC)
			print("master SLC par:",master_par)
			break
		ind+=1
	file_in.seek(0)
	
	for line in file_in:
		slave_par,slave_SLC=line.split(" ")
		coregistration(master_SLC,master_par,slave_SLC,slave_par)
	
	file_in.close()
	compute_offset()

if __name__=="__main__":

	SLC_tab = sys.argv[1]	#liste des slc (path/to/SLC.slc path/to/SLC.par)
	master = sys.argv[2] # ind of the master SLC according to SLC_tab (from 1-n)
	main(SLC_tab,master)

