import tempfile
import shutil
import os
import hashlib
import pathlib
import time
import zipfile
import base64
import traceback

LIBXSPEC_VERSION = "v6.35.1"
COMPILER_SUPPORT_VERSION = "v1.3.1"


def make_record_entry(filepath: str, package_root: str = "", name="") -> str:
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(sha256.block_size)
            if not chunk:
                break
            sha256.update(chunk)

    digest_bytes = sha256.digest()

    filesize = os.path.getsize(filepath)
    relative_filename = name or filepath[filepath.find(package_root) :]

    base64_digest = base64.urlsafe_b64encode(digest_bytes).rstrip(b"=").decode()

    return f"{relative_filename},sha256={base64_digest},{filesize}"


def zipdir(path: str, zf: zipfile.ZipFile):
    for root, dirs, files in os.walk(path):
        for file in files:
            zf.write(
                os.path.join(root, file),
                os.path.relpath(os.path.join(root, file), os.path.join(path)),
            )


def repackage(
    root: str,
    filename: str,
    libxspec: str,
    support: str,
    platform_tag: str = "py3-none-linux_x86_64",
):
    # TODO: get the version string from the filename
    version = "0.1.0"

    filepath = os.path.join(root, os.path.basename(filename))
    shutil.copy(filename, filepath)

    shutil.unpack_archive(filepath, root, format="zip")

    # The name of the XSPEC directory as it will be in the package
    xspec_dir = os.path.join("xspectrampoline", "LibXSPEC_v6_35_1")
    # The actual path on the machine to where the files currently are
    xspec_dir_path = os.path.join(root, xspec_dir)

    shutil.copytree(os.path.join("artifacts", libxspec), xspec_dir_path)
    # Copy the CompilerSupportLibraries and merge lib and share
    for directory in ("lib", "share"):
        shutil.copytree(
            os.path.join("artifacts", support, directory),
            os.path.join(xspec_dir_path, directory),
            dirs_exist_ok=True,
        )

    record_entries = []
    for dirpath, dirnames, filenames in os.walk(xspec_dir_path):
        filepaths = [os.path.join(dirpath, f) for f in filenames]

        record_entries.extend(
            (make_record_entry(f, package_root=xspec_dir) for f in filepaths)
        )

    # Rewrite the tag for the particular place we're packaging
    dist_info_name = f"xspectrampoline-{version}.dist-info"
    dist_info_path = pathlib.Path(root) / dist_info_name

    wheel_path = dist_info_path / "WHEEL"
    new_wheel = wheel_path.read_text().replace(
        "Tag: py3-none-any", f"Tag: {platform_tag}"
    )
    wheel_path.write_text(new_wheel)

    # Recalculate the WHEEL record entry
    wheel_record = make_record_entry(str(wheel_path), name=f"{dist_info_name}/WHEEL")

    # Write the new record file
    record_file = dist_info_path / "RECORD"

    new_record = record_entries + record_file.read_text().splitlines()
    new_record = [r for r in new_record if "info/WHEEL,sha" not in r] + [wheel_record]

    # Do a quick swap
    _tmp = new_record[-2]
    new_record[-2] = new_record[-1]
    new_record[-1] = _tmp

    record_file.write_text("\n".join(new_record))

    # TODO: copy over the licenses

    # Move everything into a directory
    new_name = f"xspectrampoline-{version}-{platform_tag}"
    new_dir = os.path.join(root, new_name)
    os.mkdir(os.path.join(root, new_dir))
    shutil.move(str(dist_info_path), new_dir)
    shutil.move(os.path.join(root, "xspectrampoline"), new_dir)

    # Now rezip and pray. Need to use zipfile here because of the timestamps of
    # the files
    new_wheel = f"{new_name}.whl"
    with zipfile.ZipFile(new_wheel, "w", strict_timestamps=False) as zf:
        zipdir(new_dir + "/", zf)

    # And restore it's location
    shutil.move(new_wheel, "./dist")


if __name__ == "__main__":
    tmpdir = "delete-me"
    try:
        shutil.rmtree(tmpdir)
    except:
        ...
    os.mkdir(tmpdir)

    platform_info = [
        (
            "py3-none-linux_x86_64",
            f"LibXSPEC.{LIBXSPEC_VERSION}.x86_64-linux-gnu-libgfortran5",
            f"CompilerSupportLibraries.{COMPILER_SUPPORT_VERSION}.x86_64-linux-gnu-libgfortran5",
        ),
        (
            "py3-none-macosx_15_0_arm64",
            f"LibXSPEC.{LIBXSPEC_VERSION}.aarch64-apple-darwin-libgfortran5",
            f"CompilerSupportLibraries.{COMPILER_SUPPORT_VERSION}.aarch64-apple-darwin-libgfortran5",
        ),
    ]
    original_wheel = "./dist/xspectrampoline-0.1.0-py3-none-any.whl"

    no_errors = True

    for platform_tag, libxspec, support in platform_info:
        print(f"Packaging for {platform_tag}")
        try:
            repackage(
                os.path.abspath("delete-me"),
                original_wheel,
                libxspec,
                support,
                platform_tag=platform_tag,
            )
        except Exception as e:
            print(traceback.format_exc())
            no_errors = False

    shutil.rmtree(tmpdir)

    if no_errors:
        print(f"No errors occured. Deleting the original wheel '{original_wheel}'")
        os.remove(original_wheel)
    else:
        raise Exception("Errors Occured")
