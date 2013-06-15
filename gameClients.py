import pygame
from pygame.locals import *
from pygame.color import *
import socket               # Import socket module

s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 5402          # Reserve a port for your service.


## Balls
balls = []

WINW=600
WINH=300
# Wall thickness
wt=20.0
# Goal width
gw=WINW/4.0
score = {'p1':0, 'p2':0}

grid=[[0,0],[2,0], # 0 1
      [0,1],[2,1], # 2 3
      [0,2],[2,2], # 4 5
      [0,3],[2,3], # 6 7
      [0,4],[2,4]] # 8 9


MOVE=0
DRAW=1
numidx=[]
for i in range(0,10):
    numidx.append([])
numidx[0]=[[MOVE,0], [DRAW,1], [DRAW,9], [DRAW,8], [DRAW,0]]
numidx[1]=[[MOVE,1], [DRAW,9]]
numidx[2]=[[MOVE,2], [DRAW,0], [DRAW,1], [DRAW,3], [DRAW,8], [DRAW,9]]
numidx[3]=[[MOVE,0], [DRAW,1], [DRAW,9], [DRAW,8], [MOVE,4], [DRAW,5]]
numidx[4]=[[MOVE,0], [DRAW,4], [DRAW,5], [MOVE,1], [DRAW,9]]
numidx[5]=[[MOVE,1], [DRAW,0], [DRAW,4], [DRAW,5], [DRAW,9], [DRAW,8], [DRAW,6]]
numidx[6]=[[MOVE,3], [DRAW,1], [DRAW,0], [DRAW,8], [DRAW,9], [DRAW,5], [DRAW,4]]
numidx[7]=[[MOVE,0], [DRAW,1], [DRAW,3], [DRAW,8]]
numidx[8]=[[MOVE,0], [DRAW,1], [DRAW,9], [DRAW,8], [DRAW,0], [MOVE,4], [DRAW,5]]
numidx[9]=[[MOVE,5], [DRAW,4], [DRAW,0], [DRAW,1], [DRAW,9], [DRAW,8]]

def DrawDigit(N, X,Y, MAG, screen, col, lw):
    cx=0 ; cy=0
    if N < 0 or N > 9:
        print "Digit ",N," out of range"
        return
    for m in numidx[N]:
        if m[0]==MOVE:
            cx=grid[m[1]][0]*MAG+X
            cy=grid[m[1]][1]*MAG+Y
        else:
            pygame.draw.line(screen, col,
                    (cx,cy),
                    (grid[m[1]][0]*MAG+X, grid[m[1]][1]*MAG+Y),
                    lw)
            cx = grid[m[1]][0]*MAG+X
            cy = grid[m[1]][1]*MAG+Y

def draw_table():
    pygame.draw.rect(screen, THECOLORS["blue"], [[0.0, 0.0], [WINW, wt]], 0)
    pygame.draw.rect(screen, THECOLORS["blue"], [[0.0, WINH-wt], [WINW, WINH]], 0)
    pygame.draw.rect(screen, THECOLORS["blue"], [[0.0, 0.0], [wt, (WINH-gw)/2]], 0)
    pygame.draw.rect(screen, THECOLORS["blue"], [[0.0, (WINH+gw)/2], [wt,WINH]], 0)
    pygame.draw.rect(screen, THECOLORS["blue"], [[WINW-wt, 0.0], [WINW, (WINH-gw)/2]], 0)
    pygame.draw.rect(screen, THECOLORS["blue"], [[WINW-wt, (WINH+gw)/2], [WINW,WINH]], 0)

    pygame.draw.line(screen, THECOLORS["grey"], (WINW/2, wt), (WINW/2, WINH-wt), 2)
    circrad=int(1.2*gw/3)
    pygame.draw.circle(screen, THECOLORS["grey"], (WINW/2, WINH/2), circrad, 2)
    pygame.draw.arc(screen, THECOLORS["grey"], [[-circrad, WINH/2-circrad], [+circrad,WINH/2+circrad]], 270, 90, 2)

def draw_score():
    DrawDigit(score['p1'], WINW/2 + 100, 100, 8, screen, THECOLORS["grey"], 2)
    DrawDigit(score['p2'], WINW/2 - 100, 100, 8, screen, THECOLORS["grey"], 2)

def draw_stuff(balls, score, screen):
    ### Clear screen
    screen.fill(THECOLORS["white"])
    ### Draw 
    draw_table()
    for ball in balls:
        p = to_pygame(ball.body.position)
        if p[0] < 0:
            score['p1'] += 1
        if p[0] >WINW:
            score['p2'] += 1

        if p[0] < 0 or p[0]>WINW:
            addball()
            balls.remove(ball)

        pygame.draw.circle(screen, THECOLORS["black"], p, int(ball.radius), 0)

    pygame.display.flip()
    pygame.display.set_caption("Wii-AWESOME AIR HOCKEY")
    draw_score()

pygame.init()

screen = pygame.display.set_mode((WINW, WINH))
clock = pygame.time.Clock()  

draw_stuff(balls, score, screen)


####################################################################

s.connect((host, port))
while 1:
	data = s.recv(1024)
	if not data:
		print "server down"
		break
	else:
		screen.fill(THECOLORS["white"])
		# split_data = data.split(",")
		# print split_data
		# score['p1'] = int(float(split_data[1]))
		# score['p2'] = int(float(split_data[2]))


		draw_stuff(balls, score, screen)
		# pygame.display.set_caption("Wii-AWESOME AIR HOCKEY ~ Player:"+ split_data[0])
s.close                     # Close the socket when done