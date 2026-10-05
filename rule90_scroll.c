/* Infinite scrolling Sierpiński triangle via Rule 90 cellular automaton. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>

#ifdef __unix__
#include <sys/ioctl.h>
#endif

#define ALIVE '#'
#define DEAD  ' '
#define DEFAULT_WIDTH 79
#define MAX_WIDTH 512
#define DELAY_US 50000

static volatile sig_atomic_t running = 1;

static void on_interrupt(int sig)
{
    (void)sig;
    running = 0;
}

static int get_width(void)
{
#ifdef TIOCGWINSZ
    struct winsize ws;
    if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &ws) == 0 && ws.ws_col > 0) {
        int w = (int)ws.ws_col;
        if (w > MAX_WIDTH) {
            return MAX_WIDTH;
        }
        return w;
    }
#endif
    return DEFAULT_WIDTH;
}

static void initial_row(char *row, int width)
{
    memset(row, DEAD, (size_t)width);
    row[width / 2] = ALIVE;
    row[width] = '\0';
}

/* Rule 90 with toroidal edges: alive iff left XOR right. */
static void next_generation(const char *row, char *next, int width)
{
    for (int i = 0; i < width; i++) {
        char left = row[(i - 1 + width) % width];
        char right = row[(i + 1) % width];
        next[i] = (left != right) ? ALIVE : DEAD;
    }
    next[width] = '\0';
}

int main(void)
{
    int width = get_width();
    char row[MAX_WIDTH + 1];
    char next[MAX_WIDTH + 1];
    char *cur = row;
    char *nxt = next;

    signal(SIGINT, on_interrupt);
    initial_row(cur, width);

    while (running) {
        puts(cur);
        fflush(stdout);
        next_generation(cur, nxt, width);
        {
            char *tmp = cur;
            cur = nxt;
            nxt = tmp;
        }
        usleep(DELAY_US);
    }

    fputs("\nStopped. Goodbye.\n", stdout);
    return 0;
}
