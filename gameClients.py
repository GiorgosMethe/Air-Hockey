import pygame
from pygame.locals import (K_ESCAPE, KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP,
        QUIT)
from pygame.color import THECOLORS
import pymunk
import socket               # Import socket module
import sys

import pgwiimote

USAGE_MESSAGE = """Call program as
    python %s HOST_IP [wiimote|mouse]
""" % sys.argv[0]

s = socket.socket()         # Create a socket object
host = "10.42.0.13" # Get local machine name
port = 5402          # Reserve a port for your service.

MOUSE = True
Wii = False
## Balls
balls = []

WINW=700
WINH=400
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


def from_pygame(p):
    """Small hack to convert pymunk to pygame coordinates"""
    return int(p.x), int(-p.y+WINH)


def to_pygame(p):
    """Small hack to convert pymunk to pygame coordinates"""
    return int(p[0]), int(-p[1]+WINH)


def draw_score():
    DrawDigit(score['p1'], WINW/2 + 100, 100, 8, screen, THECOLORS["grey"], 2)
    DrawDigit(score['p2'], WINW/2 - 100, 100, 8, screen, THECOLORS["grey"], 2)


def draw_stuff(balls, score, screen):
    # screen.fill(THECOLORS["white"])
    ### Draw 
    draw_table()
    for ball in balls:
        p = ball
        pygame.draw.circle(screen, THECOLORS["black"], to_pygame(p), int(20), 0)
    draw_score()

if __name__ == "__main__":
    for arg in sys.argv:
        arg = arg.lower()
        if arg.startswith("host="):
            host = arg.split("host=")[1]
        if arg.startswith("port="):
            port = arg.split("port=")[1]
        if arg.startswith("wii"):
            Wii = True
            MOUSE = False

    if Wii:
        raw_input("Press 1+2 on the Wiimote to connect; then press Enter")
        wiimote = pgwiimote.Wiimote()
        print "Connected! Program exits when the - button is pressed."

    pygame.init()

    screen = pygame.display.set_mode((WINW, WINH))
    clock = pygame.time.Clock()  

    draw_stuff(balls, score, screen)

    s.connect((host, port))
    while 1:
        data = s.recv(1024)
        if not data:
            print "server down"
            break
        else:
            screen.fill(THECOLORS["white"])
            split_data = data.split(",")
            
            #take the score
            score['p1'] = int(split_data[1])
            score['p2'] = int(split_data[2])
            
            #get player number
            if Wii:
                if split_data[0] == "0":
                    wiimote.set_leds(3)
                elif split_data[0] == "1":
                    wiimote.set_leds(12)

            if len(balls) == 1:
                balls.pop()
            #take the ball position
            balls.append((int(split_data[3]), int(split_data[4])))

            # fraw stuff
            draw_stuff(balls, score, screen)

            p = to_pygame((int(split_data[5]), int(split_data[6])))
            pygame.draw.circle(screen, THECOLORS["darkgreen"], p, 30, 0)
            pygame.draw.circle(screen, THECOLORS["black"], p, 31, 2)
            pygame.draw.circle(screen, THECOLORS["black"], p, 15, 1)
            p = to_pygame((int(split_data[7]), int(split_data[8])))
            pygame.draw.circle(screen, THECOLORS["red"], p, 30, 0)
            pygame.draw.circle(screen, THECOLORS["black"], p, 31, 2)
            pygame.draw.circle(screen, THECOLORS["black"], p, 15, 1)

            if MOUSE:
                # mouse stuff
                mouse_body = pymunk.Body()
                mpos = pygame.mouse.get_pos()
                mouse_body.angle = 0
                mouse_body.angular_velocity = 0
                button = "0";
                if pygame.event.peek(MOUSEBUTTONUP):
                    button = "1"
                elif pygame.event.peek(MOUSEBUTTONDOWN):
                    button = "2"
            elif Wii:
                wiimote.set_leds(int(split_data[0]))
                wiimote_body = pymunk.Body()
                mpos = wiimote.get_pos()
                mpos = int(mpos[0] * WINW), int(mpos[1] * WINH)
                wiimote_body.angle = 0
                wiimote_body.angular_velocity = 0
                button = "0";
                buttons = wiimote.get_pressed()
                pressed_buttons = filter(lambda x: buttons[x], buttons)
                if "B" in pressed_buttons:
                    button = "2"
                else:
                    button = "1"
                if "-" in pressed_buttons:
                    pygame.event.post(pygame.event.Event(QUIT, None))

            for event in pygame.event.get():
                if event.type == QUIT:
                    s.close()
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    s.close()
                    pygame.quit()
                    sys.exit()
            msg = "1" + "," + button + "," + str(mpos[0]) + "," + str(mpos[1])
            s.send(msg)
            # end mouse stuff

            # draw playes
            # players positions
            pygame.display.flip()
    s.close()
