"""
AIR HOCKEY
Server-client architecture
Control the players with Wii or Mouse controls.
Forked Repository: git://github.com/robogeek42/Air-Hockey.git
Added Functionalities:
* Improved Graphics
* Network gaming
* Two player mode
* Wii controller integration (Rumble mode)
* Adaptive ball physics
* Scalable window sizew

Authors:
Methenitis Georgios 10407537
Patrick de Kok ~
Amogh Gudi ~
"""


import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
from pymunk import Vec2d
import math, sys, random
import socket               # Import socket module

print 'Number of arguments:', len(sys.argv), 'arguments.'
print 'Argument List:', str(sys.argv)

RENDERING = False
if len(sys.argv) == 2:
    if str(sys.argv[1]) == "rendering=true":
        RENDERING = True
    if str(sys.argv[1]) == "rendering=false":
        RENDERING = False

s = socket.socket()         # Create a socket object
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host = "10.42.0.13" # Get local machine name
port = 5402            # Reserve a port for your service.
s.bind((host, port))        # Bind to the port
connections = []

WINW=1400
WINH=800
PI=3.14247

## Balls
balls = []
   
## players
players = []

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

def to_pygame(p):
    """Small hack to convert pymunk to pygame coordinates"""
    return int(p.x), int(-p.y+WINH)

def from_pygame(p):
    """Small hack to convert pymunk to pygame coordinates"""
    return int(p.x), int(-p.y+WINH)
    
def addball():
    radius=20
    mass=1
    inertia = pymunk.moment_for_circle(mass, 20, radius, (0,0))
    ball_body = pymunk.Body(mass, inertia)
    ball_body.position=(WINW/2,WINH/2)

    mainball = pymunk.Circle(ball_body, radius, (0,0))
    mainball.elasticity = 0.95
    space.add(ball_body, mainball)
    balls.append(mainball)

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

    for line in static_lines:
        body = line.body
        pv1 = body.position + line.a.rotated(body.angle)
        pv2 = body.position + line.b.rotated(body.angle)
        p1 = to_pygame(pv1)
        p2 = to_pygame(pv2)
        pygame.draw.lines(screen, THECOLORS["black"], False, [p1,p2])
    
def draw_score():
    DrawDigit(score['p1'], WINW/2 + 100, 100, 8, screen, THECOLORS["grey"], 2)
    DrawDigit(score['p2'], WINW/2 - 100, 100, 8, screen, THECOLORS["grey"], 2)

def draw_stuff(balls, space, score, screen):
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
            space.remove(ball)
            balls.remove(ball)
        pygame.draw.circle(screen, THECOLORS["black"], p, int(ball.radius), 0)
    pygame.display.flip()
    pygame.display.set_caption("Wii-AWESOME AIR HOCKEY")
    draw_score()

pygame.init()
clock = pygame.time.Clock()
if RENDERING:
    screen = pygame.display.set_mode((WINW, WINH))
running = True

### Physics stuff
space = pymunk.Space(50)
space.gravity = (0.0,0.0)

### walls
static_body = pymunk.Body()
static_lines = [pymunk.Segment(static_body, (wt, wt), (WINW-wt, wt), 1.0),
                pymunk.Segment(static_body, (wt, WINH-wt), (WINW-wt, WINH-wt), 1.0),
                pymunk.Segment(static_body, (wt, wt), (wt, (WINH-gw)/2), 1.0),
                pymunk.Segment(static_body, (wt, (WINH+gw)/2), (wt, WINH-wt), 1.0),
                pymunk.Segment(static_body, (WINW-wt, wt), ((WINW-wt), (WINH-gw)/2), 1.0),
                pymunk.Segment(static_body, (WINW-wt, (WINH+gw)/2), (WINW-wt, WINH-wt), 1.0),
                ]  
for line in static_lines:
    line.elasticity = 0.7
    line.group = 1
space.add(static_lines)

pmass=3
pradius=30
# Setup Player 1
p1inertia = pymunk.moment_for_circle(pmass, 0, pradius, (0,0))
p1_body = pymunk.Body(pmass, p1inertia)
p1_body.position=(WINW-WINW/8, WINH/2)
p1_shape = pymunk.Circle(p1_body, pradius, (0,0))
p1_shape.elasticity = 0.95

# Setup Player 2
p2inertia = pymunk.moment_for_circle(pmass, 0, pradius, (0,0))
p2_body = pymunk.Body(pmass, p2inertia)
p2_body.position=(WINW/8, WINH/2)
p2_shape = pymunk.Circle(p2_body, pradius, (0,0))
p2_shape.elasticity = 0.95

mouse_body1 = pymunk.Body()
mouse_body2 = pymunk.Body()
joint1=None
joint2=None
selected = None

# Add the ball
addball()
if RENDERING:
    draw_stuff(balls, space, score, screen)

s.listen(2)
while 1:
    conn, addr = s.accept()
    connections.append(conn)
    if len(connections) == 1:
        space.add(p1_body, p1_shape)
        players.append(p1_shape)
        p = to_pygame(p1_body.position)
        if RENDERING:
            pygame.draw.circle(screen, THECOLORS["darkgreen"], p, int(p1_shape.radius), 0)
            pygame.draw.circle(screen, THECOLORS["black"], p, int(p1_shape.radius+1), 2)
            pygame.draw.circle(screen, THECOLORS["black"], p, int(p1_shape.radius/2), 1)
    elif len(connections) == 2:
        space.add(p2_body, p2_shape)
        players.append(p2_shape)
        p = to_pygame(p2_body.position)
        if RENDERING:
            pygame.draw.circle(screen, THECOLORS["red"], p, int(p1_shape.radius), 0)
            pygame.draw.circle(screen, THECOLORS["black"], p, int(p1_shape.radius+1), 2)
            pygame.draw.circle(screen, THECOLORS["black"], p, int(p1_shape.radius/2), 1)
        break
    else:
        sys.exit()

while running:
    i = 0
    for q in connections:
        data = str(i)
        data += "," + str(score['p1']) + "," + str(score['p2'])
        for ball in balls:
            data +=  "," + str(int(ball.body.position[0])) + "," + str(int(ball.body.position[1]))
        data += "," + str(int(p1_body.position[0])) + "," + str(int(p1_body.position[1]))
        data += "," + str(int(p2_body.position[0])) + "," + str(int(p2_body.position[1]))
        q.send(data)
        i += 1

    data1 = connections[0].recv(1024)
    split_data1 = data1.split(",")
    mpos = (int(split_data1[2]), int(split_data1[3]))
    mouse_body1.position = from_pygame( Vec2d(mpos) )
    mouse_body1.angle = 0
    mouse_body1.angular_velocity = 0
    if joint1 is None:
        p1_body.position = mouse_body1.position
        joint1 = pymunk.PivotJoint(mouse_body1, p1_body, (0,0), (0,0) )
        space.add(joint1)
        p1_body.angular_velocity=0

    data2 = connections[1].recv(1024)
    split_data2 = data2.split(",")
    mpos = (int(split_data2[2]), int(split_data2[3]))
    mouse_body2.position = from_pygame( Vec2d(mpos) )
    mouse_body2.angle = 0
    mouse_body2.angular_velocity = 0
    if joint2 is None:
        p2_body.position = mouse_body2.position
        joint2 = pymunk.PivotJoint(mouse_body2, p2_body, (0,0), (0,0) )
        space.add(joint2)
    p2_body.angular_velocity=0

    # check if players are in the opponments' half
    if p1_body.position[0] < WINW / 2 :
        p1_body.position[0] = WINW / 2;

    if p2_body.position[0] > WINW / 2 :
        p2_body.position[0] = WINW / 2;
  
    ### Clear screen
    if RENDERING:
        screen.fill(THECOLORS["white"])
    
    ### Draw
    if RENDERING:
        draw_table()

    for ball in balls:
        p = to_pygame(ball.body.position)
        if p[0] < 0:
            score['p1'] += 1
        if p[0] >WINW:
            score['p2'] += 1

        if p[0] < 0 or p[0]>WINW:
            addball()
            space.remove(ball)
            balls.remove(ball)
        if RENDERING:
            pygame.draw.circle(screen, THECOLORS["black"], p, int(ball.radius), 0)

    if RENDERING:
        p = to_pygame(p1_body.position)
        pygame.draw.circle(screen, THECOLORS["darkgreen"], p, int(p1_shape.radius), 0)
        pygame.draw.circle(screen, THECOLORS["black"], p, int(p1_shape.radius+1), 2)
        pygame.draw.circle(screen, THECOLORS["black"], p, int(p1_shape.radius/2), 1)

        p = to_pygame(p2_body.position)
        pygame.draw.circle(screen, THECOLORS["red"], p, int(p1_shape.radius), 0)
        pygame.draw.circle(screen, THECOLORS["black"], p, int(p1_shape.radius+1), 2)
        pygame.draw.circle(screen, THECOLORS["black"], p, int(p1_shape.radius/2), 1)

        draw_score()

    ### Update physics
    dt = 1.0/60.0/5.
    for x in range(5):
        space.step(dt)
    
    clock.tick(50)

    ### Flip screen
    if RENDERING:
        pygame.display.flip()
        pygame.display.set_caption("Wii-AWESOME AIR HOCKEY")
s.close()
