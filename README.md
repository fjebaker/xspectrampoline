# xspectrampoline

Installing the XSPEC model library _can be as easy_ as
```bash
pip install xspectrampoline
```
and that's what this package provides.

## Usage

This package is indented only for providing the XSPEC model binaries, and is
not a wrapper around the model library. The minimal wrapper code that exists is
code you would have to write anyway, but beyond that there may are too many
ways the models could be put together for Python usage. That's an exercise left
to the reader.

Whilst you think about that, here's how you can use `xspectrampoline`
```python
# Importing calls FNINIT in the libXS
import xspectrampoline

# Get a handle to the minimal wrapper
lib_xspec = xspectrampoline.get_libraries()

# Get the function by the symbol name
powerlaw = lib_xspec.get_model("C_powerlaw")

# Setup an energy, parameter, and output arrays
energy = np.linspace(0.01, 10.0, 100, dtype=np.float64)
parameters = np.array([3.0], dtype=np.float64)
output = np.zeros(len(energy) - 1, dtype=np.float64)
error = np.zeros(len(energy) - 1, dtype=np.float64)

# Invoke the model
powerlaw(energy, parameters, output, error)

# Then do things with `output`
...
```

## Overwriting which libraries are used

By default `xspectrampoline` bundles everything that is needed to use the XSPEC
model library. But what if you already have HEASOFT / XSPEC installed and want
to use your local version? `xspectrampoline` checks if the `HEADAS` environment
variable is set and determines the library locations accordingly. If you want
to use your local version, just make sure `HEADAS` points to the right location
and your linker paths are configured via `headinit`.

`xspectrampoline` sets the `HEADAS` environment variable if it's not already
set. You can also access the path it uses to resolve the libraries using

```python
import xspectrampoline

headas_path = xspectrampoline.get_HEADAS()
print(headas_path)
```

## How does it work

This package is possible all thanks to Julia's
[BinaryBuilder.jl](https://github.com/JuliaPackaging/BinaryBuilder.jl) who have
done all the hard work for making compiled libraries relatively easy to share
around. The XSPEC model library was cross compiled into
[LibXSPEC_jll.jl](https://github.com/astro-group-bristol/LibXSPEC_jll.jl) for
Linux and MacOS, and `xspectrampoline` is basically those artifacts bundled for
distribution with Python.

## For developers

To bundle things locally, ensure you have `setuptools`, `wheel`, and `build`
installed:
```bash
python3 -m pip install --upgrade setuptool wheel build
```
You can then use the Makefile targets to automate the build commands. The
Makefile fetches the BinaryBuilder.jl artifacts, unpacks them, and runs the
necessary Python packaging commands to create the wheels. Those will then be
available under `./dist` in your local directory.
```
make
```

You can test the packaging by installing from the wheel:
```bash
python -m pip install ./dist/xspectrampoline-0.1.0-py3-none-linux_x86_64.whl
```
selecting the correct platform tag as needed.

There are also handy targets for doing this:
```bash
make install    # install the wheel on your system

make clean      # delete all files (include dist) that were generating during
                # the packaging process
```
