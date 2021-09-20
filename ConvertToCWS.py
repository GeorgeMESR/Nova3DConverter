from PIL import Image, ImageOps
import os
import zipfile
from datetime import datetime
# import threading
# import io
# import time

#Input file name without .ext
fileName='DRUID2'
config_printer={}
#To exposition time correction or comment this line for get from gcode
config_printer['Layer Time']=3000 # ms
#speed has been incread after this heigth
FirstLayersHeight=2 #mm


for folder, subfolders, files in os.walk('Out/tmp'):
	for file in files:
			os.remove(os.path.join(folder, file))
for folder, subfolders, files in os.walk('Out/tmp1'):
	for file in files:
			os.remove(os.path.join(folder, file))
rawzip = zipfile.ZipFile('In/' + fileName + '.zip', 'r')
rawzip.extractall('Out/tmp')

with open('Out/tmp/run.gcode', 'r') as fin:
	lines = fin.readlines()
	fin.close()
	for l in lines:
		if(l.find(';layerHeight:')!=-1):
			config_printer['Layer Thickness']=float(l[len(';layerHeight:'):len(l)].strip())
			print('Layer Thickness' + str(config_printer['Layer Thickness']))
		if(l.find(';totalLayer:')!=-1):
			config_printer['Number of Slices']=int(l[len(';totalLayer:'):len(l)].strip())
			print('Number of Slices' + str(config_printer['Number of Slices']))
		if(l.find(';resolutionX:')!=-1):
			XRES=int(l[len(';resolutionX:'):len(l)].strip())
		if(l.find(';resolutionY:')!=-1):
			YRES=int(l[len(';resolutionY:'):len(l)].strip())


def GetValue(instr):
	if instr[0].isdigit():
		k=instr.find('m')
		if(k==-1):
			k=instr.find('s')
		val=instr
		units=''
		if(k!=-1):
			val=instr[0:k].strip()
			units=instr[k:len(instr)]
		if(val.find('.')!=-1):
			try:
				return float(val),units
			except:
				print('Strange string value '+ instr)
				return 0.0,units
		else:
			try:
				return int(val),units
			except:
				print('Strange string value ' + instr)
				return 0,units
	else:
		return instr, ''

with open('Out/tmp1/chitu.gcode', 'w') as fout:
	with open('gcode/lycheeHat.gcode', 'r') as fin:
		lines=fin.readlines()
		fin.close()
		for l in lines:
			l2=l.lstrip(';(')
			l2=l2.rstrip(')\n')
			l2=l2.strip('')
			l1=l2.split('=')
			if(len(l1)<2):
				fout.write(l)
			else:
				name=l1[0].strip()
				value=l1[1].strip()
				if (name in config_printer)==False:
					config_printer[name], units=GetValue(value)
				else:
					noused, units = GetValue(value)
				pl=name.ljust(22)
				if(name!='Number of Slices'):
					fout.write(';(' + pl + '  = ' + str(config_printer[name])+' '+units + '\n')
				else:
					fout.write(';' + pl + '  = ' + str(config_printer[name])+' '+units + '\n')
		fin.close()
	if(XRES!=config_printer['X Resolution'] or YRES!=config_printer['Y Resolution']):
		print('Please change resolution to %dx%d and repeat slice' %(config_printer['X Resolution'],config_printer['Y Resolution']))
	with open('gcode/lycheeStart.gcode', 'r') as fin:
		lines=fin.readlines()
		fin.close()
		for l in lines:
			fout.write(l)

	time_of_layerstart=config_printer['Blanking Layer Time']
	time_of_exposition=config_printer['Bottom Layers Time']
	time_of_UFoff=int(config_printer['Blanking Layer Time']/2)
	speed_of_lift_up=config_printer['Z Bottom Lift Feed Rate']
	liftUp=config_printer['Lift Distance']
	time_of_lift_up1= int(60000.* liftUp/ speed_of_lift_up)
	time_of_lift_up2=0#int(config_printer['Blanking Layer Time']/2)
	liftDn=-config_printer['Lift Distance']+float(config_printer['Layer Thickness'])
	speed_of_lift_down=config_printer['Z Lift Feed Rate']
	time_of_lift_down=int(60000.* -liftDn/ speed_of_lift_down)

	number_BotLayers=config_printer['Number of Bottom Layers']
	number_FirstLayers=FirstLayersHeight/float(config_printer['Layer Thickness'])

	for i in range(config_printer['Number of Slices']):
		fout.write(';--- Layer %d\n' %(i))
		fout.write(';<Delay> %d\n' %(time_of_layerstart))
		fout.write(';<Slice> %d\n' %(i))
		fout.write('M106 S255\n')
		if(i>=number_BotLayers):
			time_of_exposition=(config_printer['Layer Time'])
			time_of_UFoff=0
			time_of_lift_up2=int(config_printer['Blanking Layer Time']/2)
		if(i>=number_FirstLayers):
			speed_of_lift_up = config_printer['Z Lift Feed Rate']
			time_of_lift_up1 = int(60000. * liftUp / speed_of_lift_up)
			speed_of_lift_down = config_printer['Z Lift Retract Rate']
			time_of_lift_down = int(60000. * -liftDn / speed_of_lift_down)

		fout.write(';<Delay> %d\n' % (time_of_exposition))
		fout.write('M106 S0\n')
		fout.write(';<Slice> Blank\n')
		fout.write(';<Delay> %d\n' %(time_of_UFoff))
		fout.write('G1 Z%g F%d\n' %(liftUp, speed_of_lift_up))
		fout.write(';<Delay> %d\n' %(time_of_lift_up1))
		fout.write(';<Delay> %d\n' %(time_of_lift_up2))
		fout.write('G1 Z%g F%g\n' %(liftDn, speed_of_lift_down))
		fout.write(';<Delay> %d\n' %(time_of_lift_down))

	with open('gcode/lycheeFin.gcode', 'r') as fin:
		lines=fin.readlines()
		fin.close()
		for l in lines:
			fout.write(l)
	fout.close()
with open('Out/tmp1/slice.conf' , 'w') as fout:
	dt=datetime.now()
	strdate=dt.strftime("%d. %B %Y, %I:%M%p")
	fout.write('# Chitu Slicer 1.0 ' + strdate +'\n' )
	fout.write('# conf version 1.0'+'\n\n')
	fout.write('xppm                = '+str(config_printer['Pix per mm X'])+'\n')
	fout.write('yppm                = '+str(config_printer['Pix per mm Y'])+'\n')
	fout.write('xres                = '+str(config_printer['X Resolution'])+'\n')
	fout.write('yres                = '+str(config_printer['Y Resolution'])+'\n')
	fout.write('thickness           = '+str(config_printer['Layer Thickness'])+'\n')
	fout.write('layers_num          = '+str(config_printer['Number of Slices'])+'\n')
	fout.write('head_layers_num     = '+str(config_printer['Number of Bottom Layers'])+'\n')
	fout.write('layers_expo_ms      = '+str(config_printer['Layer Time'])+'\n')
	fout.write('head_layers_expo_ms = '+str(config_printer['Bottom Layers Time'])+'\n')
	fout.write('wait_before_expo_ms = '+str(config_printer['Blanking Layer Time'])+'\n')
	fout.write('lift_distance       = '+str(config_printer['Lift Distance'])+'\n')
	fout.write('lift_up_speed       = '+str(config_printer['Z Lift Feed Rate'])+'\n')
	fout.write('lift_down_speed     = '+str(config_printer['Z Bottom Lift Feed Rate'])+'\n')
	fout.write('lift_when_finished  = '+str(config_printer['Z Lift Retract Rate'])+'\n')
	fout.close()

def Convert(num):
	imageIn = Image.open('Out/tmp/%d.png' % (num + 1))
	ResX = int(config_printer['X Resolution']/ 3)
	ResY = int(config_printer['Y Resolution'])
	imageCWS = Image.new("RGB", (ResX, ResY))
	for j in range(ResY):
		for k in range(ResX):
			imageCWS.putpixel((k,j), (imageIn.getpixel((k * 3 + 2,j)), imageIn.getpixel((k * 3 + 1,j)), imageIn.getpixel((k * 3,j))))
	imageCWS.save('Out/tmp1/chitu%03d.png' % (num))
	print('Save chitu%03d.png' % (num))

def ConvertFast(num):
	imageIn = Image.open('Out/tmp/%d.png' % (num + 1))
	imageIn1=ImageOps.mirror(imageIn) # for exhange R and B bytes
	imageIndata=imageIn1.tobytes()
	ResX = int(config_printer['X Resolution']/ 3)
	ResY = int(config_printer['Y Resolution'])
	imageCWS = Image.new("RGB", (ResX, ResY))
	imageCWS.frombytes(imageIndata)
	imageCWS1=ImageOps.mirror(imageCWS) # repeat mirror
	imageCWS1.save('Out/tmp1/chitu%04d.png' % (num))
	print('Save chitu%04d.png' % (num))

for i in range(config_printer['Number of Slices']):
	ConvertFast(i)

# for i in range(0,config_printer['Number of Slices'],3):
# 	t1= threading.Thread(target= Convert1, args=(i,))
# 	t2 = threading.Thread(target=Convert1, args=(i+1,))
# 	t3 = threading.Thread(target=Convert1, args=(i+2,))
# 	t1.start()
# 	t2.start()
# 	t3.start()
# 	t1.join()
# 	t2.join()
# 	t3.join()


cwszip = zipfile.ZipFile('Out/' + fileName + '.cws', 'w')
for folder, subfolders, files in os.walk('Out/tmp1'):
	for file in files:
			cwszip.write(os.path.join(folder, file),os.path.relpath(os.path.join(folder, file), 'Out/tmp1'),compress_type=zipfile.ZIP_DEFLATED)
cwszip.close()