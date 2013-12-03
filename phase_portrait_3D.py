'''
Plot Phase Portraits

Author  : Jithin B.P, jithinbp@gmail.com
License : GNU GPL version 3
Date : june-2012
'''

from widgets import *
import math,os,time,pygame,time,string,Tkinter
import numpy as np
import scipy
WIDTH=800
HEIGHT=650
YSHIFT=200
size = [WIDTH,HEIGHT]
flags=pygame.SRCALPHA|pygame.NOFRAME|pygame.HWSURFACE|pygame.HWACCEL
os.environ['SDL_VIDEO_WINDOW_POS'] = '300,100'

screen = pygame.display.set_mode(size,flags)
pygame.display.set_caption("lorenz attractor")
surf=[]
angles=40
for a in range(angles):
	surf.append(pygame.Surface(size,flags))

surf_behind=[]
for a in range(angles):
	surf_behind.append(pygame.Surface(size,flags))

stability=pygame.Surface(size,flags)
scale=50.0
spacing=10
x=px=0
y=py=0



#stable orbit
#scale=50.0
r=10
scale=25.0
radius=5
	

xaxis=[]
yaxis=[]
zaxis=[]

cls=[]

x_axis=[]
y_axis=[]
z_axis=[]
previous_position=[]

def qqt():
	global running
	running=False
	
ll=0

t=time.time()
running=True
buttons=[]

b=button(5,5,'quit',10,'red',qqt)
b.fontsize=int(18)
b.reconfigure()
quit_id=b.id
b.bg='blue'
b.highlight=True
b.transparency=250
b.fontcolor='red'
b.border=True
buttons.append(b)

b=button(35,5,'clear',10,'red')
b.fontsize=int(18)
b.reconfigure()
b.bg='blue'
b.highlight=True
b.toggle=False
b.transparency=250
b.fontcolor='red'
b.border=True
clr=b
buttons.append(b)

b=button(105,5,'simulate',10,'red')
b.fontsize=int(18)
b.reconfigure()
b.bg='blue'
b.highlight=True
b.transparency=250
b.fontcolor='red'
b.border=True
simul=b
buttons.append(b)


v=button(70,5,'view',10,'red')
v.fontsize=int(18)
v.reconfigure()
v.bg='blue'
v.highlight=False
v.transparency=250
v.fontcolor='red'
v.border=True
buttons.append(v)

space=button(WIDTH-80,10,'spaced',10,'red')
space.fontsize=int(18)
space.reconfigure()
space.bg='blue'
space.highlight=False
space.transparency=250
space.fontcolor='red'
space.border=True
buttons.append(space)

rtt=slider(5,27,'Rotation',0,0,angles-1,150)
buttons.append(rtt)

slid=slider(WIDTH-200,10,'Resolution',1,1,10)
buttons.append(slid)

timestep=slider(WIDTH-200,40,'timestep',1,1,100,150)
buttons.append(timestep)

crds=label(30,5,'0')
buttons.append(crds)

getat=label(200,5,'none')
buttons.append(getat)


b=button(5,HEIGHT-20,'CHANGE EQUATIONS',10,'lightgreen')
b.fontsize=int(18)
b.reconfigure()
b.bg='blue'
b.highlight=True
b.toggle=False
b.transparency=250
b.fontcolor='red'
b.border=True
set_equation=b
buttons.append(b)

b=button(155,HEIGHT-20,'SHADE DEPTH?',10,'lightgreen')
b.fontsize=int(18)
b.reconfigure()
b.bg='blue'
b.highlight=False
b.toggle=True
b.transparency=200
b.fontcolor='red'
b.border=True
shade_depth=b
buttons.append(b)

def solve(eq,x,y,z,r):
	eq=string.replace(eq,'x',str(x))
	eq=string.replace(eq,'y',str(y))
	eq=string.replace(eq,'z',str(z))
	return eval(eq)

deriv=lambda eq,x,y,z,r:solve(eq,x,y,z,r)
dxtext='10*y-10*x'
dytext='r*x-y-x*z'
dztext='x*y-8.0*z/3'


def dnewxy(x,y,z):
	global dt,scale,slid,dxtext,dytext,dztext
	
	
	x2=deriv(dxtext,x,y,z,r)
	y2=deriv(dytext,x,y,z,r)
	z2=deriv(dztext,x,y,z,r)
	velocity=math.sqrt(x2*x2+y2*y2)
	sc=max([abs(x2),abs(y2),abs(z2)])/(2.0)    #*slid.val
	dt=1.0/abs(scale*sc)
	
	if dt>scale:
		stop=True
	else:
		stop=False
		
	return x2*dt,y2*dt,z2*dt,stop,velocity
	


midx=WIDTH/2
midy=HEIGHT/2
font=pygame.font.Font(None,18)
markings=[(midx+300,midy),(midx,midy-300),(midx-300,midy),(midx,midy+300)]

buttons.append(label(markings[0][0],markings[0][1],'%.3f'%(300/scale))  )
buttons.append(label(markings[1][0],markings[1][1],'%.3f'%( (-300+YSHIFT)/scale))  )
buttons.append(label(markings[2][0],markings[2][1],'%.3f'%(300/scale))  )
buttons.append(label(markings[3][0],markings[3][1],'%.3f'%( (300+YSHIFT)/scale))  )

	
rt=2*math.pi/angles
def blitgraph():
	for m in range(angles):
		surf[m].fill(colors['black'])
		blk=list(colors['black'])
		blk[3]=0
		surf_behind[m].fill(blk)
		for a in markings:
			pygame.draw.circle(surf[m],colors['red'],a,3)
		for a in range(-300,300,30):
			for b in range(-300,300,5):
				surf[m].set_at((midx+a,midy+b),colors['red'])
		for b in range(-300,300,30):
			for a in range(-300,300,5):
				surf[m].set_at((midx+a,midy+b),colors['red'])
		txt3=font.render('Angle is%.3f'%(rt*m*180/math.pi),1,colors['red'])
		surf[m].blit(txt3,(10,50))

blitgraph()

run=False

avgy=[]
avgz=[]
MAXVEL=	4   #Set maximum velocity here
MAXX=0.1
MINX=-0.1
VELOCITYPLOT=False

def cart2sph(x,y,z):
    XsqPlusYsq = x**2 + y**2
    r = math.sqrt(XsqPlusYsq + z**2)               # r
    elev = math.atan2(z,math.sqrt(XsqPlusYsq))     # theta
    az = math.atan2(y,x)                           # phi
    return r, elev, az

def sph2cart(r,elev,az):
	x=r*math.cos(elev)*math.cos(az)
	y=r*math.cos(elev)*math.sin(az)
	z=r*math.sin(elev)
	return x,y,z

def distance(a,b):
	return math.sqrt( (a[0]-b[0])*(a[0]-b[0]) + (a[1]-b[1])*(a[1]-b[1])  )
	

an=0
autorotate=True
angle=0
last_time=time.time()
total_steps=0
while running:
	event = pygame.event.poll()
	pygame.event.clear()
	c=0
	if event.type == pygame.QUIT:
		running = 0
		continue
	elif event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONDOWN:  #evaluate mouse gestures here
		x,y= pygame.mouse.get_pos()
		cs=surf[0].get_at((x,y))
		if cs!=colors['black']:
			getat.txt='velocity here = '+str(cs[2]*MAXVEL/255.0)
	elif event.type == pygame.KEYDOWN:			#get keypresses
		c=pygame.key.name(event.key)

	try:
		ll=event.button
	except:
		if c:ll=c
		else: ll=0			#ll = 0 for mousemotion, 1 for click, 4,5 for scroll


	if event.type!=pygame.MOUSEBUTTONUP:
		a=check(buttons,x,y,ll)					#returns the toggled button(command/action already executed)
	else:
		a=1

	if ll==1 and a==set_equation:
		try:
			import Tkinter
			root=Tkinter.Tk()
			dx=Tkinter.StringVar()
			dy=Tkinter.StringVar()
			dz=Tkinter.StringVar()
			dx.set(dxtext)
			dy.set(dytext)
			dz.set(dztext)
			def final():
				global dxtext,dytext,dztext
				try:
					t=dx.get()
					solve(t,1,1,1,1)
					dxtext=t
					t=dy.get()
					solve(t,1,1,1,1)
					dytext=t
					t=dz.get()
					solve(t,1,1,1,1)
					dztext=t
					root.destroy()
				except:
					pass
				
			Tkinter.Label(root,text='dx= ').pack(side=Tkinter.LEFT)
			Tkinter.Entry(root,textvariable=dx).pack(side=Tkinter.LEFT)
			Tkinter.Label(root,text='   dy= ').pack(side=Tkinter.LEFT)
			Tkinter.Entry(root,textvariable=dy).pack(side=Tkinter.LEFT)
			Tkinter.Label(root,text='   dz= ').pack(side=Tkinter.LEFT)
			Tkinter.Entry(root,textvariable=dz).pack(side=Tkinter.LEFT)
			Tkinter.Button(root,text='SET',command=final).pack(side=Tkinter.LEFT)
			root.mainloop()

		except:
			pass
		a=clr
	
	if ll==1 and a==clr:
		run=False
		total_steps=0
		xaxis=[]
		yaxis=[]
		x_axis=[]
		y_axis=[]
		previous_position=[]
		
		zaxis=[]
		cls=[]
		MINX=-0.1
		MAXX=0.1
		crds.txt=str( len(xaxis) )

		blk=list(colors['black'])
		blk[3]=0
		blitgraph()
		
		
	if (ll==1 or pygame.mouse.get_pressed()[0]==1) and (px!=x or py!=y or v.highlight) and a==False :
		rot=an*rt
		yy=(x-midx)/scale
		zz=(y-midy+YSHIFT)/scale
		xx=cart2sph(0,yy,zz)
		txx=sph2cart(xx[0],xx[1],xx[2]-rot)
		yaxis.append(txx[1])
		zaxis.append(txx[2])
		xaxis.append(txx[0])
		if txx[1]<0:
			cls.append(list(colors['cyan']))
		else:
			cls.append(list(colors['magenta']))
		avgy.append([1,1,1,1])
		avgz.append([1,1,1,1])
		px=x
		py=y
		run=True
		#surf[0].set_at((x,y),colors['magenta'])
		initpos=[]
		for m in range(angles):
				xx=cart2sph(xaxis[-1],yaxis[-1],zaxis[-1])
				txx=sph2cart(xx[0],xx[1],xx[2]+rt*m)
				#xx=cart2sph(txx[0],txx[1],txx[2])
				#txx=sph2cart(xx[0],xx[1],xx[2]+rt*m)
				surf[m].set_at((int(txx[1]*scale)+midx,int(txx[2]*scale)+midy-YSHIFT),colors['magenta'])	
				crds.txt=str( len(xaxis) )
				initpos.append( (int(txx[1]*scale)+midx,int(txx[2]*scale)+midy-YSHIFT ))
		previous_position.append(initpos)


	if a==False:
		if ll==4:an+=1
		if ll==5:an-=1
		if an==angles:an=0
		elif an==-1: an =angles-1
		rtt.val=an
	elif a==rtt:
		if ll!=0:
			v.highlight=False
		an=int(rtt.val)

			
	if run:
		if v.highlight and (time.time()-last_time)>timestep.val/1000.0:
			an+=1
			last_time=time.time()

			if an>angles-1:
				an=0
			elif an<0:
				an=angles-1
			
			rtt.val=an
		if simul.highlight==True:
		  total_steps+=1
		  crds.txt = '%d [ %d ],depth E [%d,%d] '%(len(xaxis),total_steps,int(MAXX),int(MINX))
		  for a in range(len(xaxis)):
			dxtmp,dytmp,dztmp,stop,velocity=dnewxy(xaxis[a],yaxis[a],zaxis[a])
			xaxis[a]+=dxtmp
			yaxis[a]+=dytmp
			zaxis[a]+=dztmp

			if not (stop):
				
				cl=list(cls[a])
				resolution=int(slid.val)
				spacing=space.highlight
				for m in range(angles):
					xx=cart2sph(xaxis[a],yaxis[a],zaxis[a])
					txx=sph2cart(xx[0],xx[1],xx[2]+rt*m)
					if MAXX<txx[0]:MAXX=txx[0]
					elif MINX>txx[0]:MINX=txx[0]
					if distance(previous_position[a][m],(int(txx[1]*scale)+midx,int(txx[2]*scale)+midy-YSHIFT ) ) < resolution:
						continue

					per=1.0 #(txx[0]+50)/50.0
					if shade_depth.highlight:
						cl[3]=int(255*(txx[0]+MAXX)/(2.0*MAXX))
						if cl[3]<10: cl[3]=10
						elif cl[3]>255: cl[3]=255
					#print previous_position,xaxis,len(xaxis),len(previous_position)
					newpos=(int(txx[1]*scale)+midx,int(txx[2]*scale)+midy-YSHIFT )
					if txx[0]<0:
							pygame.draw.line(surf[m],cl,previous_position[a][m],newpos ,1 )
					else:
							pygame.draw.line(surf_behind[m],cl,previous_position[a][m],newpos,1)
					
					previous_position[a][m]=newpos
			


	pygame.draw.line(surf[an],colors['cyan'],(midx,0),(midx,HEIGHT),1)
	pygame.draw.line(surf[an],colors['cyan'],(0,midy),(WIDTH,midy),1)

	crds.x=x-10
	crds.y=y-30
		
	screen.fill(colors['black'])
	screen.blit(surf[an],(0,0))
	screen.blit(surf_behind[an],(0,0))

	screen.blit(stability,(0,0))
	for b in buttons:
		b.renew(screen)
	pygame.display.flip()








