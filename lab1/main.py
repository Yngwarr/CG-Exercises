#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import sys
from peak.rules import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class Point(object):
    def __init__(self, x, y):
        if not (isinstance(x, int) and isinstance(y, int)):
            raise TypeError('x and y must be int')
        self.x = x
        self.y = y

    def __repr__(self):
        return '(' + str(self.x) + ',' + str(self.y) + ')'


class Color(object):
    @abstract()
    def __init__(self, r, g=None, b=None):
        pass

    @when(__init__, 'isinstance(r, int) and isinstance(g, int) \
            and isinstance(b, int)')
    def _init_3i(self, r, g, b):
        self.r = r % 0x100
        self.g = g % 0x100
        self.b = b % 0x100

    # format is '#rrggbb'
    @when(__init__, 'isinstance(r, basestring) and g == None and b == None')
    def _init_s(self, s, g=None, b=None):
        if s[0] != '#' or len(s) != 7:
            raise Exception('use \'#rrggbb\' for color')
        self.r = int(s[1:3], 16)
        self.g = int(s[3:5], 16)
        self.b = int(s[5:7], 16)

    def __repr__(self):
        return '#{:0>2x}{:0>2x}{:0>2x}'.format(self.r, self.g, self.b)

    def inverse(self):
        self.r ^= 0xFF
        self.g ^= 0xFF
        self.b ^= 0xFF


class Shape(object):
    def __init__(self):
        self.vtx = []
        self.color = Color('#000000')


def printText(text, pos, color):
    glColor3ub(color.r, color.g, color.b)
    offset = Point(0, 0)
    for c in text:
        if c != '\n':
            offset.x += 9
        else:
            offset.y -= 15
            offset.x = 0
            continue
        glRasterPos2i(pos.x + offset.x, pos.y + offset.y)
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))


def doCmd(text):
    global help_shown
    if text == 'help':
        help_shown = True if not help_shown else False

# globals
WIN_TITLE = 'Первая лаба'
width = 800
height = 600
ss = []

cmd = ['']
cmd_edition_mode = False
help_text = '''Use keys to manupulate objects:
    left mouse button - add point to current shape
    right mouse button - remove last point from current shape
    middle mouse button - finish with current shape
    w, a, s, d - move current shape
    r, g, b, R, G, B - change color of current shape
    <, > - shift chapes in the list'''
help_shown = False

# TODO reshape still doesn't work
def reshape(w, h):
    global width, height

    width = w
    height = h
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, w, 0, h, -1.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def display():
    global color, ss

    glClearColor(0.3, 0.3, 0.3, 1)
    glClear(GL_COLOR_BUFFER_BIT)
    glPointSize(6)
    glLineWidth(3)

    for s in ss:
        glColor3ub(s.color.r, s.color.g, s.color.b)
        glBegin(GL_POLYGON)
        for i in range(0, len(s.vtx)):
            glVertex2i(s.vtx[i].x, s.vtx[i].y)
        glEnd()

    if len(ss) != 0:
        glColor3ub(ss[-1].color.r ^ 0xFF, \
                ss[-1].color.g ^ 0xFF, \
                ss[-1].color.b ^ 0xFF)
        glBegin(GL_LINE_LOOP)
        for i in range(0, len(ss[-1].vtx)):
            glVertex2i(ss[-1].vtx[i].x, ss[-1].vtx[i].y)
        glEnd()

        if len(ss[-1].vtx) != 0:
            glBegin(GL_POINTS)
            glVertex2i(ss[-1].vtx[-1].x, ss[-1].vtx[-1].y)
            glEnd()

    text_color = Color('#ffffff')
    if not help_shown:
        printText('Type \':help\' for help.', Point(5, 20), text_color)
    else:
        printText(help_text, Point(5, 125), text_color)
    printText(cmd[-1], Point(5, 5), text_color)

    glFinish()


def keyboard(key, x, y):
    global ss, cmd, cmd_edition_mode
    if cmd_edition_mode:
        if key == '\x0d':
            cmd_edition_mode = False
            cmd += ['']
            doCmd(cmd[-2][1:])
        elif key == '\x08':
            cmd[-1] = cmd[-1][:-1]
        else:
            cmd[-1] += key
            print(str(ord(key)))
    else:
        if key == ':':
            cmd_edition_mode = True
            cmd += ':'
        # Изменение RGB-компонент цвета точек
        if key == 'r': ss[-1].color.r += 5
        if key == 'g': ss[-1].color.g += 5
        if key == 'b': ss[-1].color.b += 5
        if key == 'R': ss[-1].color.r -= 5
        if key == 'G': ss[-1].color.g -= 5
        if key == 'B': ss[-1].color.b -= 5
        # Изменение XY-кординат точек
        if key == 'w':
            for i in range(0, len(ss[-1].vtx)):
                ss[-1].vtx[i].y += 9
        if key == 's':
            for i in range(0, len(ss[-1].vtx)):
                ss[-1].vtx[i].y -= 9
        if key == 'a':
            for i in range(0, len(ss[-1].vtx)):
                ss[-1].vtx[i].x -= 9
        if key == 'd':
            for i in range(0, len(ss[-1].vtx)):
                ss[-1].vtx[i].x += 9
        if key == '>':
            ss = [ss[-1]] + ss[:-1]
        if key == '<':
            ss = ss[1:] + [ss[0]]

    glutPostRedisplay()

def mouse(button, state, x, y):
    global ss
    # клавиша была нажата, но не отпущена
    if state != GLUT_DOWN: return
    # новая точка по левому клику 
    if button == GLUT_LEFT_BUTTON:
        p = Point(x, height - y)
        if len(ss) == 0: 
            ss.append(Shape())
        ss[-1].vtx.append(p)
    # удаление последней точки по правому клику 
    if button == GLUT_RIGHT_BUTTON:
        if len(ss) == 0: return
        if len(ss[-1].vtx) == 0:
            ss = ss[:-1]
            glutPostRedisplay()
            return
        ss[-1].vtx = ss[-1].vtx[:-1]
    if button == GLUT_MIDDLE_BUTTON:
        ss.append(Shape())
    glutPostRedisplay()


if __name__ == '__main__':
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB)
    glutInitWindowSize(width, height)
    glutCreateWindow(WIN_TITLE)
    glEnable(GL_POINT_SMOOTH)

    glutReshapeFunc(reshape)
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutMouseFunc(mouse)

    glutMainLoop()
