
LIBXSPEC_VERSION = v6.35.1
LIBXSPEC_BUILD_VERSION = +1

ARTIFACTS_DIR := artifacts

ALL_PLATFORMS := x86_64-linux-gnu-libgfortran5 \
				 aarch64-apple-darwin-libgfortran5

ALL_LIBXSPEC_PATHS := $(foreach PLAT,$(ALL_PLATFORMS),LibXSPEC.$(LIBXSPEC_VERSION).$(PLAT))
ALL_ARTIFACT_PATHS := $(foreach ARTIFACT,$(ALL_LIBXSPEC_PATHS),$(ARTIFACTS_DIR)/$(ARTIFACT))

ARTIFACT_DOWNLOAD_ROOT := \
	https://github.com/astro-group-bristol/LibXSPEC_jll.jl/releases/download/LibXSPEC-$(LIBXSPEC_VERSION)$(LIBXSPEC_BUILD_VERSION)

all: all-artifacts wheels

.PHONY: all-artifacts
all-artifacts: $(ARTIFACTS_DIR) $(ALL_ARTIFACT_PATHS)

$(ARTIFACTS_DIR):
	mkdir -p $@

# Download the artifact from the remote location
$(ARTIFACTS_DIR)/%.tar.gz:
	curl -SL $(ARTIFACT_DOWNLOAD_ROOT)/$*.tar.gz \
		-o $@

# Unpack the artifact
$(ARTIFACTS_DIR)/%: $(ARTIFACTS_DIR)/%.tar.gz
	mkdir -p $@
	tar -C $@ -xzf $<

.PHONY: wheels
wheels:
	python3 -m build --wheel
	python3 dist-package.py

.PHONY: install
install:
	python -m pip install dist/xspectrampoline-0.1.0-py3-none-linux_x86_64.whl

.PHONY: clean
clean: clean-dist
	python -m pip uninstall -y xspectrampoline

.PHONY: clean-dist
clean-dist:
	rm -rf xspectrampoline.egg-info build dist delete-me

.PHONY: clean-artifacts
clean-artifacts:
	rm -rf $(ARTIFACTS_DIR)
