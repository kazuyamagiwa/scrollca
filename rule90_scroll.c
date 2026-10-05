/* Infinite scrolling Sierpiński triangle via Rule 90 cellular automaton. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
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
#define SCROLLART "scrollart!"
#define INSERT_CHANCE_PERCENT 8

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

/* Copy CA row into out, sometimes overlaying "scrollart!" for display only. */
static void format_row(const char *row, char *out, int width)
{
    static const char label[] = SCROLLART;
    const int label_len = (int)(sizeof(label) - 1);

    memcpy(out, row, (size_t)width + 1);
    if (width < label_len) {
        return;
    }
    if ((rand() % 100) >= INSERT_CHANCE_PERCENT) {
        return;
    }
    {
        int pos = rand() % (width - label_len + 1);
        memcpy(out + pos, label, (size_t)label_len);
    }
}

int main(void)
{
    int width = get_width();
    char row[MAX_WIDTH + 1];
    char next[MAX_WIDTH + 1];
    char display[MAX_WIDTH + 1];
    char *cur = row;
    char *nxt = next;

    srand((unsigned)time(NULL));
    signal(SIGINT, on_interrupt);
    initial_row(cur, width);

    while (running) {
        format_row(cur, display, width);
        puts(display);
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
