#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import sys
import shlex
from copy import deepcopy
from peak.rules import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class Point(object):
    """ Point on the screen. """
    def __init__(self, x, y):
        if not (isinstance(x, int) and isinstance(y, int)):
            raise TypeError('x and y must be int')
        self.x = x
        self.y = y

    def __repr__(self):
        return '(' + str(self.x) + ',' + str(self.y) + ')'

    def get2i(self):
        return (self.x, self.y)

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
        return Color(self.r ^ 0xFF, self.g ^ 0xFF, self.b ^ 0xFF)

    def get3i(self):
        return (self.r, self.g, self.b)

    def get4f(self):
        return (self.r/255., self.g/255., self.b/255., 1.)

class Shape(object):
    def __init__(self):
        self.vtx = []
        self.color = deepcopy(cfg['shape_color'])

class Settings(object):
    def __init__(self):
        self._vs = {
            'title': ['Lab 1', 'title of the window'],
            'bg': [Color('#333333'), 'background color'],
            'text_color': [Color('#ffffff'), 'color of text'],
            'shape_color': [Color('#000000'), 'default color for shape'],
            'motd': ['Type \':help\' for help.', 'the first message you see'],
            'point_size': [6, 'size of the point denoting the current vertex'],
            'line_width': [3, 'width of the outline of current shape'],
            'color_delta': [5, 'value to add to color with r,g,b'],
            'pos_delta': [9, 'value to add to pos with w,a,s,d']
        }

    def __getitem__(self, key):
       return self._vs[key][0] 

    def __repr__(self):
        return ', '.join(self._vs.keys())

    @abstract()
    def __setitem__(self, key, value):
        pass

    @when(__setitem__, 'isinstance(self._vs[key][0], Color)')
    def _set_color(self, key, value):
        self._vs[key][0] = Color(value)

    @when(__setitem__, 'isinstance(self._vs[key][0], int)')
    def _set_int(self, key, value):
        self._vs[key][0] = int(value)

    @when(__setitem__, 'isinstance(self._vs[key][0], basestring)')
    def _set_color(self, key, value):
        self._vs[key][0] = value

    def showInfo(self, key):
        return key + ' - ' + self._vs[key][1]


def printText(text, pos, color):
    glColor3ub(*color.get3i())
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
    global cfg
    global txts
    global text_buf
    
    # print('Doin\' ' + text)
    # args-like split 
    c = shlex.split(text)
    if c[0] == 'help':
        text_buf = txts['help']
    elif c[0] == 'clear':
        text_buf = ''
    elif c[0] == 'get':
        if len(c) < 2:
            text_buf = txts['get_usage']
            return
        try:
            text_buf = c[1] + ' = ' + str(cfg[c[1]])
        except KeyError:
            text_buf = txts['no_setting'].format(c[1])
    elif c[0] == 'set':
        if len(c) < 2:
            text_buf = txts['set_usage']
        else:
            if c[1] == 'info':
                if len(c) == 2:
                    text_buf = txts['set_info'].format(str(cfg))
                    return
                try:
                    text_buf = cfg.showInfo(c[2])
                except KeyError:
                    text_buf = txts['no_setting'].format(c[2])
            else:
                if len(c) != 3:
                    text_buf = txts['set_usage']
                    return
                try:
                    cfg[c[1]] = c[2]
                except KeyError:
                    text_buf = txts['no_setting'].format(c[1])


# globals
cfg = None
cfg_file = None
width = None
height = None
ss = None
text_buf = None

cmd = ['']
cmd_edition_mode = False
txts = {
    'help': '''Use keys to manupulate objects:
    left mouse button - add a point to current shape
    right mouse button - remove the last point from current shape
    middle mouse button - finish current shape
    w, a, s, d - move current point
    W, A, S, D - move current shape
    r, g, b, R, G, B - change color of current shape
    ',', '.' - shift points in the shape
    <, > - shift shapes in the list''',
    'get_usage': '''Usage: get setting_name
See all settings with \'set info\' ''',
    'set_usage': '''Usage: set setting_name value
See all settings with \'set info\' ''',
    'set_info': '{}\nYou can see info about each setting using\
 \'set info setting_name\'',
    'no_setting': 'No setting with name \'{}\''
}

def reshape(w, h):
    global width
    global height

    width = w
    height = h
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, w, 0, h, -1.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def display():
    global cfg
    global text_buf

    glClearColor(*cfg['bg'].get4f())
    glClear(GL_COLOR_BUFFER_BIT)
    glPointSize(cfg['point_size'])
    glLineWidth(cfg['line_width'])

    for s in ss:
        glColor3ub(*s.color.get3i())
        glBegin(GL_POLYGON)
        for i in range(0, len(s.vtx)):
            glVertex2i(*s.vtx[i].get2i())
        glEnd()

    if len(ss) != 0:
        glColor3ub(*ss[-1].color.inverse().get3i())
        glBegin(GL_LINE_LOOP)
        for i in range(0, len(ss[-1].vtx)):
            glVertex2i(*ss[-1].vtx[i].get2i())
        glEnd()

        if len(ss[-1].vtx) != 0:
            glBegin(GL_POINTS)
            glVertex2i(*ss[-1].vtx[-1].get2i())
            glEnd()

    printText(text_buf, Point(5, 20 + 15*text_buf.count('\n')), \
            cfg['text_color'])
    printText(cmd[-1], Point(5, 5), cfg['text_color'])

    glFinish()


def keyboard(key, x, y):
    global cfg
    global ss
    global cmd
    global cmd_edition_mode

    if cmd_edition_mode:
        if key == '\x0d':
            cmd_edition_mode = False
            cmd += ['']
            doCmd(cmd[-2][1:])
        elif key == '\x08':
            if cmd[-1] == ':':
                cmd_edition_mode = False
            cmd[-1] = cmd[-1][:-1]
        elif key == '\x1b':
            cmd_edition_mode = False
            cmd[-1] = ''
        else:
            cmd[-1] += key
            # print(str(ord(key)))
    else:
        if key == ':':
            cmd_edition_mode = True
            cmd += ':'
        # RGB accending
        elif key == 'r': ss[-1].color.r += cfg['color_delta']
        elif key == 'g': ss[-1].color.g += cfg['color_delta']
        elif key == 'b': ss[-1].color.b += cfg['color_delta']
        # RGB decenging
        elif key == 'R': ss[-1].color.r -= cfg['color_delta']
        elif key == 'G': ss[-1].color.g -= cfg['color_delta']
        elif key == 'B': ss[-1].color.b -= cfg['color_delta']
        # Changing position of whole the shape
        elif key == 'W':
            for i in range(0, len(ss[-1].vtx)):
                ss[-1].vtx[i].y += cfg['pos_delta']
        elif key == 'S':
            for i in range(0, len(ss[-1].vtx)):
                ss[-1].vtx[i].y -= cfg['pos_delta']
        elif key == 'A':
            for i in range(0, len(ss[-1].vtx)):
                ss[-1].vtx[i].x -= cfg['pos_delta']
        elif key == 'D':
            for i in range(0, len(ss[-1].vtx)):
                ss[-1].vtx[i].x += cfg['pos_delta']
        # Changing position of the point
        elif key == 'w':
            ss[-1].vtx[-1].y += cfg['pos_delta']
        elif key == 's':
            ss[-1].vtx[-1].y -= cfg['pos_delta']
        elif key == 'a':
            ss[-1].vtx[-1].x -= cfg['pos_delta']
        elif key == 'd':
            ss[-1].vtx[-1].x += cfg['pos_delta']
        # reorder the list of shapes
        elif key == '>':
            ss = [ss[-1]] + ss[:-1]
        elif key == '<':
            ss = ss[1:] + [ss[0]]
        # reorder the list of points
        elif key == '.':
            ss[-1].vtx = [ss[-1].vtx[-1]] + ss[-1].vtx[:-1]
        elif key == ',':
            ss[-1].vtx = ss[-1].vtx[1:] + [ss[-1].vtx[0]]

    glutPostRedisplay()


def mouse(button, state, x, y):
    global cfg
    global ss

    if state != GLUT_DOWN: return
    if button == GLUT_LEFT_BUTTON:
        p = Point(x, height - y)
        if len(ss) == 0: 
            ss.append(Shape())
        ss[-1].vtx.append(p)
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
    cfg = Settings()
    cfg_file = '.lab1rc'
    
    # load config file
    try:
        f = open(cfg_file)
    except IOError:
        print("[INFO] can't find './.lab1rc', using defaults.")
    else:
        with f:
            cmds = [x.strip() for x in f.readlines()]
        map(doCmd, cmds)

    width = 800
    height = 600
    ss = []
    text_buf = cfg['motd']

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB)
    glutInitWindowSize(width, height)

    glutCreateWindow(cfg['title'])
    glEnable(GL_POINT_SMOOTH)

    glutReshapeFunc(reshape)
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutMouseFunc(mouse)

    glutMainLoop()
