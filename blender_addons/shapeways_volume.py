#!BPY

"""
Name: 'Shapeways Cost'
Blender: 248
Group: 'Object'
Tooltip: 'Calculate Shapeways cost based on volume'
"""

__author__="Loonsbury"
__url__=["blender.org", "shapeways.com"]
__version__="0.7"

__bpydoc__="""
"""

# --------------------------------------------------------------------------
# Shapeways Volume Calculator by Loonsbury (loonsbury@yahoo.com)
# --------------------------------------------------------------------------
# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****
# --------------------------------------------------------------------------

import Blender
import math
from Blender import *
from Blender.Mesh import *
from Blender.BGL import *
from Blender.Draw import *

#store: Scale, Material, Prices, VAT%, Mkup, Target Price, Target Scale, material details, 

GLOBALS={}
GLOBALS["vtot"]=0
GLOBALS["vtot2"]=0
GLOBALS["pcount"]=0
GLOBALS["qcount"]=0
GLOBALS["manifold"]=-1
GLOBALS["normals"]=-1
GLOBALS["selection"]=Blender.Object.GetSelected()
GLOBALS["l"]=len(GLOBALS["selection"])
GLOBALS["VAT"]=Create("0")
GLOBALS["mkup"]=Create("0")
GLOBALS["tdollars"]=Create("25")
GLOBALS["tscale"]=Create("100")
GLOBALS["se"]={}
GLOBALS["se"][4]=Create(0)
GLOBALS["se"][5]=Create(1)
GLOBALS["se"][6]=Create(0)
GLOBALS["se"][7]=Create(0)
GLOBALS["se"][8]=Create(0)
GLOBALS["se"][9]=Create(0)
GLOBALS["se"][10]=Create(1)
GLOBALS["se"][11]=Create(0)
GLOBALS["se"][12]=Create(0)
GLOBALS["se"][13]=Create(0)
GLOBALS["se"][20]=Create(0)
GLOBALS["se"][21]=Create(1)
GLOBALS["se"][22]=Create(1)
GLOBALS["se"][23]=Create(0)
GLOBALS["se"][24]=Create(0)
GLOBALS["obdim"]={}
GLOBALS["SCALE_EXPONENT"]=1
GLOBALS["SCALE_MULT"]=1
GLOBALS["mat"]=3
GLOBALS["EVENT_NONE"]=0
GLOBALS["EVENT_EXIT"]=1
GLOBALS["EVENT_REDRAW"]=2
GLOBALS["EVENT"]=GLOBALS["EVENT_REDRAW"]
GLOBALS["locx"]=0
GLOBALS["locy"]=0
GLOBALS["MATERIAL_INFO"]=[["Cream Robust",                Create(2.50)],
                          ["Transparent Detail",          Create(2.77)],
                          ["White Detail",                Create(2.89)],
                          ["White Strong & Flexible",     Create(1.50)],
                          ["White Strong & Flexible Dyed",Create(1.60)],
                          ["Black Detail",                Create(2.90)],
                          ["Stainless Steel Polished",    Create(10.00)]]

# Load settings from registry
def getKeys():
	global GLOBALS
	try:
		k=Blender.Registry.GetKey("shapeways_volume",False)
		if k:
			GLOBALS["VAT"].val=k["VAT"]
			GLOBALS["mkup"].val=k["mkup"]
			GLOBALS["tdollars"].val=k["tdollars"]
			GLOBALS["tscale"].val=k["tscale"]
			for i in range(4,12):
				GLOBALS["se"][i].val=0
			if k["scale"]==4:
				GLOBALS["se"][4].val=1
				GLOBALS["SCALE_EXPONENT"]=0.001
				GLOBALS["SCALE_MULT"]=0.1
			elif k["scale"]==5:
				GLOBALS["se"][5].val=1
				GLOBALS["SCALE_EXPONENT"]=1
				GLOBALS["SCALE_MULT"]=1
			elif k["scale"]==6:
				GLOBALS["se"][6].val=1
				GLOBALS["SCALE_EXPONENT"]=1000000
				GLOBALS["SCALE_MULT"]=100
			GLOBALS["se"][k["material"]].val=1
			for i in range(7,14):
				GLOBALS["MATERIAL_INFO"][i-7][1].val=k["matprice" + str(i-7)]
			for i in range(20,24):
				GLOBALS["se"][i].val=k["se" + str(i-7)]
		else:
			GLOBALS["se"][12].val=1
	except KeyError:
		print "Error loading registry data; likely due to new version, updating registry entry."
		k={}
		k["VAT"]=GLOBALS["VAT"].val
		k["mkup"]=GLOBALS["mkup"].val
		k["tdollars"]=GLOBALS["tdollars"].val
		k["tscale"]=GLOBALS["tscale"].val
		for i in range(4,7):
			if GLOBALS["se"][i].val==1:
				k["scale"]=i
		for i in range(7,14):
			if GLOBALS["se"][i].val==1:
				k["material"]=i
			k["matprice" + str(i-7)]=float(GLOBALS["MATERIAL_INFO"][i-7][1].val)
		for i in range(20,24):
			k["se" + str(i-7)]=float(GLOBALS["se"][i].val)
		Blender.Registry.SetKey("shapeways_volume",k,False)

# Save settings to registry
def saveKeys():
	global GLOBALS
	k={}
	k["VAT"]=GLOBALS["VAT"].val
	k["mkup"]=GLOBALS["mkup"].val
	k["tdollars"]=GLOBALS["tdollars"].val
	k["tscale"]=GLOBALS["tscale"].val
	for i in range(4,7):
		if GLOBALS["se"][i].val==1:
			k["scale"]=i
	for i in range(7,14):
		if GLOBALS["se"][i].val==1:
			k["material"]=i
		k["matprice" + str(i-7)]=float(GLOBALS["MATERIAL_INFO"][i-7][1].val)
	for i in range(20,24):
		k["se" + str(i-7)]=float(GLOBALS["se"][i].val)
	Blender.Registry.SetKey("shapeways_volume",k,False)

# Volume calculation subroutine
def getvolume():
	global GLOBALS
	extremes=[["",0,0],[0,0,0]]
	
	GLOBALS["vtot"]=0
	# Calculate BU volume
	if GLOBALS["l"] > 0:
		for i in range(0,GLOBALS["l"]):
			obj=GLOBALS["selection"][i]
			obname=obj.getName()
		 	vto=0
			if obj.getType()=='Mesh':
			 	obmesh=Mesh.Get(obj.getData(True,True))
				for f in obmesh.faces:
					fzn=f.no[2]
					# Scaled vert coordinates with object XYZ offsets for selection extremes/sizing
					x1=f.v[0].co[0] * obj.SizeX + obj.LocX
					y1=f.v[0].co[1] * obj.SizeY + obj.LocY
					z1=f.v[0].co[2] * obj.SizeZ + obj.LocZ
					x2=f.v[1].co[0] * obj.SizeX + obj.LocX
					y2=f.v[1].co[1] * obj.SizeY + obj.LocY
					z2=f.v[1].co[2] * obj.SizeZ + obj.LocZ
					x3=f.v[2].co[0] * obj.SizeX + obj.LocX
					y3=f.v[2].co[1] * obj.SizeY + obj.LocY
					z3=f.v[2].co[2] * obj.SizeZ + obj.LocZ
					GLOBALS["pcount"]+=1
					GLOBALS["qcount"]+=1
					if extremes[0][0]=="":
						extremes=[[x1,y1,z1],[x1,y1,z1]]
					pa=0.5*abs((x1*(y3-y2))+(x2*(y1-y3))+(x3*(y2-y1)))
					volume=((z1+z2+z3)/3.0)*pa
					# Allowing for quads
					if len(f)==4:
						GLOBALS["pcount"]+=1
						x4=f.v[3].co[0] * obj.SizeX + obj.LocX
						y4=f.v[3].co[1] * obj.SizeY + obj.LocY
						z4=f.v[3].co[2] * obj.SizeZ + obj.LocZ
						pa=0.5*abs((x1*(y4-y3))+(x3*(y1-y4))+(x4*(y3-y1)))
						volume+=(((z1+z3+z4)/3.0)*pa)
						extremes=[[min([x1,x2,x3,x4,extremes[0][0]]),min([y1,y2,y3,y4,extremes[0][1]]),min([z1,z2,z3,z4,extremes[0][2]])],[max([x1,x2,x3,x4,extremes[1][0]]),max([y1,y2,y3,y4,extremes[1][1]]),max([z1,z2,z3,z4,extremes[1][2]])]]
					else:
						extremes=[[min([x1,x2,x3,extremes[0][0]]),min([y1,y2,y3,extremes[0][1]]),min([z1,z2,z3,extremes[0][2]])],[max([x1,x2,x3,extremes[1][0]]),max([y1,y2,y3,extremes[1][1]]),max([z1,z2,z3,extremes[1][2]])]]
					if fzn < 0:
						fzn=-1
					elif fzn > 0:
						fzn=1
					else:
						fzn=0
					vto+=fzn * volume
				GLOBALS["vtot"]+=vto
			else:
				print obname, ': object must be a mesh.'
		GLOBALS["obdim"][0]=extremes[1][0]-extremes[0][0]
		GLOBALS["obdim"][1]=extremes[1][1]-extremes[0][1]
		GLOBALS["obdim"][2]=extremes[1][2]-extremes[0][2]

# Manifold Checks
def checkManifold():
	global GLOBALS
	GLOBALS["manifold"]=1
	if GLOBALS["l"] > 0:
		for i in range(0,GLOBALS["l"]):
			obj=GLOBALS["selection"][i]
			if obj.getType()=='Mesh':
			 	obmesh=Mesh.Get(obj.getData(True,True))
				mc=dict([(ed.key, 0) for ed in obmesh.edges])
				for f in obmesh.faces:
					for e in f.edge_keys:
						mc[e]+=1
						if mc[e]>2:
							GLOBALS["manifold"]=0
							return 0
				mt = [e[1] for e in mc.items()]
				mt.sort()
				if mt[0]<2:
					GLOBALS["manifold"]=0
					return 0
				if mt[len(mt)-1]>2:
					GLOBALS["manifold"]=0
					return 0

# Normal Checks
def checkNormals():
	global GLOBALS
	return 0

# Button/text events
def DRAW_set_event(e,v):
	global GLOBALS
	if e in (4,5,6):
		for k in [4,5,6]:
			if k!=e:
				GLOBALS["se"][k].val=0
			else:
				GLOBALS["se"][k].val=1
		if e==4:
			GLOBALS["SCALE_EXPONENT"]=0.001
			GLOBALS["SCALE_MULT"]=0.1
		elif e==5:
			GLOBALS["SCALE_EXPONENT"]=1
			GLOBALS["SCALE_MULT"]=1
		else:
			GLOBALS["SCALE_EXPONENT"]=1000000
			GLOBALS["SCALE_MULT"]=100
		GLOBALS["EVENT"]=GLOBALS["EVENT_REDRAW"]
	elif e in (7,8,9,10,11,12,13):
		for k in [7,8,9,10,11,12,13]:
			if k!=e:
				GLOBALS["se"][k].val=0
			else:
				GLOBALS["se"][k].val=1
		GLOBALS["mat"]=e-7
		GLOBALS["EVENT"]=GLOBALS["EVENT_REDRAW"]
	elif e==25:
		checkManifold()
		GLOBALS["EVENT"]=e
	elif e==26:
		checkNormals()
		GLOBALS["EVENT"]=e
	elif e==27:
		Blender.Registry.RemoveKey("shapeways_volume")
		GLOBALS["EVENT"]=e
	else:
		GLOBALS["EVENT"]=e

# Shortcut for drawing UI pieces
def drawElement(type,text,event,ox,oy,width,height,length,value,lo,context,defevent):
	global GLOBALS
	GLOBALS["locy"]-=25+lo
	if type==1:
		return Button(text,event,GLOBALS["locx"]+ox,GLOBALS["locy"]+oy+25+lo,width,height,context,defevent)
	elif type==2:
		return Label(text,GLOBALS["locx"]+ox,GLOBALS["locy"]+oy+25+lo,width,height)
	elif type==3:
		return Toggle(text,event,GLOBALS["locx"]+ox,GLOBALS["locy"]+oy+25+lo,width,height,value,context,defevent)
	elif type==4:
		return String(text,length,GLOBALS["locx"]+ox,GLOBALS["locy"]+oy+25+lo,width,height,value,length,context,defevent)

# Begin UI
def DRAW():
	global GLOBALS
	
	GLOBALS["vtot2"]=GLOBALS["vtot"]*GLOBALS["SCALE_EXPONENT"]
	line=20

	# Begin UI object definitions
	GLOBALS["locx"], GLOBALS["locy"]=[i/2 for i in Window.GetScreenSize()]
	GLOBALS["locx"]-=150
	height=180
	if GLOBALS["se"][20].val==1:
		height+=201
	if GLOBALS["se"][21].val==1:
		height+=290
	if GLOBALS["se"][22].val==1:
		height+=180
	if GLOBALS["se"][23].val==1:
		height+=100
	if GLOBALS["se"][24].val==1:
		height+=80
	GLOBALS["locy"]+=height/2

	drawElement(2,"Shapeways Calculator v" + __version__,0,0,0,300,10,0,0,5,'',0)

	# Info Section; usually hidden to save space
	GLOBALS["se"][20]=drawElement(3,"Information",20,0,0,300,20,0,GLOBALS["se"][20].val,0,'',DRAW_set_event)
	if GLOBALS["se"][20].val==1:
		drawElement(2,"Written by " + __author__ + " 2009",0,16,5,240,10,0,0,-5,'',0)
		drawElement(2,"Designed for use with",0,16,0,240,10,0,0,-8,'',0)
		drawElement(2,"     www.shapeways.com",0,16,0,240,10,0,0,0,'',0)
		drawElement(2,"Selected objects must be meshes,",0,16,0,240,10,0,0,-8,'',0)
		drawElement(2,"     manifold, and have correct normals",0,16,0,240,10,0,0,0,'',0)
		drawElement(2,"I offer no warranty for accuracy",0,16,0,240,10,0,0,0,'',0)
		drawElement(2,"All figures are for reference only",0,16,0,240,10,0,0,0,'',0)
		drawElement(2,"Final pricing will be calculated by",0,16,0,240,10,0,0,-8,'',0)
		drawElement(2,"     Shapeways",0,16,0,240,10,0,0,5,'',0)

	# General Section
	GLOBALS["se"][21]=drawElement(3,"General",21,0,0,300,20,0,GLOBALS["se"][21].val,0,'',DRAW_set_event)
	if GLOBALS["se"][21].val==1:
		drawElement(2,"Objects Selected: " + str(GLOBALS["l"]),0,16,5,160,10,0,0,-5,'',0)
		drawElement(2,"Blender Unit Scale",0,16,0,160,10,0,0,0,'',0)
		GLOBALS["se"][4]=drawElement(3,"mm",4,20,0,60,20,0,GLOBALS["se"][4].val,-25,'1 Blender Unit=1 millimetre',DRAW_set_event)
		GLOBALS["se"][5]=drawElement(3,"cm",5,82,0,60,20,0,GLOBALS["se"][5].val,-25,'1 Blender Unit=1 centimetre',DRAW_set_event)
		GLOBALS["se"][6]=drawElement(3,"m",6,144,0,60,20,0,GLOBALS["se"][6].val,0,'1 Blender Unit=1 metre',DRAW_set_event)
		drawElement(2,"Material",0,16,0,160,10,0,0,0,'',0)
		for i in range(7,14):
			GLOBALS["se"][i]=drawElement(3,GLOBALS["MATERIAL_INFO"][i-7][0],i,20,0,150,20,0,GLOBALS["se"][i].val,-25,'',DRAW_set_event)
			drawElement(2,"$",0,175,5,20,10,0,0,-25,'',0)
			GLOBALS["MATERIAL_INFO"][i-7][1]=drawElement(4,"",2,190,0,40,20,5,str(round(float(GLOBALS["MATERIAL_INFO"][i-7][1].val),2)),0,"Type a price for " + GLOBALS["MATERIAL_INFO"][i-7][0],DRAW_set_event)
		drawElement(2,"Price per cm3: $" + str(round(float(GLOBALS["MATERIAL_INFO"][GLOBALS["mat"]][1].val),2)),0,16,0,160,10,0,0,0,'',0)
		drawElement(2,"Dimensions:",0,16,0,160,10,0,0,-25,'',0)
		drawElement(2,"X:" + str(round(GLOBALS["obdim"][0]*GLOBALS["SCALE_MULT"],1)) + "cm",0,102,0,160,10,0,0,-5,'',0)
		drawElement(2,"Y:" + str(round(GLOBALS["obdim"][1]*GLOBALS["SCALE_MULT"],1)) + "cm",0,102,0,160,10,0,0,-5,'',0)
		drawElement(2,"Z:" + str(round(GLOBALS["obdim"][2]*GLOBALS["SCALE_MULT"],1)) + "cm",0,102,0,160,10,0,0,5,'',0)

	# Pricing Section
	bprice=round(GLOBALS["vtot2"]*float(GLOBALS["MATERIAL_INFO"][GLOBALS["mat"]][1].val),2)
	if GLOBALS["MATERIAL_INFO"][GLOBALS["mat"]][0]=="White Strong & Flexible":
		bprice=bprice+1.5
	if GLOBALS["MATERIAL_INFO"][GLOBALS["mat"]][0].find("Dyed")>=0:
		bprice=bprice+4.0
	vatprice=round(bprice*(float(GLOBALS["VAT"].val)/100),2)
	ivprice=bprice+vatprice
	mvatprice=round(float(GLOBALS["mkup"].val)*(float(GLOBALS["VAT"].val)/100),2)
	mkprice=round(float(GLOBALS["mkup"].val),2)
	totalprice=ivprice+mkprice+mvatprice
	GLOBALS["se"][22]=drawElement(3,"Pricing",22,0,0,300,20,0,GLOBALS["se"][22].val,0,'',DRAW_set_event)
	if GLOBALS["se"][22].val==1:
		drawElement(2,"Volume",0,16,5,100,10,0,0,-25,'',0)
		drawElement(2,str(round(GLOBALS["vtot2"],2)) + " cm3",0,131,5,70,10,0,0,-5,'',0)
		drawElement(2,"Base Price:",0,16,0,100,10,0,0,-25,'',0)
		drawElement(2,"$" + str(bprice),0,131,0,80,10,0,0,0,'',0)
		drawElement(2,"VAT:         %",0,16,0,100,10,0,0,-25,'',0)
		drawElement(2,"$" + str(vatprice),0,131,0,80,10,0,0,-25,'',0)
		GLOBALS["VAT"]=drawElement(4,"",2,50,0,30,20,3,GLOBALS["VAT"].val,0,"Type a percentage representing your locale's VAT",DRAW_set_event)
		drawElement(2,"Price Inc VAT:",0,16,0,100,10,0,0,-25,'',0)
		drawElement(2,"$" + str(ivprice),0,131,0,80,10,0,0,0,'',0)
		drawElement(2,"Markup:",0,16,0,100,10,0,0,-25,'',0)
		drawElement(2,"$",0,131,0,80,10,0,0,-25,'',0)
		GLOBALS["mkup"]=drawElement(4,"",2,143,-6,30,20,3,GLOBALS["mkup"].val,0,"Type a Dollar value for shop markup; leave at zero if this is your own print",DRAW_set_event)
		drawElement(2,"Markup VAT:",0,16,0,100,10,0,0,-25,'',0)
		drawElement(2,"$" + str(mvatprice),0,131,0,80,10,0,0,0,'',0)
		drawElement(2,"Total Price Inc VAT:",0,16,0,160,10,0,0,-25,'',0)
		drawElement(2,"$" + str(totalprice),0,131,0,80,10,0,0,5,'',0)

	# Scaling Section
	GLOBALS["se"][23]=drawElement(3,"Scaling (VAT Included)",23,0,0,300,20,0,GLOBALS["se"][23].val,0,'',DRAW_set_event)
	if GLOBALS["se"][23].val==1:
		drawElement(2,"Target Price:",0,16,0,100,10,0,0,-25,'',0)
		drawElement(2,"$",0,93,0,80,10,0,0,-25,'',0)
		GLOBALS["tdollars"]=drawElement(4,"",2,106,-6,80,20,8,GLOBALS["tdollars"].val,0,"Type a target Dollar value",DRAW_set_event)
		drawElement(2,"Scale:",0,16,0,100,10,0,0,-25,'',0)
		if (float(GLOBALS["tdollars"].val) > 0) and (GLOBALS["vtot2"] > 0) and ((bprice+vatprice) > 0):
			drawElement(2,str(round(((round(float(GLOBALS["tdollars"].val)-mkprice-mvatprice,2)/(bprice+vatprice)) ** (1/3.0))*100,3)) + "%",0,93,0,80,10,0,0,0,'',0)
		else:
			drawElement(2,"100%",0,93,0,80,10,0,0,0,'',0)
		drawElement(2,"Target Scale:",0,16,0,100,10,0,0,-25,'',0)
		GLOBALS["tscale"]=drawElement(4,"",2,97,-6,70,20,7,GLOBALS["tscale"].val,-25,"Type a target scale percentage",DRAW_set_event)
		drawElement(2,"%",0,168,0,15,10,0,0,0,'',0)
		drawElement(2,"Price:",0,16,0,100,10,0,0,-25,'',0)
		if (float(GLOBALS["tscale"].val) > 0) and (GLOBALS["vtot2"] > 0):
			drawElement(2,"$" + str(round((bprice+vatprice)*((float(GLOBALS["tscale"].val)/100) ** 3),2)+mkprice+mvatprice),0,93,0,80,10,0,0,0,'',0)
		else:
			drawElement(2,"$0",0,93,0,80,10,0,0,0,'',0)

	# Error Checking Section
	GLOBALS["se"][24]=drawElement(3,"Error Checks",24,0,0,300,20,0,GLOBALS["se"][24].val,0,'',DRAW_set_event)
	if GLOBALS["se"][24].val==1:
		drawElement(2,"Polygons:       " + str(GLOBALS["qcount"]),0,16,0,150,10,0,0,0,'',0)
		drawElement(2,"Polygons(tris): " + str(GLOBALS["pcount"]),0,16,5,150,10,0,0,-5,'',0)
		drawElement(1,"Manifold",25,16,-12,150,25,0,0,-20,'',DRAW_set_event)
		if GLOBALS["manifold"]==-1:
			drawElement(2,"Unchecked",0,170,0,100,10,0,0,5,'',0)
		elif GLOBALS["manifold"]==1:
			drawElement(2,"Good",0,170,0,100,10,0,0,5,'',0)
		else:
			drawElement(2,"BAD",0,170,0,100,10,0,0,5,'',0)
		#drawElement(1,"Normals",26,16,-5,150,25,0,0,5,'',DRAW_set_event)
		#if GLOBALS["normals"]==-1:
		#	drawElement(2,"Unchecked",0,170,0,100,10,0,0,5,'',0)
		#elif GLOBALS["normals"]==1:
		#	drawElement(2,"Good",0,170,0,100,10,0,0,5,'',0)
		#else:
		#	drawElement(2,"BAD",0,170,0,100,10,0,0,5,'',0)

	drawElement(1,"Exit",GLOBALS["EVENT_EXIT"],75,-30,150,40,0,0,0,'',DRAW_set_event)

# Start general processing
def main():
	global GLOBALS
	
	getKeys()
	getvolume()
		
	# Wait for exit
	while GLOBALS["EVENT"]!=GLOBALS["EVENT_EXIT"]:
		UIBlock(DRAW, 0)
	
	saveKeys()

if __name__=='__main__':
	main()
