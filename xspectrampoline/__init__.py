import importlib.resources
import ctypes
import os
import pathlib
import traceback
import logging
import sys
import numpy as np

from typing import Optional

SHARED_LIB_EXT = ".so" if sys.platform.startswith("linux") else ".dylib"


class NoLibXSPEC(Exception): ...


logger = logging.getLogger(__name__)

__xspectrampoline_path = (
    importlib.resources.files("xspectrampoline") / "LibXSPEC_v6_35_1"
)

if "HEADAS" not in os.environ:
    os.environ["HEADAS"] = str(__xspectrampoline_path)

__headas_path = pathlib.Path(os.environ.get("HEADAS"))


def _dlopen_wrapper(path: pathlib.Path) -> ctypes.CDLL:
    """
    A wrapper around `ctypes.CDLL` that is used for all `dlopen` calls. The
    indended purpose is to configure all the mode flags in one place.
    """
    return ctypes.CDLL(path, mode=ctypes.RTLD_GLOBAL)


class LibXSPEC:
    def __init__(self, lib_xs, lib_xs_functions, lib_xs_utils):
        self.lib_xs = lib_XS
        self.lib_xs_functions = lib_xs_functions
        self.lib_xs_utils = lib_xs_utils

    @staticmethod
    def _wrap_Fortran_interface(f) -> callable:
        f.argtypes = [
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
        ]
        f.restype = None

        def _wrapper(
            domain: np.array, parameter: np.array, output: np.array, error: np.array
        ) -> None:
            return f(
                domain.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                ctypes.byref(ctypes.c_int(len(output))),
                parameter.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                ctypes.byref(ctypes.c_int(1)),
                output.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                error.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
            )

        return _wrapper

    @staticmethod
    def _wrap_C_interface(f) -> callable:
        f.argtypes = [
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_char_p,
        ]
        f.restype = None

        def _wrapper(
            domain: np.array,
            parameter: np.array,
            output: np.array,
            error: np.array,
            init_str: str = "",
        ) -> None:
            return f(
                domain.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                ctypes.c_int(len(output)),
                parameter.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                ctypes.c_int(1),
                output.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                error.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                init_str.encode("ascii"),
            )

        return _wrapper

    def get_model(self, symbol: str, interface: Optional[str] = None) -> callable:
        """
        Obtain a callable that invokes a model with the standard XSPEC model
        interface.
        """
        f = getattr(self.lib_xs_functions, symbol)
        if interface == "fortan" or symbol.endswith("_"):
            return self._wrap_Fortran_interface(f)
        elif interface == "c" or symbol.startswith("C_"):
            return self._wrap_C_interface(f)
        else:
            if interface is not None:
                raise Exception(f"Unknown function interface '{interface}'")
            else:
                raise Exception(
                    f"Could not determine interface for '{symbol}'. Use the `interface` kwarg to set the wrapper type."
                )


# Load the various libraries
try:
    lib_XS = _dlopen_wrapper(__headas_path / "lib" / f"libXS{SHARED_LIB_EXT}")
    lib_XSFunctions = _dlopen_wrapper(
        __headas_path / "lib" / f"libXSFunctions{SHARED_LIB_EXT}"
    )
    lib_XSUtil = _dlopen_wrapper(__headas_path / "lib" / f"libXSUtil{SHARED_LIB_EXT}")
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


def get_libXSPEC() -> LibXSPEC:
    """
    Get a handle to all of the XSPEC libraries.
    """
    return LibXSPEC(lib_XS, lib_XSFunctions, lib_XSUtil)


def getHEADAS() -> str:
    """
    Returns the HEADAS path currently used by the library.
    """
    return str(__headas_path)


__all__ = [getHEADAS]
