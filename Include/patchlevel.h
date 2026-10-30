#ifndef HAVEN_PATCHLEVEL_H
#define HAVEN_PATCHLEVEL_H

#define HAVEN_VERSION_MAJOR     1
#define HAVEN_VERSION_MINOR     0
#define HAVEN_VERSION_MICRO     0
#define HAVEN_VERSION_LEVEL     "final"
#define HAVEN_VERSION_SERIAL    0

#define HAVEN_VERSION           "1.0.0"
#define HAVEN_BANNER            "Haven 1.0.0 (ODCS Native Production Core) [Windows/MSVC]"
#define HAVEN_COPYRIGHT         "Copyright (c) 2026 Anirudha Puthraya. All Rights Reserved."

/* Values for PY_RELEASE_LEVEL */
#define PY_RELEASE_LEVEL_ALPHA  0xA
#define PY_RELEASE_LEVEL_BETA   0xB
#define PY_RELEASE_LEVEL_GAMMA  0xC     /* For release candidates */
#define PY_RELEASE_LEVEL_FINAL  0xF     /* Serial should be 0 here */

/* Version parsed out into numeric values */
#define PY_MAJOR_VERSION        3
#define PY_MINOR_VERSION        16
#define PY_MICRO_VERSION        0
#define PY_RELEASE_LEVEL        PY_RELEASE_LEVEL_FINAL
#define PY_RELEASE_SERIAL       0

/* Version as a string */
#define PY_VERSION              "3.16.0"

#define _Py_PACK_FULL_VERSION(X, Y, Z, LEVEL, SERIAL) ( \
    (((X) & 0xff) << 24) |                              \
    (((Y) & 0xff) << 16) |                              \
    (((Z) & 0xff) << 8) |                               \
    (((LEVEL) & 0xf) << 4) |                            \
    (((SERIAL) & 0xf) << 0))

/* Version as a single 4-byte hex number */
#define PY_VERSION_HEX _Py_PACK_FULL_VERSION( \
    PY_MAJOR_VERSION,                         \
    PY_MINOR_VERSION,                         \
    PY_MICRO_VERSION,                         \
    PY_RELEASE_LEVEL,                         \
    PY_RELEASE_SERIAL)

#define PYTHON_API_VERSION 1013
#define PYTHON_API_STRING "1013"
#define PYTHON_ABI_VERSION 3
#define PYTHON_ABI_STRING "3"

#endif /* !HAVEN_PATCHLEVEL_H */
