import pytest
import xspectrampoline_helpers as helpers

def test_linker_arguments():
    flags = helpers.get_linker_flags(["fftw3", "XSFunctions", "cfitsio"])

    flag_string = " -- ".join(flags)

    assert "libXSFunctions" in flag_string
    assert "libcfitsio" in flag_string
