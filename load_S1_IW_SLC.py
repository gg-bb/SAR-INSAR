#!/home/guillaume/anaconda3/bin/python3

import sys
import os
import subprocess
import threading
import glob
import exiftool

#script automatisant la mise en forme des données S1 à partir des fichier .SAFE. Sequences de commandes extraite de la documentation GAMMA: ASAR ScanSAR interferometry, section 5 - Septembre 2023
#load SAFE files
#applie par_S1_SLC to each swath

#@faire: sortir une liste des slc sélectionnées
#@faire: pouvoir sélectionner une swath  (done) ou un burst
#ScanSAR_burst_copy 20230810.IW1.slc 20230810.IW1.slc.par 20230810.IW1.slc.TOPS_par 20230810.IW1_b3.slc 20230810.IW1_b3.slc.par 3 1 20230810.IW1_b3.slc.dr.par

#-----------------------------------------------------------------
def test_fichier(path):

	try:
 		with open(path): pass
 		print("file "+ path +" exist")
 		return 1
	except IOError:
 		print("Erreur! file "+path+" doesn't exist or not found")
 		return 0


class ImageSAR:

	def __init__(self, nameSAFE,swath_nb=0):
		
		self.SAFE=nameSAFE
		
		self.swath_nb=swath_nb
		self.date=self.SAFE.split("_")[6].split("T")[0]
		self.get_footprint()
		self.slc_path="./SLC"
		self.rslc_path="./RSLC"
		self.diff_path="./DIFF"
		
	
	def create_rep(self):
	
		try:
			os.mkdir(self.date)
			
		except:
			print("can't create directory: "+str(self.date))
			print("file already existing?")
			quit()
			
	def get_footprint_swath(self, name_image):
	
		#get footprint form exif information extracted from the tiff images
		#règle des 3M: Moche Mais Marche

		metadata=exiftool.ExifToolHelper().get_metadata(name_image)
		temp=str(metadata[0]).split(',')
		
		ref_width=int(temp[13].split(":")[2])-1 # compté à partir de 0
		ref_height=int(temp[14].split(":")[2])-1
		
		temp=temp[30].split(":")[2].split(" ")[1:]
		
		TLlon=float(temp[3])
		TLlat=float(temp[4])
		BRlon=float(temp[3])
		BRlat=float(temp[4])
		
		
		for i in range(int(len(temp)/6)):
			
			pos_0=i*6
			pos_1=pos_0+6
			px,py,pz,lon,lat,alt=temp[pos_0:pos_1]
			
			if(px==str(ref_width) and py==str(0)):
				TRlon=float(lon)
				TRlat=float(lat)
				
			if(px==str(0) and py==str(ref_height)):
				BLlon=float(lon)
				BLlat=float(lat)
	
		min_Lat=min([TLlat,TRlat,BLlat,BRlat])
		max_Lat=max([TLlat,TRlat,BLlat,BRlat])
		min_Lon=min([TLlon,TRlon,BLlon,BRlon])
		max_Lon=max([TLlon,TRlon,BLlon,BRlon])
		
		file_out=open("footprint.txt","w")
		file_out.write(str([min_Lat,max_Lat,min_Lon,max_Lon]))
		file_out.close()
		

	def import_DATA(self):
	
		listeSwath=["004","005","006"]
		listeInd=["1","2","3"]
		
		if(!test_fichier(self.slc_path)):
			os.mkdir(self.slc_path)
		
		for i,j in zip(listeSwath,listeInd):
			
			if(int(j)==self.swath_nb or self.swath_nb==0):
			
				nameTiff = glob.glob(self.SAFE+"/measurement/*"+i+".tiff")[0]
				nameXml  = glob.glob(self.SAFE+"/annotation/*"+i+".xml")[0]
				calibrationXml = glob.glob(self.SAFE+"/annotation/calibration/calibration-*"+i+".xml")[0]
				noiseXml = glob.glob(self.SAFE+"/annotation/calibration/noise-*"+i+".xml")[0]
			
				self.get_footprint_swath(nameTiff)
		
				outSLCpar = self.slc_path+"/"+self.date+"/"+self.date+".IW"+j+".slc.par"
				outSLC    = self.slc_path+"/"+self.date+"/"+self.date+".IW"+j+".slc"
				outSLC_TOPSpar=self.slc_path+"/"+self.date+"/"+self.date+".IW"+j+".slc.TOPS_par"
		
				p=subprocess.Popen(["par_S1_SLC", nameTiff, nameXml, calibrationXml, noiseXml, outSLCpar, outSLC, outSLC_TOPSpar])
				p.wait()
	
		
	def makeMliSlcMosaic(self,la=10,lr=2):
	
		fileSLCtab=self.date+"/SLC_tab"
		
		SLCout=self.date+"/"+self.date+".slc"
		SLCoutPar=self.date+"/"+self.date+".slc.par"
		
		p=subprocess.Popen(["SLC_mosaic_S1_TOPS", fileSLCtab, SLCout, SLCoutPar, str(la), str(lr)])
		p.wait()
		
		MLIout=self.date+"/"+self.date+".mli"
		MLIoutPar=self.date+"/"+self.date+".mli.par"
		
		p=subprocess.Popen(["multi_S1_TOPS", fileSLCtab, MLIout, MLIoutPar, str(la), str(lr)])
		p.wait()


	def get_footprint(self):

		file_in_name=self.SAFE+"/manifest.safe"

		file_in = open(file_in_name,"r")

		latl=[]
		lonl=[]
		for line in file_in:

			if "<gml:coordinates>" in line:
	
				nline=line.replace('<gml:coordinates>','')
				nline=nline.replace('</gml:coordinates>','')
		
				for coord in nline.split(' '):

					if coord=='':
						continue

					lat,lon = coord.split(',')
			
					latl.append(float(lat))
					lonl.append(float(lon))

		file_in.close() 
		self.footprint=[min(latl),max(latl),min(lonl),max(lonl)]
		file_out_name=self.SAFE+"/footprint.txt"
		fileout=open(file_out_name,"w")
		fileout.write(str(self.footprint))
		fileout.close()
	
	def makeSLCtab(self):
	
		listeInd=["1","2","3"]
		
		file=open(self.date+"/SLC_tab","w")
	
		for i in listeInd:
				
			flag=self.date+"/"+self.date+".IW"+i+".slc"
			
			outSLCpar=flag+".par"
			outSLC=flag
			outSLC_TOPSpar=flag+".TOPS_par"
			line=outSLC+" "+outSLCpar+" "+outSLC_TOPSpar+"\n"
			
			if(int(i)==self.swath_nb or self.swath_nb==0):
				file.write(line)	
		
		file.close()


#------------------------------------------------------------------------------------------------------

def main(nameSAFE,swath_nb=0):

	file=ImageSAR(nameSAFE,swath_nb)
	file.create_rep()
	file.import_DATA() #file.import(1) si uniquement la swath 1 (003), 2 pour (004), 3 pour (005)
	file.makeSLCtab()
	
	print(file.footprint)
	
	la=10
	lr=2
	file.makeMliSlcMosaic(la,lr)

if(__name__=="__main__"):

	if(len(sys.argv) >= 3):
		swath_nb=int(sys.argv[1])
		nameSAFE=sys.argv[2]
		main(nameSAFE)

	if(len(sys.argv)== 2):
		swath_nb=int(sys.argv[1])
		for nameSAFE in glob.glob("*.SAFE"):
			main(nameSAFE,swath_nb)
	
	print("done")
	
	
