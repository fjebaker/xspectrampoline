import importlib.resources
import logging
import os
import pathlib
import sys

logger = logging.getLogger(__name__)


class UnknownLibrary(Exception): ...


LIBXSPEC = "LibXSPEC_v6_35_1"
SHARED_LIB_EXT = "so" if sys.platform.startswith("linux") else "dylib"

# xspectrampoline cannot directly be accessed, because it would initialise the
# module by importing it, which would lead to a circular import as
# xspectrampoline imports xspectrampoline_helpers. This should be a portable
# solution which discovers the location of xspectrampoline relative to
# xspectrampoline_helpers. As these packages are installed together, this
# should always be their relationship.
_xspectrampoline_path = (
    importlib.resources.files("xspectrampoline_helpers") / ".." / "xspectrampoline"
)
_libxspec_path = _xspectrampoline_path / LIBXSPEC

if "HEADAS" not in os.environ:
    os.environ["HEADAS"] = str(_libxspec_path)

_headas_path = pathlib.Path(os.environ.get("HEADAS"))


def get_HEADAS() -> str:
    """
    Returns the HEADAS path currently used by the library.
    """
    return str(_headas_path)


def _get_linkfiles() -> list[tuple[str, str]]:
    linked_files = (_xspectrampoline_path / "LINKEDFILES").read_text().splitlines()
    linked_files = [
        [
            item.strip()
            for item in line.replace("SHARED_EXT", SHARED_LIB_EXT).split("->")
        ]
        for line in linked_files
    ]
    return linked_files


def create_symlinks() -> None:
    """
    Create missing symlinks to common library paths.

    !!! warning
        It is not recommended to use this function as it creates files that are
        not managed or cleaned up by the Python package manager when
        uninstalling or upgrading xspectrampoline. If you need these symlinks
        to exist to compile a library, consider linking against the specific
        version of the library that is shipped instead, e.g. instead of
        `-lcfitsio` use on Linux

            -L $HEADAS/lib -Wl,-rpath,"$HEADAS/lib" -l:libcfitsio.so.10

        Replace .so with dylib on MacOS. This will not only resolve the correct
        version of the library, but hardcode the library search path in the
        binary to wherever you have xspectrampoline installed.

    As Python wheels do not support symlinks, every symlink is replaced with a
    copy of the file it pointed to. For distribution file size reasons, many of
    these symlinks are removed when assembling xspectrampoline. This command is
    intended to repopulate those missing links, but with the caeveat that it
    must be invoked by someone with permissions to create files in the Python
    package library directory. It is therefore not automatically done as part
    of the setup proceedure or installation, as those permissions cannot be
    known ahead of time.
    """
    linked_files = _get_linkfiles()
    for source, dest in linked_files:
        source_path = _libxspec_path / "lib" / source
        dest_path = _libxspec_path / "lib" / dest
        logger.info("Symlink: '%s' -> '%s'", source_path, dest_path)
        source_path.symlink_to(dest_path)


def remove_symlinks() -> None:
    """
    Remove the symlinks created with `create_symlinks`.
    """
    linked_files = _get_linkfiles()

    for source, _ in linked_files:
        source_path = _libxspec_path / "lib" / source
        logger.info("Removing symlink: '%s'", source_path)
        source_path.unlink()


def list_libraries() -> list[str]:
    """
    List all of the libraries (not just XSPEC specific ones) that are
    distributed in this version of xspectrampoline.
    """
    libraries = []
    for file in (_libxspec_path / "lib").iterdir():
        if SHARED_LIB_EXT in file.name:
            libraries.append(file.name)
    return libraries


def get_linker_flags(libraries: list[str], rpath_relative: bool = False) -> list[str]:
    """
    Returns the linker flags needed to compile a model with given libraries.
    Example usage:

        xspectrampoline.get_linker_flags(["cfitsio", "fftw"])

    Raises an `UnknownLibrary` exception if the library is not distributed by
    xspectrampoline. Use `list_libraries` to list all libraries that can be
    used as arguments to this function.

    The function accepts a single keyword argument `rpath_relative`, which is
    used to control whether the rpath linker option should use absolute paths
    (default, `rpath_relative = False`), or relative paths based on `$ORIGIN`.
    The latter should be more portable between different machines, allowing
    e.g.  binary distributions of models, but has the caveat that is assumes
    something about how these packages will be installed by Python on the
    target machine. The first option will prevent any compiled binaries from
    being relocatable between machines, but is guaranteed to work on your
    machine.
    """
    available_libraries = list_libraries()
    selected_libraries = set()
    for lib in libraries:
        found = False
        for _lib in available_libraries:
            if lib in _lib:
                selected_libraries.add(_lib)
                found = True
                break
        if not found:
            raise UnknownLibrary(lib)

    linker_flags = [f"-l:{lib}" for lib in selected_libraries]

    if rpath_relative:
        rpath_flag = f"-Wl,-rpath'$ORIGIN/../xspectrampoline/{LIBXSPEC}/lib'"
    else:
        rpath_flag = f"-Wl,-rpath'{_headas_path}'"

    return [f"-L{_headas_path}", rpath_flag] + linker_flags


__all__ = [
    SHARED_LIB_EXT,
    get_HEADAS,
    create_symlinks,
    remove_symlinks,
    get_linker_flags,
    list_libraries,
]
