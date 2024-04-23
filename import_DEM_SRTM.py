#!/home/guillaume/anaconda3/bin/python3

import sys
import os
import subprocess
import threading
import glob
import math
import zipfile

path_to_SRTM="/home/guillaume/Bureau/SAR_SCRIPTS/SRTMGL1"

#-----------------------------------------------------------------
def test_fichier(path):

	try:
 		with open(path): pass
 		print("file "+ path +" exist")
 		return 1
	except IOError:
 		print("Erreur! file "+path+" doesn't exist or not found")
 		return 0

#-----------------------------------------------------------------
def get_srtm_tiles_from_footprint(foot_print,path_to_SRTM):

	#translate footprint into srtmgrid and file name
	#SRTM name convention correspond to the lower left corner of the image
	#foot_print=[minlat, maxlat, minlon, maxlon] 
	#decimal degree, lat=[-90S,90N],lon=[-180W,180E] 
	#greenwhich lon=0
	
	list_tiles=[]
	minlat=float(foot_print[0])
	maxlat=float(foot_print[1])
	minlon=float(foot_print[2])
	maxlon=float(foot_print[3])

	minlat_round = int(math.floor(minlat))
	maxlat_round = int(math.floor(maxlat))
	minlon_round = int(math.floor(minlon))
	maxlon_round = int(math.floor(maxlon))
	
	nstp_lat=maxlat_round-minlat_round
	nstp_lon=maxlon_round-minlon_round

	print(minlat_round,maxlat_round,minlon_round,maxlon_round)

	for la in range(nstp_lat+1):

		for lo in range(nstp_lon+1):
			
			print("tile:",minlat_round+la,minlon_round+lo)
			
			templat=minlat_round+la
			templon=minlon_round+lo

			if(templat>=0 and templon < 0):
				flagLat,flagLon="N","W"
			if(templat>=0 and templon >= 0):
				flagLat,flagLon="N","E"
			if(templat < 0 and templon < 0):
				flagLat,flagLon="S","W"
			if(templat < 0 and templon >= 0):
				flagLat,flagLon="S","E"

			flagname=flagLat+"{:02}".format(abs(templat))+flagLon+"{:03}".format(abs(templon))
			
			name=flagname+".SRTMGL1.hgt.zip"
			
			file_name=os.path.join(path_to_SRTM,name)
			
			if(test_fichier(file_name)):
				print("new tile found: "+file_name)
				list_tiles.append(file_name)

	return list_tiles

#-----------------------------------------------------------------
def make_dem_from_tiles_GAMMA(list_dem_zip, path_dem="./"):
	
	print("build dem from tiles")
	
	path_dem = os.path.join(path_dem,"dem")

	try:
		os.makedirs(path_dem)
		print("creation of dem directory")
	except:
		print(path_dem+" exist")

	for file_name in list_dem_zip:
		with zipfile.ZipFile(file_name, 'r') as zip_ref:
			zip_ref.extractall(path_dem)

	list_hgt= glob.glob(path_dem+"/*.hgt")
	
	commande_mosaic=["mosaic",str(len(list_hgt))]

	n=1

	for file in list_hgt:

		name_out=path_dem+"/dem"+str(n)
		name_out_par=name_out+"_par"
		
		p=subprocess.Popen(["dem_import", file, name_out,name_out_par])
		p.wait()

		commande_mosaic.append(name_out)
		commande_mosaic.append(name_out_par)

		n+=1

	commande_mosaic.append(path_dem+"/SRTM.dem")
	commande_mosaic.append(path_dem+"/SRTM.dem_par")
	commande_mosaic.append("1")
	commande_mosaic.append("0")
	
	
	#print("Subprocess: "+commande_mosaic)
	p=subprocess.Popen(commande_mosaic)
	p.wait()
#-----------------------------------------------------------------
def make_dem_from_tiles_GMTSAR(list_dem_zip, path_dem="./"):
	
	print("build dem from tiles")
	
	path_dem = os.path.join(path_dem,"dem")

	try:
		os.makedirs(path_dem)
		print("creation of dem directory")
	except:
		print(path_dem+" exist")

	for file_name in list_dem_zip:
		with zipfile.ZipFile(file_name, 'r') as zip_ref:
			zip_ref.extractall(path_dem)

	list_hgt= glob.glob(path_dem+"/*.hgt")
	
	commande_mosaic=["mosaic",str(len(list_hgt))]

	n=1

	for file in list_hgt:

		name_out=path_dem+"/dem"+str(n)
		name_out_par=name_out+"_par"
		
		p=subprocess.Popen(["dem_import", file, name_out,name_out_par])
		p.wait()

		commande_mosaic.append(name_out)
		commande_mosaic.append(name_out_par)

		n+=1

	commande_mosaic.append(path_dem+"/SRTM.dem")
	commande_mosaic.append(path_dem+"/SRTM.dem_par")
	commande_mosaic.append("1")
	commande_mosaic.append("0")
	
	
	#print("Subprocess: "+commande_mosaic)
	p=subprocess.Popen(commande_mosaic)
	p.wait()
def main(foot_print=[11.298461, 13.371735, -87.595421, -84.974709],path="./"):

	make_dem_from_tiles_GAMMA(get_srtm_tiles_from_footprint(foot_print,path_to_SRTM),path)
	
#-----------------------------------------------------------------

def make_lookupTable_GAMMA(ref_image=None):
	
	if(ref_image):
	
		ref_image_name = ref_image+"/"+ref_image+".mli.par"
		dem_name_par="dem/SRTM.dem_par"
		dem_name="dem/SRTM.dem"
		eqa_par="dem/eqa.dem_par"
		eqa_dem="dem/eqa.dem"
		lookuptable="dem/lookup_table.lt"
		command = ["gc_map", 
			  ref_image_name,
			  "-",
			  dem_name_par,
			  dem_name,
			  eqa_par,
			  eqa_dem,
			  lookuptable,
			  "-","-","-","-","-","-","-","-","-","-","-","-"]
		p=subprocess.Popen(command)
		p.wait()
	else:
		print("No reference date/image given, return 0")
		return(0)

#gc_map_fine 20211027.lt 7201 20211027.diff_par 20211027.lt_fine 1
#-----------------------------------------------------------------
if(__name__=="__main__"):
	
	print(sys.argv)
	#if(len(sys.argv) >= 5):
	if(0):
		
		foot_print=[]
		
		foot_print.append(sys.argv[1]) #min lat [-90:+90]
		foot_print.append(sys.argv[2]) #max lat [-90:+90]
		foot_print.append(sys.argv[3]) #min lon [-180:+180]
		foot_print.append(sys.argv[4]) #max lon [-180:+180]
		
		print(foot_print)
		
		path=sys.argv[5]
		print(path)
		
		main(foot_print,path)
		
		print("cleaning...")
		for el in glob.glob("./dem/dem*_par"):
			print("delete:"+str(el))
			os.remove(el)
		for el in glob.glob("./dem/*.hgt"):
			print("delete:"+str(el))
			os.remove(el)
		for el in glob.glob("./dem/dem*"):
			print("delete:"+str(el))
			os.remove(el)
		
	if(len(sys.argv) >= 6):
		
		make_lookupTable(sys.argv[6])
			

	else:

		main()
