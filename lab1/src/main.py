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


# globals
WIN_TITLE = 'Первая лаба'
width = 800
height = 600
ss = []


# TODO reshape still doesn't work
def reshape(w, h):
    global width, height

    width = w
    height = h
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, w, 0, h)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def display():
    global color, ss

    glClearColor(0.3, 0.3, 0.3, 1)
    glClear(GL_COLOR_BUFFER_BIT)
    # glPointSize(6)
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

    glRasterPos2i(0,0)
    glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord('X'))

    glFinish()


def keyboard(key, x, y):
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
