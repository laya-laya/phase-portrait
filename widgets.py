'''
Widget library for python-pygame

Author  : Jithin B.P, jithinbp@gmail.com
License : GNU GPL version 3
Date : may-2012
'''

import pygame, time,os
from pygame.color import THECOLORS as colors
from math import pi
import numpy as np
from scipy import interpolate

selected_label=None
pygame.font.init()
font = pygame.font.Font(None, 18)
sfont = pygame.font.Font(None, 15)


MOUSEHELD=False
total_items=0
ontop_id=-1

def sine_erf(p,y,x):					
	return y - p[0] * np.sin(2*pi*p[1]*x+p[2])+p[3]
	
def sine_eval(x,p):			# y = a * sin(2*pi*f*x + phi)+ offset
	return p[0] * np.sin(2*pi*p[1]*x+p[2])-p[3]

def check(b,x,y,mouseclick):
	global ontop_id
	for a in reversed(b):
		if a.inside(x,y,mouseclick):
			if(ontop_id!=a.id):
				b.remove(a)
				b.append(a)
				ontop_id=a.id
			return a
	return False

def get_object(b,identification):
	'''return a widget from widget list b
	based on unique id passed'''
	for a in b:
		if a.id==identification:
			return a
	return False
	
def hide(b,surf,speed=3,slideright=True):
	'''b is a widget
	this function shows an animated slide out of the widget
	sets visibility to False in the end'''
	width=b.width
	wt=width
	x=b.x
	while b.width:
		b.clear_region(surf)
		wt-=speed
		b.width=int(wt)
		if slideright: b.x=(x+width-wt)
		b.renew(surf)
		pygame.display.flip()
	b.width=width
	b.x=x
	b.visible=False
		
def show(b,surf,speed=3,slideright=True):
	'''b is a widget
	this function shows an animated slide in of the widget
	sets visibility to True in the end'''
	b.visible=True
	width=b.width
	wt=0
	x=b.x
	b.width=0
	b.x+=width
	while b.width<width:
		b.clear_region(surf)
		wt+=speed
		b.width=int(wt)
		b.x=(x+width-b.width)
		b.renew(surf)
		pygame.display.flip()
	b.width=width
	b.x=x

def play_movie(x=0,y=0,name='Losing grip.mpg'):
	'''plays a video file'''
	
	print 'clicck'
	size=[320,240]
	flags=pygame.SRCALPHA|pygame.HWSURFACE|pygame.HWACCEL
	os.environ['SDL_VIDEO_WINDOW_POS'] = str(x)+','+str(y)
	screen = pygame.display.set_mode(size,flags)
	pygame.display.set_caption("test")
	mov=pygame.movie.Movie(name)
	mov.set_display(screen)
	mov.play()
	while(mov.get_busy()):
		pass

def rect(surf,x,y,width,height,color,transparency):
	'''draws a shaded rectangle in the region defined by
	x,y,width,height using smaller rectangles on surface 
	surf and transparency varying from 0 to limit. 
	invert decides the direction of the gradient
	'''	
	for ll in range(0,width-3,3):
		color[3]=int(transparency*float(ll)/(width-4))
		pygame.draw.rect(surf,color,(x,y,ll+3,height),3) #blit box

def rect_line(surf,x,y,width,height,color,limit=255,invert=False):
	'''draws a shaded rectangle in the region defined by
	x,y,width,height on surface surf and transparency
	varying from 0 to limit. invert decides the direction
	of the gradient
	'''
	for ll in range(0,width,3):
		color[3]=int(limit*float(ll)/width)
		if(invert):
			color[3]=limit-color[3]
		pygame.draw.line(surf,color,(x+ll,y),(x+ll,y+height),3)

class graph:
	def __init__(self,x,y,width,height,color='white'):
		'''This widget can plot 2-D data and also has inbuilt controls for
		curve fitting , interpolation , saving plots , and labelling peaks.
		
		Viewing plots requires Eye of Gnome to be installed.
		
		functions defined:
		self.clear_region(surf) - fills surf with black , rubbing out this widget only
		self.renew(surf) - draws everythin on surf( pygame.surface) passed 
		self.plot(xaxis,yaxis) -plot the data [xaxis scales but yaxis is fixed based on self.unit_length]
		self.inside(x,y,b) - x,y are mouse coordinates on parent surface. b is event id
		if mouseover , b=0
		if mouseclick , b=event.button
		if keypress , b=ASCII value
		'''
		global total_items
		total_items+=1
		self.visible=True
		self.id=total_items
		self.help=''
		self.type='graph'
		self.x=x
		self.color=list(colors[color])
		self.tracecolor=list(colors[color])
		self.transparency=20
		self.seethrough=1
		self.y=y
		self.unit_scale=1.0
		self.dy=1
		self.dx=1
		self.width=width
		self.height=height
		self.gh=height-48
		self.xgap=20
		self.gw=width-self.xgap
		self.fontcolor=colors['white']
		self.xaxis_text='ihgkjfdhg -->>'
		self.yaxis_text='yaxis -->>'
		self.xval=0
		self.yval=0
		self.coords=''
		self.mx=0
		self.my=0
		self.ln=0
		self.capture=False
		self.filename='screenshot.png'
		self.select_file_width=120
		self.controls=[]
		self.make_room=False
		xright=self.width-5
		scale=1.0
		spacing=10
		self.yaxis=np.array([])
		self.xaxis=np.array([])
		

		#save plot button
		b=button(1,5,'save plot',10,'red')
		b.fontsize=int(18*scale)
		b.reconfigure()
		b.x=xright-b.width-spacing
		b.y=self.height-20
		b.bg='blue'
		b.highlight=True
		b.toggle=False
		b.transparency=250
		b.fontcolor='red'
		self.save_button=b
		self.controls.append(b)
		
		#show saved images button
		b=button(1,5,'saved plots',10,'red')
		b.fontsize=int(15*scale)
		b.reconfigure()
		b.x=2
		b.y=self.height-17
		b.bg='blue'
		b.highlight=False
		b.border=True
		b.transparency=250
		b.fontcolor='red'
		self.file_button=b
		self.controls.append(b)

		#filename button
		tt=entry(5,self.height-35,'Filename : ','darkgreen')
		tt.help='enter filename to save plot to'
		tt.reconfigure()
		self.filename_entry=tt
		self.controls.append(tt)

		items=os.listdir('./plots/')
		if len(items)==0:
			items.append('none saved yet')
		b=selection_menu(5,5,items,'white')
		b.fontsize=15
		b.fixed_width=80
		b.reconfigure()
		b.transparency=170
		b.bg='orange'
		b.visible=False
		self.images_menu=b
		self.controls.append(b)

	def clear_region(self,surf):
		if self.capture:
			if self.filename!='':
				surface=surf.subsurface((self.x,self.y,self.width+2,self.height))
				pygame.image.save(surface,'plots/'+self.filename)
				self.capture=False
		surf.fill(colors['black'],(self.x,self.y,self.width+2,self.height))
		
		
	def renew(self,surf,scale=1):
		if not self.visible:
			return False
			
		if self.make_room:
			if self.xgap<self.select_file_width:
				self.xgap+=5
				self.gw=self.width-self.xgap
			else:
				self.images_menu.visible=True
				self.xgap=self.select_file_width
				items=os.listdir('./plots/')
				if len(items)==0:
					items.append('none saved yet')
				self.images_menu.items=items
				self.images_menu.num=len(items)
				self.images_menu.selection=items[0]
				self.images_menu.reconfigure()
		elif not self.make_room:
			self.images_menu.visible=False
			if self.xgap>20:
				self.xgap-=5
				self.gw=self.width-self.xgap
			else:
				self.xgap=20
				self.make_room=False
				self.file_button.highlight=False

		surface=pygame.Surface((self.width,self.height),pygame.SRCALPHA)
		self.color[3]=150
		pygame.draw.rect(surface,self.color,(0,0,self.width,self.height),1) #blit box
		if self.seethrough: self.color[3]=self.transparency
		
		rect(surface,self.xgap,3,self.gw-3,self.gh,self.color,self.transparency)
		text=sfont.render(self.yaxis_text,1,self.fontcolor)
		text=pygame.transform.rotate(text,90)
		surface.blit(text,(self.xgap-7,self.height/2-20) )
		a=0

		self.text=sfont.render(self.coords,1,self.fontcolor)
		surface.blit(self.text,(self.xgap,self.gh-10) )
		text=sfont.render(self.xaxis_text,1,self.fontcolor)
		surface.blit(text,(self.width/2,self.gh+15) )
		for b in self.controls:
			b.renew(surface)
		surf.blit(surface,(self.x,self.y))
		self.plot(surf)

	def plot(self,surf):
		if not self.visible:
			return False
		xaxis=self.xaxis
		yaxis=self.yaxis
		if len(xaxis) != len(yaxis):
			print "different array lengths for plotting : abort"
			return
		surface=pygame.Surface((self.width,self.height),pygame.SRCALPHA)
		self.ln=len(xaxis)
		if(len(self.yaxis)>2):
			print 'asdsa'
			self.dy=(self.gh)/(max(yaxis)-min(yaxis))
			self.dx=float(self.gw-1)/abs(xaxis[-1]-xaxis[0])

			self.color[3]=255
			pygame.draw.line(surface,self.color,(self.xgap,self.gh/2),(self.width,self.gh/2))
			

		if self.ln>2:
			xoffset=xaxis[0]						#for calculating coordinates while plotting
			a=xaxis[0]
			dx=float(xaxis[-1]-xaxis[0])
			while a<=xaxis[-1]:				#markings & text on xaxis
				xp=int( ( (float(a)-xaxis[0])/dx )*self.gw+self.xgap)
				surface.set_at((xp,self.gh),self.fontcolor)
				txt=sfont.render('%.2f'%(a),1,self.fontcolor,colors['black'])
				surface.blit(txt,(xp-7,self.gh+3) )
				a+=dx/10.0
			print self.ln
			for a in range(self.ln):								#make plottable list from numpy array
				yp=self.gh/2-int(yaxis[a]*self.dy)
				xp=int( (xaxis[a]-xoffset)*self.dx+self.xgap)
				if yp >self.gh-1:yp=self.gh-1
				elif yp<0:yp=0
				surface.set_at((xp,yp),self.tracecolor)
		surf.blit(surface,(self.x,self.y))
		

	def update(self):
		pygame.display.update((self.x,self.y,self.width,self.height))
	
	def inside(self,x,y,b):
		global MOUSEHELD,screen
		if not self.visible:
			return False
		if x>self.x and x< self.x+self.width and y>self.y and y<self.y+self.height and MOUSEHELD==False:
			self.mx=x-self.x-self.xgap
			self.my=y-self.y-self.gh/2
			if b==1:
					self.xaxis=np.insert(self.xaxis,0,self.mx)
					self.yaxis=np.insert(self.yaxis,0,self.my)
					print 'asdsa'
			a=check(self.controls,x-self.x,y-self.y,b)
			self.help='plot window'
			if a:
				self.help=a.help
			if a and b==1:
				if a==self.save_button:
					self.filename=self.filename_entry.get()
					self.capture=True
				elif a==self.file_button:				
					self.make_room=not self.make_room
				elif a==self.images_menu:
					if a.highlighted!=-1:
						os.system('eog'+' ./plots/'+a.selection)
						print 'asdas'
						self.make_room=False
					

					
			self.xval=(x-self.x-self.xgap)/self.dx
			self.yval=-(y-self.y-self.height/2+10)/self.dy
			self.coords='%.3f %.3f'%(self.xval,self.yval)
			
			return True
		else:
			self.coords=''
			self.mx=self.gw-1
			return False

class button:
	def __init__(self,x,y,text,width=0,color='white',command=None):
		global total_items
		total_items+=1
		self.visible=True
		self.id=total_items
		self.type='button'
		self.x=x
		self.color=list(colors[color])
		self.transparency=240
		self.y=y
		self.txt=text
		self.fontcolor=colors['white']
		self.bg='blue'
		self.text=font.render(text,1,self.fontcolor)
		self.width,self.height=font.size(text)
		self.width+=4
		self.height+=4
		if width>self.width :self.width=width
		self.command=command
		self.border=False
		self.highlight=False
		self.border_thickness=1
		self.fontsize=22
		self.toggle=True
		self.help=''
	def reconfigure(self):
		tmpfont = pygame.font.Font(None, self.fontsize)
		self.text=tmpfont.render(self.txt,1,self.color)
		self.width,self.height=tmpfont.size(self.txt)
		self.width+=2
		self.height+=2
		
	def clear_region(self,surf):
		if not self.visible:
			return False
		surf.fill(colors['black'],(self.x,self.y,self.width,self.height))
		
	def renew(self,surf,scale=1):
		if not self.visible:
			return False
		surface=pygame.Surface((self.width,self.height),pygame.SRCALPHA)
		if self.highlight:
			bg=list(colors[self.bg])
			rect_line(surface,0,0,self.width,self.height,bg,self.transparency,True)
		if self.border:
			color=self.color
			color[3]=255
			pygame.draw.rect(surface,color,(0,0,self.width,self.height),self.border_thickness) #blit box
			pygame.draw.rect(surface,colors['black'],(1,1,self.width-2,self.height-2),1) #blit box
		surface.blit(self.text,(2,2))
		if scale!=1:
			surface=pygame.transform.smoothscale(surface,(int(self.width*scale),int(self.height*scale) ) )
		surf.blit(surface,(self.x,self.y))
	def update(self):
		pygame.display.update((self.x,self.y,self.width,self.height))
	
	def inside(self,x,y,b):
		global MOUSEHELD
		if not self.visible:
			return False
		if x>self.x and x< self.x+self.width and y>self.y and y<self.y+self.height and MOUSEHELD==False:
			if b==1:
				if self.toggle: self.highlight=not self.highlight
				try:
					self.command()
				except:
					pass
			return True
		else:
			return False

class label:
	def __init__(self,x,y,text,color='white'):
		global total_items
		total_items+=1
		self.id=total_items
		self.type='label'
		self.visible=True
		self.x=x
		self.cx=0  #cursor coords if clicked
		self.cy=0
		self.color=list(colors[color])
		self.transparency=10
		self.fontcolor=list(colors[color])
		self.fontsize=18
		self.y=y
		self.py=y
		self.px=x
		self.txt=text
		self.help=''
		self.locked=False
		self.text=font.render(text,1,self.color)
		self.width,self.height=font.size(text)
		self.font = pygame.font.Font(None, self.fontsize)
		self.bg='gray'
		self.transparency=170
	def clear_region(self,surf):
		if not self.visible:
			return False
		if MOUSEHELD==self.id:
			surf.fill(colors['black'],(self.px,self.py,self.width+4,self.height+4))
		surf.fill(colors['black'],(self.x,self.y,self.width+4,self.height+4))
	
	def reconfigure(self):
		self.font = pygame.font.Font(None, self.fontsize)
		self.text=self.font.render(self.txt,1,self.color)
		self.width,self.height=self.font.size(self.txt)
		self.width+=4
		self.height+=4

	def renew(self,surf,scale=1):
		if not self.visible:
			return False
		self.color[3]=self.transparency
		self.text=font.render(self.txt,1,self.color)
		self.width,self.height=self.font.size(self.txt)
		surface=pygame.Surface((self.width+4,self.height+4),pygame.SRCALPHA)
		bg=list(colors[self.bg])
		rect_line(surface,0,0,self.width+4,self.height+4,bg,self.transparency,0) #blit box
		self.text=self.font.render(self.txt,1,self.color)
		surface.blit(self.text,(2,2))
		surface=pygame.transform.smoothscale(surface, (int((self.width+4)*scale),int((self.height+4)*scale)) )
		surf.blit(surface,(self.x,self.y))

	def update(self):
		if not self.visible:
			return False
		if self.grabbed:
			pygame.display.update((self.px,self.py,self.width+4,self.height+4))
		pygame.display.update((self.x,self.y,self.width+4,self.height+4))

	def inside(self,x,y,b):
		if not self.visible:
			return False
		global MOUSEHELD
		if pygame.mouse.get_pressed()[0]==1 and MOUSEHELD==self.id:
				self.px=self.x
				self.py=self.y
				self.x=x-self.cx
				self.y=y-self.cy
		elif MOUSEHELD==self.id:
			MOUSEHELD=False

		if x>self.x and x< self.x+self.width+4 and y>self.y and y<self.y+self.height+4 and (MOUSEHELD==False or MOUSEHELD==self.id) :
			if self.locked==False and b==1:
					self.cx=x-self.x
					self.cy=y-self.y
					MOUSEHELD=self.id
			return True
		else:
			return False

class entry:
	def __init__(self,x,y,text,color='white'):
		global total_items
		total_items+=1
		self.id=total_items
		self.type='label'
		self.visible=True
		self.x=x
		self.color=list(colors[color])
		self.transparency=10
		self.fontcolor=list(colors[color])
		self.highlight=False
		self.fontsize=18
		self.y=y
		self.txt=text
		self.help=''
		self.text=font.render(text,1,self.color)
		self.initial_len=len(text)
		self.width,self.height=font.size(text)
		self.init_width=self.width
		self.font = pygame.font.Font(None, self.fontsize)
		self.bg='gray'
		self.transparency=250
	def clear_region(self,surf):
		if not self.visible:
			return False
		surf.fill(colors['black'],(self.x,self.y,self.width+4,self.height+4))
	
	def reconfigure(self):
		self.font = pygame.font.Font(None, self.fontsize)
		self.text=self.font.render(self.txt,1,self.color)
		self.width,self.height=self.font.size(self.txt)
		self.width+=4

	def renew(self,surf,scale=1):
		if not self.visible:
			return False
		self.color[3]=self.transparency
		surface=pygame.Surface((self.width+4,self.height+4),pygame.SRCALPHA)
		bg=list(colors[self.bg])
		if self.highlight:rect_line(surface,0,0,self.width+4,self.height+4,bg,self.transparency,0) #blit box
		self.text=self.font.render(self.txt,1,self.color)
		surface.blit(self.text,(2,2))
		surface=pygame.transform.smoothscale(surface, (int((self.width+4)*scale),int((self.height+4)*scale)) )
		surf.blit(surface,(self.x,self.y))

	def update(self):
		if not self.visible:
			return False
		pygame.display.update((self.x,self.y,self.width+4,self.height+4))

	def inside(self,x,y,b):
		if not self.visible:
			return False
		global MOUSEHELD
		self.highlight=False
		if x>self.x and x< self.x+self.init_width+4 and y>self.y and y<self.y+self.height+4 and (MOUSEHELD==False or MOUSEHELD==self.id):
			self.highlight=True
			if type(b)!=int:
				if len(b)==1:
					self.txt+=b[0]
				elif b=='space':
					self.txt+=' '
				elif b=='backspace':
					try: 
						if(len(self.txt)>self.initial_len): self.txt=self.txt[:-1]
					except: pass
				
				self.reconfigure()
			return True
		else:
			return False
	def get(self):
		return self.txt[self.initial_len:]

class selection_menu:
	def __init__(self,x,y,items,color='white'):
		global total_items
		total_items+=1
		self.id=total_items
		self.type='menu'
		self.visible=True
		self.help=''
		self.x=x
		self.y=y
		self.open=False
		self.fixed_width=0
		self.highlighted=0
		self.index=0
		self.num=len(items)
		self.items=items
		self.transparency=100
		self.color=list(colors[color])
		self.bg=color
		self.selection=items[0]
		self.fontsize=18
		self.font = pygame.font.Font(None, self.fontsize)
		self.title=self.font.render('  '+items[0],1,self.color)
		self.width,self.text_height=font.size(items[0]+'   ')
		self.cell_height=self.text_height+3
		self.height=(self.cell_height)
		self.closed_lasttime=False
		
	def reconfigure(self):
		self.font = pygame.font.Font(None, self.fontsize)
		self.title=self.font.render('  '+self.items[0],1,self.color)
		self.width,self.text_height=self.font.size(self.items[0]+'   ')
		self.cell_height=self.text_height+3
		self.height=(self.cell_height)
		if self.fixed_width: self.width=self.fixed_width
	
	def clear_region(self,surf):
		if not self.visible:
			return False
		if self.closed_lasttime==True:
			surf.fill(colors['black'],(self.x,self.y,self.width+4,(self.cell_height)*(self.num+1) ))
		else:
			surf.fill(colors['black'],(self.x,self.y,self.width+4,self.height))
		self.closed_lasttime=False

	def renew(self,surf):
		if not self.visible:
			return False
		if(self.open==True): self.height=(self.cell_height)*(self.num+1)
		else: self.height=(self.cell_height)
		self.color[3]=self.transparency
			
		surface=pygame.Surface((self.width+4,self.height+4),pygame.SRCALPHA)
		self.color[3]=self.transparency
		bg=list(colors[self.bg])
		rect_line(surface,0,0,self.width+4,(self.cell_height)-3,bg,self.transparency) #blit box
		bg[3]=255
		pygame.draw.rect(surface,bg,(0,0,self.width+4,(self.cell_height)-3),1) #blit box

		if self.open==True:
			for a in range(self.num):
				l=True
				if self.highlighted==a:
					l=False
				rect_line(surface,0,(self.cell_height)*(a+1) ,self.width+4,self.cell_height-3,bg,self.transparency,l)
				txt=self.font.render(self.items[a],1,self.color)
				surface.blit(txt,( 10 , (self.cell_height)*(a+1)+1 ))
			
		surface.blit(self.title,(2,2))		
		surf.blit(surface,(self.x,self.y))

	def update(self):
		if not self.visible:
			return False
		if self.closed_lasttime==True:
			pygame.display.update((self.x,self.y,self.width,(self.cell_height)*(self.num+1) ))
			self.closed_lasttime=False
		else:
			pygame.display.update((self.x,self.y,self.width,self.height))

	def inside(self,x,y,b):
		global MOUSEHELD
		if not self.visible:
			return False
		if x>self.x and x< self.x+self.width+4 and y>self.y and y<self.y+self.height+4 and MOUSEHELD==False:
			if(b==0):
				self.highlighted=(y-self.y)/self.cell_height-1
				if self.highlighted>(self.num-1) : self.highlighted=self.num-1
				#elif self.highlighted<0 : self.highlighted=0
			elif(b==1):
				if self.highlighted==-1:
					self.title=self.font.render('  '+self.selection,1,self.color)
					self.open = not self.open
				else:
					self.selection=self.items[self.highlighted]
					self.index=self.highlighted
					self.title=self.font.render('  '+self.selection,1,self.color)
					self.open=False
				self.closed_lasttime=True
			return True
		else:
			return False

class rotating_menu:
	def __init__(self,x,y,items,width,color='white'):
		global total_items
		total_items+=1
		self.id=total_items
		self.type='rotating_menu'
		self.visible=True
		self.x=x
		self.y=y
		self.help=''
		self.num=len(items)
		self.items=[]
		self.midway=self.num/2-1
		n=1
		s=0
		for b in range(len(items)):
			l=button(10,0,items[b],width-20,color)
			l.bg=color
			l.locked=True
			if(n<=self.midway+1):
				s+=250/(self.midway+1)
			else :
				s-=250/(self.midway+1)
			if s<10: s=30
			l.transparency=s
			self.items.append(l)
			n+=1
		self.color=colors[color]
		self.selection=0
		self.width=width
		self.text_height=font.size('___')[1]
		self.cell_height=self.text_height+6
		self.height=self.cell_height*(self.num-1)
		self.first_pos=0
		self.yoffset=0
		self.co=0
		self.scrolling_to=self.items[self.num/2-1].id
		self.scrolling_direction=0
		self.fancy=False
	def clear_region(self,surf):
		if not self.visible:
			return False
		surf.fill(colors['black'],(self.x,self.y,self.width,self.height))

	def renew(self,surf):
		if not self.visible:
			return False
		surface=pygame.Surface((self.width,self.height),pygame.SRCALPHA)
		pygame.draw.circle(surface,self.color,(5,self.cell_height*self.first_pos+self.cell_height/2+int(self.yoffset) ),4,2)
		yy=int(self.yoffset)
		s=0
		n=1
		if self.fancy:
			scale=0.5
			scale_add=0.5/(self.midway+1)
		for a in self.items:
			a.y=yy
			yy+=self.cell_height
			a.border=False
			if self.fancy:
				if(n<=self.midway+1):
					scale+=scale_add
				else :
					scale-=scale_add
			if n==(self.midway+1):
				a.border=True
			if self.fancy:
				a.renew(surface,scale)
			else:
				a.renew(surface)
			n+=1
		surf.blit(surface,(self.x,self.y))

	def inside(self,x,y,b):
		global MOUSEHELD
		if not self.visible:
			return False
		self.yoffset-=self.scrolling_direction
		if self.items[self.midway].id==self.scrolling_to:
			self.scrolling_direction=0
		if(self.yoffset<-self.cell_height):
			tmp=self.items.pop(0)
			self.items.append(tmp)
			self.first_pos-=1
			if self.first_pos<0:self.first_pos=self.num-1
			self.yoffset=0
		elif(self.yoffset>0):
			tmp=self.items.pop()
			self.items.insert(0,tmp)
			self.first_pos+=1
			if self.first_pos>self.num-1:self.first_pos=0
			self.yoffset=-self.cell_height
								
		if x>self.x and x< self.x+self.width+4 and y>self.y and y<self.y+self.height+4 and MOUSEHELD==False:
			
			if b==4:
				self.yoffset-=5
			elif b==5:
				self.yoffset+=5
			elif b==1:
				pos=0
				for a in self.items:
					if a.inside(x-self.x,y-self.y,0):
						if pos==self.midway:
							print 'bingo'
						else:
							self.scrolling_to=a.id
							self.scrolling_direction=5*abs(pos-self.midway)/(pos-self.midway)
					pos+=1	
		
			return True
		else:
			return False


class knob:
	def __init__(self,x,y,text,val,minval=0,maxval=100,color='white'):
		global total_items
		total_items+=1
		self.id=total_items
		self.type='knob'
		self.x=x
		self.visible=True
		self.y=y
		self.step_size=1
		self.help=''
		self.color=colors[color]
		self.txt=text
		self.text=sfont.render(text,1,self.color)
		self.text_width,self.text_height=sfont.size(text)
		self.val=val		
		self.minval=minval		
		self.maxval=maxval
		self.width=50
		self.height=65

	def clear_region(self,surf):
		if not self.visible:
			return False
		surf.fill(colors['black'],(self.x,self.y,self.width,self.height))

	def renew(self,surf):
		if not self.visible:
			return False
		surface=pygame.Surface((self.width+4,self.height+4),pygame.SRCALPHA)
		val_text=sfont.render(str(self.val),1,self.color)
		val_text_width=sfont.size(str(self.val))[0]
		surface.blit(self.text,(self.width/2-self.text_width/2,self.height/2-10))
		surface.blit(val_text,(self.width/2-val_text_width/2,self.height/2))
		
		#pygame.draw.rect(surf,self.color,(self.x,self.y,self.width,self.height-15),1) #blit box
		pygame.draw.arc(surface, colors['gray'],(0,0,self.width,self.height-15) , -pi/4, pi*1.25, 3) #entire arc
		dtheta=1.5*pi/(self.maxval-self.minval)
		pygame.draw.arc(surface, self.color,(0,0,self.width,self.height-15) ,\
		pi*1.25-dtheta*(self.val-self.minval),pi*1.25-dtheta*(self.val-self.minval)+pi/10, 5)
		surf.blit(surface,(self.x,self.y))

	def update(self):
		if not self.visible:
			return False
		pygame.display.update((self.x,self.y,self.width,self.height))

	def inside(self,x,y,b):
		global MOUSEHELD
		if not self.visible:
			return False
		if x>self.x and x< self.x+self.width+4 and y>self.y and y<self.y+self.height+4 and MOUSEHELD==False:
			midway=self.x+(self.width+4)/2.0
			if b==4 or (x>midway and b==1): self.increase()
			elif b==5 or (x<midway and b==1): self.decrease()
			
			return True
		else:
			return False
	def increase(self):
		self.val+=self.step_size
		if( self.val > self.maxval ):self.val=self.maxval
	def decrease(self):
		self.val-=self.step_size
		if( self.val < self.minval ):self.val=self.minval

class slider:
	def __init__(self,x,y,text,val,minval=0,maxval=100,width=100,color='white'):
		global total_items
		total_items+=1
		self.id=total_items
		self.type='slider'
		self.visible=True
		self.x=x
		self.accuracy=1
		self.y=y
		self.step_size=1
		self.color=list(colors[color])
		self.transparency=170
		self.txt=text
		self.text=font.render(text,1,self.color)
		self.text_width,self.text_height=font.size(text)
		self.val=val		
		self.minval=minval	
		self.maxval=maxval
		self.help=''
		self.width=width
		self.slide_width=self.width/5.0
		self.height=self.text_height+4
		self.dx=float(self.width-self.slide_width)/(self.maxval-self.minval)
		self.grabbed=False
		self.cx=0
		self.bg=list(colors['darkgray'])
		self.bg[3]=200

	def clear_region(self,surf):
		if not self.visible:
			return False
		surf.fill(colors['black'],(self.x,self.y,self.width,self.height))

	def renew(self,surf):
		if not self.visible:
			return False
		self.color[3]=self.transparency
		showval=str(self.val-self.val%self.accuracy)
		surface=pygame.Surface((self.width,self.height),pygame.SRCALPHA)
		slide=pygame.Surface((self.slide_width,self.height),pygame.SRCALPHA)
		val_text=sfont.render(showval,1,colors['black'])
		val_text_width=sfont.size(showval)[0]
		rect_line(surface,0,0,self.width,self.height,self.bg)
		pygame.draw.rect(surface,colors['red'],(0,0,self.width,self.height),1) #blit box
		surface.blit(self.text,(self.width/2-self.text_width/2,6) )
		pygame.draw.rect(slide,self.color,(0,0,int(self.slide_width),self.height),0) #blit slider
		self.color[3]=250
		pygame.draw.rect(slide,self.color,(1,1,int(self.slide_width-2),self.height-2),1) #blit slider
		slide.blit(val_text,(10,3) )
		surface.blit(slide,(int((self.val-self.minval)*self.dx),0) )
		surf.blit(surface,(self.x,self.y))

	def update(self):
		pygame.display.update((self.x,self.y,self.width,self.height))
	
	def getval(self):
		return self.val-self.val%self.accuracy
		
	def inside(self,x,y,b):
		global MOUSEHELD
		if not self.visible:
			return False

		if (x>self.x and x< self.x+self.width and y>self.y and y<self.y+self.height) or (MOUSEHELD==self.id and pygame.mouse.get_pressed()[0]==1):
			if b==4 : self.increase()
			elif b==5 : self.decrease()
			elif b==1 and x>int((self.val-self.minval)*self.dx+self.x)\
			and x< int((self.val-self.minval)*self.dx+self.slide_width+self.x):
					self.cx=x-int((self.val-self.minval)*self.dx)-self.x
					self.grabbed=True
					MOUSEHELD=self.id
			elif pygame.mouse.get_pressed()[0]==1 and MOUSEHELD==self.id:
					self.val=( (x-(self.cx+self.x))/self.dx+self.minval)
					
					if self.val<self.minval:
						self.val=self.minval
					elif self.val>self.maxval:
						self.val=self.maxval
			else:
				MOUSEHELD=False
			return True
		elif MOUSEHELD==self.id:
			MOUSEHELD=False
			return False
			
	def increase(self):
		self.val+=self.step_size
		if( self.val > self.maxval ):self.val=self.maxval
	def decrease(self):
		self.val-=self.step_size
		if( self.val < self.minval ):self.val=self.minval

