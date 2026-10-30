// Resource script for Haven core DLL.
// Holds version and metadata information for Open Digital Continuity Standard (ODCS).
//
#pragma code_page(1252)
#include "winver.h"

#define PYTHON_COMPANY   "Anirudha Puthraya / Haven Language Core"
#define PYTHON_COPYRIGHT "Copyright \xA9 2026 Haven Language Foundation & Anirudha Puthraya. Built for Open Digital Continuity Standard (ODCS)."

#define MS_WINDOWS
#include "patchlevel.h"
#ifdef Py_DEBUG
#   define PYTHON_DEBUG_EXT "_d"
#else
#   define PYTHON_DEBUG_EXT
#endif

#define PYTHON_VERSION HAVEN_VERSION "\0"

/* 64-bit version number as comma-separated list of 4 16-bit ints */
#if PY_MICRO_VERSION > 64
#   error "PY_MICRO_VERSION > 64"
#endif
#if PY_RELEASE_LEVEL > 99
#   error "PY_RELEASE_LEVEL > 99"
#endif
#if PY_RELEASE_SERIAL > 9
#   error "PY_RELEASE_SERIAL > 9"
#endif
#define PYVERSION64 0, 1, 0, 0
