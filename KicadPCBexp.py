import gerber
from gerber.render.cairo_backend import GerberCairoContext
from gerber.render.theme import THEMES
from io import BytesIO
from gerber.render.render import GerberContext
from PIL import Image, ImageColor, ImageDraw
import zipfile
from datetime import datetime
import os

Image.MAX_IMAGE_PIXELS = None

fileName='Bno080'
Layers='Bot'
# Layers='Top'
#Layers='Both'

#change drill to small plate
drilldiam=0.3
drillintop=False
#drillintop=True

Exposition = 15 #s
Waiting= 5 #s
Negative=False


config_printer={}
config_printer['Blanking Layer Time']=Waiting*1000 # ms
config_printer['Layer Time']=Exposition*1000 # ms
config_printer['Number of Slices']=2
config_printer['Number of Bottom Layers']=1


#speed has been incread after this heigth
FirstLayersHeight=2 #mm

for folder, subfolders, files in os.walk('Out/tmp1'):
	for file in files:
			os.remove(os.path.join(folder, file))

# Read gerber and Excellon files
if(Layers=='Both' or Layers=='Top'):
	top_copper = gerber.read('In/'+fileName+'-F_Cu.gbr')
if(Layers=='Both' or Layers=='Bot'):
	bot_copper = gerber.read('In/'+fileName+'-B_Cu.gbr')
cuts = gerber.read('In/'+fileName+'-Edge_Cuts.gbr')

#change drill layer to small holes with drilldiam diameters
with open('In/'+fileName+'-PTH.drl' , 'r') as fin:
	with open('In/' + fileName + '-PTH_d.drl', 'w') as fout:
		lines=fin.readlines()
		for l in lines:
			k= l.find('C')
			if ( l[0]=='T'and k!=-1):
				fout.write(l[0:k+1]+('%g' % drilldiam)+'\n')
			else:
				fout.write(l)
		fout.close()
	fin.close()

nc_drill = gerber.read('In/'+fileName+'-PTH_d.drl')

# Rendering context
if(Layers=='Both' or Layers=='Top'):
	ctx_top = GerberCairoContext()
	ctx_top.color = (1, 1, 1)
	cuts.render(ctx_top)
	top_copper.render(ctx_top)
	ctx_top.color=(0,0,0)
	ctx_top.drill_color=(0,0,0)
	if(drillintop):
		nc_drill.render(ctx_top)
if(Layers=='Both' or Layers=='Bot'):
	ctx_bot = GerberCairoContext()
	ctx_bot.color = (1, 1, 1)
	cuts.render(ctx_bot)
	bot_copper.render(ctx_bot)
	ctx_bot.color=(0,0,0)
	ctx_bot.drill_color=(0,0,0)
	if(drillintop==False):
		nc_drill.render(ctx_bot)
ctx_cuts = GerberCairoContext()
ctx_cuts.color = (1, 1, 1)
cuts.render(ctx_cuts)

if(Layers=='Top'):
	ctx=ctx_top
if(Layers=='Bot'):
	ctx=ctx_bot
if(Layers=='Both'):
	ctx=ctx_bot


ResX=2549
ResY=1470
xppm=19.608
yppm=19.608
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

def MakeGCODE(filename):
	with open('Out/tmp1/' + filename + '.gcode', 'w') as fout:
		with open('gcode/lycheeHat.gcode', 'r') as fin:
			lines = fin.readlines()
			fin.close()
			for l in lines:
				l2 = l.lstrip(';(')
				l2 = l2.rstrip(')\n')
				l2 = l2.strip('')
				l1 = l2.split('=')
				if (len(l1) < 2):
					fout.write(l)
				else:
					name = l1[0].strip()
					value = l1[1].strip()
					if (name in config_printer) == False:
						config_printer[name], units = GetValue(value)
					else:
						noused, units = GetValue(value)
					pl = name.ljust(22)
					if (name != 'Number of Slices'):
						fout.write(';(' + pl + '  = ' + str(config_printer[name]) + ' ' + units + '\n')
					else:
						fout.write(';' + pl + '  = ' + str(config_printer[name]) + ' ' + units + '\n')
			fin.close()
			# fout.write('G28\n')
			fout.write('G21 ;Set units to be mm\n')
			fout.write('G91 ;Relative Positioning\n')
			fout.write('M17 ;Enable motors\n')
			fout.write('<Slice> Blank\n')
			fout.write('M106 S0 ; UV off\n')
			fout.write(';--- Layer 0\n')
			fout.write(';<Delay> 1000\n')
			fout.write(';<Slice> 0\n')
			fout.write('M106 S255 ; UV on \n')
			fout.write(';<Delay> %d\n' %(Waiting*1000))
			fout.write('M106 S0; UV off\n')
			fout.write(';<Slice> Blank\n')
			fout.write(';<Delay> 500\n')
			# fout.write('G1 Z6 F60\n')
			# fout.write(';<Delay> 6000\n')
			# fout.write(';<Delay> 0\n')
			# fout.write('G1 Z-5.95 F120\n')
			# fout.write(';<Delay> 2975\n')
			fout.write(';--- Layer 1\n')
			fout.write(';<Delay> 1000\n')
			fout.write(';<Slice> 1\n')
			fout.write('M106 S255 ; UV on \n')
			fout.write(';<Delay> %d\n' %(Exposition*1000))
			fout.write('M106 S0 ; UV off \n')
			fout.write(';<Slice> Blank\n')
			fout.write('M18 ;Disable Motors\n')
			fout.close()
		fin.close()


if(Layers=='Both' or Layers=='Top'):
	MakeGCODE(fileName+'_F')
if(Layers=='Both' or Layers=='Bot'):
	MakeGCODE(fileName+'_B')


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


dimScreenX=ResX/xppm #mm
dimScreenY=ResY/yppm #mm


sizemmX = ctx.size_in_inch[0]  # *25.4
sizemmY = ctx.size_in_inch[1]  # *25.4
sizePxlX = ctx.size_in_pixels[0]
sizePxlY = ctx.size_in_pixels[1]
ScaleX = sizemmX/sizePxlX * ResX/dimScreenX
ScaleY = sizemmY/sizePxlY * ResY/dimScreenY
StartX= int((dimScreenX-sizemmX) /2.0 * ResX/dimScreenX)
StartY= int((dimScreenY-sizemmY) /2.0 * ResY/dimScreenY)



def makeImage(ctx, ctx_cats, mirror_layer, make_cuts_in_bk):
	pospxl=255
	negpxl=0
	if(Negative):
		pospxl = 0
		negpxl = 255

	print('Start image convert to png')
	fobj = BytesIO()
	ctx.surface.write_to_png(fobj)
	# with open('Out/'+fileName+'FullRes.png' ,'wb') as f:
	# 	f.write(fobj.getbuffer())
	# 	f.close()
	imageCTX = Image.open(fobj)
	fobj_cats = BytesIO()
	ctx_cats.surface.write_to_png(fobj_cats)
	imageCuts = Image.open(fobj_cats)
	# with open('Out/'+fileName+'FullResCuts.png' ,'wb') as f:
	# 	f.write(fobj_cats.getbuffer())
	# 	f.close()
	print('Make printer\'s image')
	#full resolution 3D printer screen image  - 2 layer
	imageRaw = Image.new("RGB", (ResY, ResX))
	draw = ImageDraw.Draw(imageRaw)
	draw.rectangle((0,0,ResY,ResX),fill=(0,0,0))
	draw.rectangle((StartY,StartX,StartY+sizePxlY*ScaleY,StartX+sizePxlX*ScaleX),fill=(negpxl,negpxl,negpxl))
	#image with resolution for mono 3D printer - 2 layer
	imageCWS = Image.new("RGB", (int(ResY/3),ResX))
	draw = ImageDraw.Draw(imageCWS)
	draw.rectangle((0,0,ResY,ResX),fill=(0,0,0))
	draw.rectangle((StartY,StartX,StartY+sizePxlY*ScaleY,StartX+sizePxlX*ScaleX),fill=(negpxl,negpxl,negpxl))
	#full resolution 3D printer screen background image- 1 layer
	imageRawBg = Image.new("RGB", (ResY, ResX))
	draw = ImageDraw.Draw(imageRawBg)
	draw.rectangle((0,0,ResY,ResX),fill=(0,0,0))
	draw.rectangle((StartY,StartX,StartY+sizePxlY*ScaleY,StartX+sizePxlX*ScaleX),fill=(255,255,255))
	draw.rectangle((StartY+1,StartX+1,StartY+sizePxlY*ScaleY-1,StartX+sizePxlX*ScaleX-1),fill=(0,0,0))
	#background image with  resolution for mono 3D printer - 1 layer
	imageCWSBg = Image.new("RGB", (int(ResY/3),ResX))
	draw = ImageDraw.Draw(imageCWSBg)
	draw.rectangle((0,0,int(ResY/3),ResX),fill=(0,0,0))
	draw.rectangle((int(StartY/3),StartX,int((StartY+sizePxlY*ScaleY)/3),StartX+sizePxlX*ScaleX),fill=(255,255,255))
	draw.rectangle((int(StartY/3)+1,StartX+1,int((StartY+sizePxlY*ScaleY)/3)-1,StartX+sizePxlX*ScaleX-1),fill=(0,0,0))
	treshold= 512
	WCTX, YCTX=imageCTX.size
	for  j in range(0,int(YCTX*ScaleY)-2,3):
		for i in range(int(WCTX * ScaleX)):
			if(mirror_layer==True):
				pxl1=imageCTX.getpixel((i/ScaleX, (j+0)/ ScaleY))
				pxl2=imageCTX.getpixel((i/ScaleX, (j+1)/ ScaleY))
				pxl3=imageCTX.getpixel((i/ScaleX, (j+2)/ ScaleY))
			else:
				pxl1 = imageCTX.getpixel((WCTX-1-i / ScaleX, (j + 0) / ScaleY))
				pxl2 = imageCTX.getpixel((WCTX-1-i / ScaleX, (j + 1) / ScaleY))
				pxl3 = imageCTX.getpixel((WCTX-1-i / ScaleX, (j + 2) / ScaleY))
			pxl1a=negpxl
			pxl2a=negpxl
			pxl3a=negpxl
			if((pxl1[0]+pxl1[1]+pxl1[2])>treshold):
				pxl1a=pospxl
				imageRaw.putpixel(((j+0)+StartY,i+StartX),(pospxl,pospxl,pospxl))
			if((pxl2[0]+pxl2[1]+pxl2[2])>treshold):
				pxl2a=pospxl
				imageRaw.putpixel(( (j+1) + StartY,i + StartX), (pospxl, pospxl, pospxl))
			if((pxl3[0]+pxl3[1]+pxl3[2])>treshold):
				pxl3a=pospxl
				imageRaw.putpixel(((j+2)+StartY,i+StartX),(pospxl,pospxl,pospxl))
			imageCWS.putpixel((int((j+StartY)/3),i+StartX),(pxl3a,pxl2a,pxl1a))
	if(make_cuts_in_bk):
		WCuts, YCuts = imageCuts.size
		for  j in range(0,int(YCuts*ScaleY)-2,3):
			for i in range(int(WCuts * ScaleX)):
				if(mirror_layer==True):
					pxl1=imageCuts.getpixel((i/ScaleX, (j+0)/ ScaleY))
					pxl2=imageCuts.getpixel((i/ScaleX, (j+1)/ ScaleY))
					pxl3=imageCuts.getpixel((i/ScaleX, (j+2)/ ScaleY))
				else:
					pxl1 = imageCuts.getpixel((WCuts - 1 - i / ScaleX, (j + 0) / ScaleY))
					pxl2 = imageCuts.getpixel((WCuts - 1 - i / ScaleX, (j + 1) / ScaleY))
					pxl3 = imageCuts.getpixel((WCuts - 1 - i / ScaleX, (j + 2) / ScaleY))
				pxl1a=negpxl
				pxl2a=negpxl
				pxl3a=negpxl
				if((pxl1[0]+pxl1[1]+pxl1[2])>treshold):
					pxl1a=pospxl
					imageRawBg.putpixel(((j+0)+StartY,i+StartX),(pospxl,pospxl,pospxl))
				if((pxl2[0]+pxl2[1]+pxl2[2])>treshold):
					pxl2a=pospxl
					imageRawBg.putpixel(( (j+1) + StartY,i + StartX), (pospxl, pospxl, pospxl))
				if((pxl3[0]+pxl3[1]+pxl3[2])>treshold):
					pxl3a=pospxl
					imageRawBg.putpixel(((j+2)+StartY,i+StartX),(pospxl,pospxl,pospxl))
				imageCWSBg.putpixel((int((j+StartY)/3),i+StartX),(pxl3a,pxl2a,pxl1a))
	imagePreviewMini=imageRaw.copy()
	imagePreviewMini.thumbnail((100,100), Image.ANTIALIAS)
	return imageRaw, imageRawBg, imageCWS, imageCWSBg, imagePreviewMini


if (Layers == 'Both' or Layers == 'Top'):
	imageRaw, imageRawBg, imageCWS, imageCWSBg, imagePreviewMini=makeImage(ctx_top,ctx_cuts, True, True)
	imageRaw.save('Out/tmp1/preview.png')
	imagePreviewMini.save('Out/tmp1/preview_mini.png')
	imageCWS.save('Out/tmp1/'+fileName+'_F001.png')
	# imageRawBg.save('Out/tmp1/'+fileName+'_B000.png')
	imageCWSBg.save('Out/tmp1/'+fileName+'_F000.png')

	csw = zipfile.ZipFile('Out/'+fileName+'_F.cws', 'w')
	csw.write('Out/tmp1/preview.png')
	csw.write('Out/tmp1/preview_mini.png')
	csw.write('Out/tmp1/'+fileName+'_F001.png')
	csw.write('Out/tmp1/'+fileName+'_F000.png')
	csw.write('Out/tmp1/'+fileName+'_F.gcode')
	csw.write('Out/tmp1/slice.conf')
	csw.close()

if (Layers == 'Both' or Layers == 'Bot'):
	imageRaw, imageRawBg, imageCWS, imageCWSBg, imagePreviewMini=makeImage(ctx_bot,ctx_cuts, False, False)
	imageRaw.save('Out/tmp1/preview.png')
	imagePreviewMini.save('Out/tmp1/preview_mini.png')
	imageCWS.save('Out/tmp1/'+fileName+'_B001.png')
	# imageRawBg.save('Out/tmp1/'+fileName+'_B000.png')
	imageCWSBg.save('Out/tmp1/'+fileName+'_B000.png')

	csw = zipfile.ZipFile('Out/'+fileName+'_B.cws', 'w')
	csw.write('Out/tmp1/preview.png')
	csw.write('Out/tmp1/preview_mini.png')
	csw.write('Out/tmp1/'+fileName+'_B001.png')
	csw.write('Out/tmp1/'+fileName+'_B000.png')
	csw.write('Out/tmp1/'+fileName+'_B.gcode')
	csw.write('Out/tmp1/slice.conf')
	csw.close()

imageRaw.show()
