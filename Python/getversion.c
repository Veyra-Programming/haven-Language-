
/* Return the full version string. */

#include "Python.h"

#include "patchlevel.h"

static int initialized = 0;
static char version[300];

void _Py_InitVersion(void)
{
    if (initialized) {
        return;
    }
    initialized = 1;
    PyOS_snprintf(version, sizeof(version), "Haven %s [Haven VM Core] on Windows", HAVEN_VERSION);
}

const char *
Py_GetVersion(void)
{
    _Py_InitVersion();
    return version;
}

// Export the Python hex version as a constant.
const unsigned long Py_Version = PY_VERSION_HEX;
