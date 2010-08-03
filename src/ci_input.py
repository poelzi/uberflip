######################################################################
# Modulo input modifica alarm set 0.011 No Party
# Ciro Ippolito
#   Version 9:44 PM 12/31/2008 
######################################################################
import pygame, time
import ci_alarm
import ci_gfx
import ci_mood
from pygame.locals import *
#from _init import *
import ci_init as ci
#***************** Pygame *************************************
pygame.init()
h1=pygame.Rect ( 28,88,107,207)   #magari riuscire a muovere l'area fuori dalla funzione
h2=pygame.Rect ( 130,88,107,207)
m1=pygame.Rect ( 260,88,107,207)
m2=pygame.Rect ( 365,88,107,207)
alarmswi=pygame.Rect ( 504,75,286,85)          #Select Rect ALARM SWITCH
mood0=pygame.Rect ( 504,180,140,85)
mood1=pygame.Rect ( 650,180,140,85)    #****************************************
exitrect=pygame.Rect ( 0,400,800,100)
font=pygame.font.SysFont("SwissA",120)
#***************** Inizializzazione Grafica *************************************
    
dovecliccai=0
mousepos=[0,0,0,0,0,0,0,0]
pos=0
dragc=[0,0]
screen=0
coordinate_numeri = {"ore_decine": (28, 88),
                     "ore_unita": (130, 88),
                     "minuti_decine": (260, 88),
                     "minuti_unita": (365, 88)}

###################### Code no longer used, should be removed? ##########################
def tastiera():
  global screen,coordinate_numeri,exitrect,fondo,r,g,b
#  drawkeyboard()
  ci_gfx.drawalarm()
  while True:
    event = pygame.event.wait()
    if event.type == QUIT: 
	  print "input is exiting!"
	  #sys.exit(0)                               #La musica e' finita... gli amici se ne vanno...
    elif event.type == MOUSEBUTTONDOWN:
      print "mousebutton down:"
      dovecliccai=click()                       #let see where the stupid user clicked
    elif event.type == MOUSEBUTTONUP:
      print "mousebutton up:"      
      x=anddrag(mousepos)
      if x==1:
        return #return (moodc)#(sveglia)
'''      screen.blit(fondo,(0,0))
      screen.blit(numeri[int(_init.sveglia[0])], coordinate_numeri["ore_decine"])     #ORE    (11ma lettera)
      screen.blit(numeri[int(_init.sveglia[1])], coordinate_numeri["ore_unita"])
      screen.blit(numeri[int(_init.sveglia[2])], coordinate_numeri["minuti_decine"])  #MINUTI (14ma lettera)
      screen.blit(numeri[int(_init.sveglia[3])], coordinate_numeri["minuti_unita"])
      stringasveglia=str(_init.sveglia[0])+str(_init.sveglia[1])+":"+str(_init.sveglia[2])+str(_init.sveglia[3])
      if _init.svegliaswitch==0:
       #Switch OFF
        screen.blit(allarmswitch[0],(504,75))
        msg=font.render(stringasveglia,True,(40,40,40))
        screen.blit(base,(12,386))
        screen.blit(msg,(292,390))
      else:
        #Switch ON
        screen.blit(allarmswitch[1],(504,75))
        msg=font.render(stringasveglia,True,(250,125,125))
        screen.blit(base, (12,386))
        screen.blit(msg,(292,390))
      pygame.display.flip()
      mood()
  return ()
'''
###################### Done code no longer used, should be removed? ##########################


def drawkeyboard():
  global numeri,screen,coordinate_numeri
#  screen = pygame.display.get_surface()     
#  screen.blit(fondo,(0,0))
'''  ci_gfx.bg_alarm()
  screen.blit(numeri[int(_init.sveglia[0])], coordinate_numeri["ore_decine"])     #ORE    (11ma lettera)
  screen.blit(numeri[int(_init.sveglia[1])], coordinate_numeri["ore_unita"])
  screen.blit(numeri[int(_init.sveglia[2])], coordinate_numeri["minuti_decine"])  #MINUTI (14ma lettera)
  screen.blit(numeri[int(_init.sveglia[3])], coordinate_numeri["minuti_unita"])
  stringasveglia=str(_init.sveglia[0])+str(_init.sveglia[1])+":"+str(_init.sveglia[2])+str(_init.sveglia[3])  
  mood()
  ci_gfx.drawalarm():
  if _init.svegliaswitch==0:
    screen.blit(allarmswitch[0],(504,75))              #Switch OFF
    msg=font.render(stringasveglia,True,(40,40,40))
    screen.blit(msg,(292,390))
  else:
    screen.blit(allarmswitch[1],(504,75))              #Switch ON
    msg=font.render(stringasveglia,True,(250,0,0))
    screen.blit(msg,(292,390))
  pygame.display.flip()
'''

def click():
  global mousepos,dragc,pos
  global h1,h2,m1,m2,alarmswi,mood0,mood1,moodc
  pos=pygame.mouse.get_pos()
  mousepos=((h1.collidepoint(pos[0],pos[1])),
            (h2.collidepoint(pos[0],pos[1])),
            (m1.collidepoint(pos[0],pos[1])),
            (m2.collidepoint(pos[0],pos[1])),
            (alarmswi.collidepoint(pos[0],pos[1])),
            (exitrect.collidepoint(pos[0],pos[1])),
            (mood0.collidepoint(pos[0],pos[1])),
            (mood1.collidepoint(pos[0],pos[1])))
  if mousepos[0]:
    dovecliccai=1
  elif mousepos[1]:
    dovecliccai=2
  elif mousepos[2]:
    dovecliccai=3
  elif mousepos[3]:
    dovecliccai=4
  elif mousepos[4]:     dovecliccai=5     # Alarm switch
  elif mousepos[5]:     dovecliccai=6     # Mood Off
  elif mousepos[6]:     dovecliccai=7     # Mood On    

'''def anddrag(dovecliccai):
  global dragc,mousepos,pos,exitrect         # mousepos e' la posizione del mouse al click (da comparare con la posizione al anddrag
  global h1,h2,m1,m2,alarmswi
  pos1=pygame.mouse.get_pos()  
  mousepos1=((h1.collidepoint(pos1[0],pos1[1])),
             (h2.collidepoint(pos1[0],pos1[1])),
             (m1.collidepoint(pos1[0],pos1[1])),
             (m2.collidepoint(pos1[0],pos1[1])),
             (alarmswi.collidepoint(pos1[0],pos1[1])),
             (exitrect.collidepoint(pos1[0],pos1[1])),
             (mood0.collidepoint(pos1[0],pos1[1])),
             (mood1.collidepoint(pos1[0],pos1[1])))
  if mousepos[0]==mousepos1[0]==1:      #####################H1
    if pos[1]>pos1[1]:                  #direzione su decremento
      _init.sveglia[0]=_init.sveglia[0]-1
      if _init.sveglia[0]==-1:   _init.sveglia[0]=0
    elif pos[1]<pos1[1]:                #direzione giu incremento
      _init.sveglia[0]=_init.sveglia[0]+1
      if _init.sveglia[0]==2 and _init.sveglia[1] > 4:
        _init.sveglia[0]=1
      elif _init.sveglia[0]==3  and _init.sveglia[1] < 5:
        _init.sveglia[0]=2



        
  elif mousepos[1]==mousepos1[1]==1:    #####################H2
    if pos[1]>pos1[1]:                  #direzione su decremento
      _init.sveglia[1]=_init.sveglia[1]-1
      if _init.sveglia[1]==-1: _init.sveglia[1]=0
    elif pos[1]<pos1[1]:                #direzione giu incremento
      _init.sveglia[1]=_init.sveglia[1]+1
      if _init.sveglia[1]==4 and _init.sveglia[0]>1:
        _init.sveglia[1]=3      
      elif _init.sveglia[1]>9: _init.sveglia[1]=9
  elif mousepos[2]==mousepos1[2]==1:   #####################M1
    if pos[1]>pos1[1]:
      _init.sveglia[2]=_init.sveglia[2]-1
      if _init.sveglia[2]==-1: _init.sveglia[2]=0
    elif pos[1]<pos1[1]:
      _init.sveglia[2]=_init.sveglia[2]+1
      if _init.sveglia[2]>5: _init.sveglia[2]=5
  elif mousepos[3]==mousepos1[3]==1:    #####################M2
    if pos[1]>pos1[1]:
      _init.sveglia[3]=_init.sveglia[3]-1
      if _init.sveglia[3]<0: _init.sveglia[3]=0
    elif pos[1]<pos1[1]:
      _init.sveglia[3]=_init.sveglia[3]+1
      if _init.sveglia[3]>9: _init.sveglia[3]=9
  elif mousepos[4]==mousepos1[4]==1:    #####################Alarm Switch
    if pos[0]>pos1[0]:                  #Direzione left
      _init.svegliaswitch=0
      screen.blit(allarmswitch[0],(504,75))
      pygame.display.flip()
    elif pos[0]<pos1[0]:                #Direzione right
      _init.svegliaswitch=1
      screen.blit(allarmswitch[1],(504,75))
      pygame.display.flip()
  elif mousepos[5]==mousepos1[5]==1:    ##################### close alarm
    return 1
  elif mousepos[6]==mousepos1[6]==1:    ##################### Mood0
    _init.moodc=0
  elif mousepos[7]==mousepos1[7]==1:    ##################### Mood1/2/3/4/5
    if _init.moodc<4:
      _init.moodc=_init.moodc+1
    else:
      _init.moodc=1
#  return (sveglia)
'''
def mood():
  global g_mood
  print "il mood adesso e':",_init.moodc
  screen.blit(g_mood[_init.moodc],(0,17))
  screen.blit(g_mood[_init.moodc],(0,70))
  if _init.sw_led==1:
    if _init.moodc==0:                 
      #ledrgb[]=0,0,0
      r=0                              
      g=0
      b=0
      ci_alarm.led (r,g,b)
      print r,g,b
    elif _init.moodc ==1:
      r=250
      g=125
      b=0
      ci_alarm.led (r,g,b)
      print r,g,b
    elif _init.moodc ==2:
      r=0
      g=0
      b=250
      ci_alarm.led (r,g,b)
      print r,g,b
    elif _init.moodc ==3:    
      r=250
      g=0
      b=0
      ci_alarm.led (r,g,b)
      print r,g,b
    elif _init.moodc ==4:
      r=250
      g=0
      b=125
      ci_alarm.led (r,g,b)
      print r,g,b
  pygame.display.flip()
  
def taprelease():
  global mousepos,dovecliccai,sveglia
  pos=pygame.mouse.get_pos()
  pp=exitrect.collidepoint(pos[0],pos[1])
  if pp:
    print "Fuori di qui"
    return (0)
  sveglia=anddrag(mousepos)
  screen.blit(numeri[int(sveglia[0])], coordinate_numeri["ore_decine"])     #ORE    (11ma lettera)
  screen.blit(numeri[int(sveglia[1])], coordinate_numeri["ore_unita"])
  screen.blit(numeri[int(sveglia[2])], coordinate_numeri["minuti_decine"])  #MINUTI (14ma lettera)
  screen.blit(numeri[int(sveglia[3])], coordinate_numeri["minuti_unita"])
  pygame.display.flip()
