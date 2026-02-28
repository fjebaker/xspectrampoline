import importlib
import ctypes

__xspec_path = importlib.resources.files("xspectrampoline") / "LibXSPEC_v6_35_1"
os.environ["HEADAS"] = str(__xspec_path.abspath())

lib_XS = ctypes.CDLL(__xspec_path / "lib" / "libXS.so")
lib_XSFunctions = ctypes.CDLL(__xspec_path / "lib" / "libXSFunctions.so")
lib_XSUtil = ctypes.CDLL(__xspec_path / "lib" / "libXSUtil.so")
lib_XSFunctions.FNINIT()

print("INIT DONE")
