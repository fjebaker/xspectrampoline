import importlib.resources
import ctypes
import os
import pathlib
import traceback
import logging
import sys

SHARED_LIB_EXT = ".so" if sys.platform.startswith("linux") else ".dylib"


class NoLibXSPEC(Exception): ...


logger = logging.getLogger(__name__)

__xspectrampoline_path = (
    importlib.resources.files("xspectrampoline") / "LibXSPEC_v6_35_1"
)

if "HEADAS" not in os.environ:
    os.environ["HEADAS"] = str(__xspectrampoline_path)

__headas_path = pathlib.Path(os.environ.get("HEADAS"))

# Load the various libraries
try:
    lib_XS = ctypes.CDLL(__headas_path / "lib" / f"libXS{SHARED_LIB_EXT}")
    lib_XSFunctions = ctypes.CDLL(
        __headas_path / "lib" / f"libXSFunctions{SHARED_LIB_EXT}"
    )
    lib_XSUtil = ctypes.CDLL(__headas_path / "lib" / f"libXSUtil{SHARED_LIB_EXT}")
except OSError:
    logging.error(traceback.format_exc())
    logging.error(
        "Failed to load LibXSPEC. If you have $HEADAS set in your envrionment, "
        "try unsetting it to use the bundled XSPEC installation. If HEADAS is "
        "not set, please open an issue on the xspectrampoline repository with "
        "the logs and a brief description of your environment."
    )
    raise NoLibXSPEC()


# Initialise XSPEC functions
lib_XSFunctions.FNINIT()


def getHEADAS() -> str:
    """
    Returns the HEADAS path currently used by the library.
    """
    return str(__headas_path)


__all__ = [getHEADAS]
