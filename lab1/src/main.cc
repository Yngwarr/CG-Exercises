#include <cstdlib>
#include <iostream>
#include <vector>

#include <GL/gl.h>
#include <GL/glu.h>
#include <GL/glut.h>

#define WIN_TITLE  "Первая лаба"

/* TODO add own color to every primitive */

struct point_t
{
	GLint x, y;
	point_t() {}
	point_t(GLint _x, GLint _y) : x(_x), y(_y) {}
};

struct color_t
{
	GLubyte r;
	GLubyte g;
	GLubyte b;
	color_t(GLubyte _r, GLubyte _g, GLubyte _b) :
		r(_r), g(_g), b(_b) {}
	color_t invert()
	{
		color_t res(r ^ 0xFF, b ^ 0xFF, g ^ 0xFF);
		return res;
	}
};

/* globals. don't like globals. */
GLint width = 800, height = 600;
color_t color(0, 0, 0);

std::vector<std::vector<point_t>> vs(1);

void display()
{
	glClearColor(0.3, 0.3, 0.3, 1);
	glClear(GL_COLOR_BUFFER_BIT);
	//glPointSize(6);
	glLineWidth(3);

	//if (vs.empty() || vs.back().empty()) goto q_display;
		
	glColor3ub(color.r, color.g, color.b);
	for (auto ps : vs) {
		glBegin(GL_POLYGON);
		for (int i = 0; i < ps.size(); i++)
			glVertex2i(ps[i].x, ps[i].y);
		glEnd();
	}

	glColor3ub(color.r ^ 0xFF, color.g ^ 0xFF, color.b ^ 0xFF);
	glBegin(GL_LINE_LOOP);
	for (int i = 0; i < vs.back().size(); i++)
		glVertex2i(vs.back()[i].x, vs.back()[i].y);
	glEnd();

	glRasterPos2i(0,0);
	glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, 'X');

quit:
	glFinish();
}

/* TODO reshape is dead */
void reshape(GLint w, GLint h)
{
	//std::cerr << "reshape." << w << '.' << h << '.';
	width = w;
	height = h;
	glViewport(0, 0, w, h);
	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	gluOrtho2D(0, w, 0, h);
	//gluOrtho2D(0, w, h, 0);
	glMatrixMode(GL_MODELVIEW);
	glLoadIdentity();
}

void keyboard(unsigned char key, int x, int y)
{
	int i, n = vs.back().size();
	/* Изменение RGB-компонент цвета точек */
	if (key == 'r') color.r += 5;
	if (key == 'g') color.g += 5;
	if (key == 'b') color.b += 5;
	if (key == 'R') color.r -= 5;
	if (key == 'G') color.g -= 5;
	if (key == 'B') color.b -= 5;
	/* Изменение XY-кординат точек */
	if (key == 'w') for (i = 0; i < n; i++) vs.back()[i].y += 9;
	if (key == 's') for (i = 0; i < n; i++) vs.back()[i].y -= 9;
	if (key == 'a') for (i = 0; i < n; i++) vs.back()[i].x -= 9;
	if (key == 'd') for (i = 0; i < n; i++) vs.back()[i].x += 9;
	glutPostRedisplay();
}

void mouse(int button, int state, int x, int y)
{
	/* клавиша была нажата, но не отпущена */
	if (state != GLUT_DOWN) return;
	/* новая точка по левому клику */
	if (button == GLUT_LEFT_BUTTON) {
		point_t p(x, height - y);
		if (vs.empty()) {
			std::vector<point_t> ps;
			vs.push_back(ps);
		}
		vs.back().push_back(p);
	}
	/* удаление последней точки по правому клику */
	if (button == GLUT_RIGHT_BUTTON) {
		if (vs.empty()) goto quit;
		if (vs.back().empty()) {
			vs.pop_back();
			goto quit;
		}
		vs.back().pop_back();
	}
	if (button == GLUT_MIDDLE_BUTTON) {
		vs.push_back(std::vector<point_t>(0));
	}
quit:
	glutPostRedisplay();
}

int main(int argc, char **argv)
{
	glutInit(&argc, argv);
	glutInitDisplayMode(GLUT_RGB);
	glutInitWindowSize(width, height);
	glutCreateWindow(WIN_TITLE);
	glEnable(GL_POINT_SMOOTH);

	glutReshapeFunc(reshape);
	glutDisplayFunc(display);
	glutKeyboardFunc(keyboard);
	glutMouseFunc(mouse);

	glutMainLoop();
	return 0;
}
