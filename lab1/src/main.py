#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

WIN_TITLE = 'Первая лаба'
width = 800
height = 600
color = {
    'r': 0,
    'g': 0,
    'b': 0
}
vs = [[]]

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
    global color, vs

    glClearColor(0.3, 0.3, 0.3, 1)
    glClear(GL_COLOR_BUFFER_BIT)
    # glPointSize(6)
    glLineWidth(3)

    glColor3ub(color['r'], color['g'], color['b'])
    for ps in vs:
        glBegin(GL_POLYGON)
        for i in range(0, len(ps)):
            glVertex2i(ps[i][0], ps[i][1])
        glEnd()

    if len(vs) != 0:
        glColor3ub(color['r'] ^ 0xFF, color['g'] ^ 0xFF, color['b'] ^ 0xFF)
        glBegin(GL_LINE_LOOP)
        for i in range(0, len(vs[-1])):
            glVertex2i(vs[-1][i][0], vs[-1][i][1])
        glEnd()

    glRasterPos2i(0,0)
    glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord('X'))

    glFinish()


def keyboard(key, x, y):
    # Изменение RGB-компонент цвета точек
    if key == 'r': color['r'] += 5
    if key == 'g': color['g'] += 5
    if key == 'b': color['b'] += 5
    if key == 'R': color['r'] -= 5
    if key == 'G': color['g'] -= 5
    if key == 'B': color['b'] -= 5
    # Изменение XY-кординат точек
    if key == 'w':
        for i in range(0, len(vs[-1])): vs[-1][i][1] += 9;
    if key == 's':
        for i in range(0, len(vs[-1])): vs[-1][i][1] -= 9;
    if key == 'a':
        for i in range(0, len(vs[-1])): vs[-1][i][0] -= 9;
    if key == 'd':
        for i in range(0, len(vs[-1])): vs[-1][i][0] += 9;
    glutPostRedisplay()

def mouse(button, state, x, y):
    global vs
    # клавиша была нажата, но не отпущена
    if state != GLUT_DOWN: return
    # новая точка по левому клику 
    if button == GLUT_LEFT_BUTTON:
        p = (x, height - y)
        if len(vs) == 0: 
            vs.append([])
        vs[-1].append(p)
    # удаление последней точки по правому клику 
    if button == GLUT_RIGHT_BUTTON:
        if len(vs) == 0: return
        if len(vs[-1]) == 0:
            vs = vs[:-1]
            glutPostRedisplay()
            return
        vs[-1] = vs[-1][:-1]
    if button == GLUT_MIDDLE_BUTTON:
        # TODO don't add empty shapes 
        vs.append([])
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
