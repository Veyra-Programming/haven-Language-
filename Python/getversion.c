/* Return the full version string for Haven (ODCS Native Edition). */

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
    PyOS_snprintf(version, sizeof(version), "Haven %s (ODCS Edition) [Open Digital Continuity Standard] on Windows", HAVEN_VERSION);
}

const char *
Py_GetVersion(void)
{
    _Py_InitVersion();
    return version;
}

// Export the version as a constant.
const unsigned long Py_Version = PY_VERSION_HEX;
