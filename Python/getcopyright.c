/* Return the copyright string for Haven (ODCS Native Edition). */

#include "Python.h"

static const char cprt[] =
"Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.\n"
"All Rights Reserved.\n"
"Built natively for the Open Digital Continuity Standard (ODCS).";

const char *
Py_GetCopyright(void)
{
    return cprt;
}
