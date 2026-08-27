export TERM=${TERM:="xterm-256color"}

MICROPYTHON_FLAVOUR="micropython"
MICROPYTHON_VERSION="v1.29.0"

PIMORONI_PICO_FLAVOUR="pimoroni"
PIMORONI_PICO_VERSION="1a503d31f28c1b103e852b3a654db18fc6accf2e"

PY_DECL_VERSION="v0.0.5"
DIR2UF2_VERSION="v0.1.0"

BOARD="enviro"


function log_inform {
	echo -e "$(tput setaf 6)$1$(tput sgr0)"
}

function ci_pimoroni_pico_clone {
    log_inform "Using Pimoroni Pico $PIMORONI_PICO_FLAVOUR/$PIMORONI_PICO_VERSION"
    git clone https://github.com/$PIMORONI_PICO_FLAVOUR/pimoroni-pico "$CI_BUILD_ROOT/pimoroni-pico"
    git -C "$CI_BUILD_ROOT/pimoroni-pico" checkout $PIMORONI_PICO_VERSION
    git -C "$CI_BUILD_ROOT/pimoroni-pico" submodule update --init
}

function ci_micropython_clone {
    log_inform "Using MicroPython $MICROPYTHON_FLAVOUR/$MICROPYTHON_VERSION"
    git clone https://github.com/$MICROPYTHON_FLAVOUR/micropython "$CI_BUILD_ROOT/micropython"
    git -C "$CI_BUILD_ROOT/micropython" checkout $MICROPYTHON_VERSION
    git -C "$CI_BUILD_ROOT/micropython" submodule update --init lib/pico-sdk
    git -C "$CI_BUILD_ROOT/micropython" submodule update --init lib/cyw43-driver
    git -C "$CI_BUILD_ROOT/micropython" submodule update --init lib/lwip
    git -C "$CI_BUILD_ROOT/micropython" submodule update --init lib/mbedtls
    git -C "$CI_BUILD_ROOT/micropython" submodule update --init lib/micropython-lib
    git -C "$CI_BUILD_ROOT/micropython" submodule update --init lib/tinyusb
    git -C "$CI_BUILD_ROOT/micropython" submodule update --init lib/btstack
}

function ci_tools_clone {
    mkdir -p "$CI_BUILD_ROOT/tools"
    git clone https://github.com/gadgetoid/py_decl -b "$PY_DECL_VERSION" "$CI_BUILD_ROOT/tools/py_decl"
    git clone https://github.com/gadgetoid/dir2uf2 -b "$DIR2UF2_VERSION" "$CI_BUILD_ROOT/tools/dir2uf2"
}

function ci_micropython_build_mpy_cross {
    ccache --zero-stats || true
    CROSS_COMPILE="ccache " make -C "$CI_BUILD_ROOT/micropython/mpy-cross"
    ccache --show-stats || true
}

function ci_apt_install_build_deps {
    sudo apt update && sudo apt install ccache
}

function ci_install_build_deps {
    ci_apt_install_build_deps
}

function ci_python_prepare {
    python3 -m pip install -r "${CI_BUILD_ROOT}/micropython/tools/mpremote/requirements.txt"
    python3 -m pip install -r "${CI_PROJECT_ROOT}/ci/requirements.txt"
}

function ci_prepare_all {
    ci_tools_clone
    ci_micropython_clone
    ci_pimoroni_pico_clone
    ci_micropython_build_mpy_cross
}

function ci_debug {
    log_inform "Project root: $CI_PROJECT_ROOT"
    log_inform "Build root: $CI_BUILD_ROOT"
}

function micropython_version {
    echo "MICROPY_GIT_TAG=$MICROPYTHON_VERSION, $BOARD $TAG_OR_SHA" >> $GITHUB_ENV
    echo "MICROPY_GIT_HASH=$MICROPYTHON_VERSION-$TAG_OR_SHA" >> $GITHUB_ENV
}

function ci_genversion {
    MICROPY_BOARD_DIR="$CI_PROJECT_ROOT/board"
    if [ -z ${CI_RELEASE_FILENAME+x} ]; then
        CI_RELEASE_FILENAME=$BOARD
    fi

    MICROPYTHON_SHA=`git -C "$CI_BUILD_ROOT/micropython" describe --always --long --abbrev=40 HEAD`
    PIMORONI_PICO_SHA=`git -C "$CI_BUILD_ROOT/pimoroni-pico" describe --always --long --abbrev=40 HEAD`

    cat << EOF > "$MICROPY_BOARD_DIR/version.py"
DATE="`date`"
BUILD="$CI_RELEASE_FILENAME"
MICROPYTHON_SHA="$MICROPYTHON_SHA"
PIMORONI_PICO_SHA="$PIMORONI_PICO_SHA"
EOF
}

function ci_cmake_configure {
    MICROPY_BOARD_DIR="$CI_PROJECT_ROOT/board"
    BUILD_DIR="$CI_BUILD_ROOT/build-$BOARD"
    cmake -S "$CI_BUILD_ROOT/micropython/ports/rp2" -B "$BUILD_DIR" \
    -DPICOTOOL_FORCE_FETCH_FROM_GIT=1 \
    -DPICO_BUILD_DOCS=0 \
    -DPICO_NO_COPRO_DIS=1 \
    -DPICOTOOL_FETCH_FROM_GIT_PATH="$CI_BUILD_ROOT/tools/picotool" \
    -DPIMORONI_PICO_PATH="$CI_BUILD_ROOT/pimoroni-pico" \
    -DMICROPY_MANIFEST_PIMORONI_PICO_PATH="$CI_BUILD_ROOT/pimoroni-pico" \
    -DUSER_C_MODULES="$MICROPY_BOARD_DIR/usermodules.cmake" \
    -DMICROPY_BOARD_DIR="$MICROPY_BOARD_DIR" \
    -DMICROPY_BOARD="$BOARD" \
    -DCMAKE_C_COMPILER_LAUNCHER=ccache \
    -DCMAKE_CXX_COMPILER_LAUNCHER=ccache
}

function ci_cmake_build {
    if [ -z ${CI_RELEASE_FILENAME+x} ]; then
        CI_RELEASE_FILENAME=$BOARD
    fi

    ci_genversion

    BUILD_DIR="$CI_BUILD_ROOT/build-$BOARD"
    ccache --zero-stats || true
    cmake --build "$BUILD_DIR" -j 2 || return $?
    ccache --show-stats || true

    log_inform "Copying firmware .uf2 to $(pwd)/$CI_RELEASE_FILENAME.uf2"
    cp "$BUILD_DIR/firmware.uf2" "$CI_RELEASE_FILENAME.uf2"
}

# Pack the Enviro Python files into a LittleFS image and append it to the firmware.
# dir2uf2 reads the filesystem offset and size from the firmware's binary info,
# and writes both a filesystem-only .uf2 and a combined firmware + filesystem .uf2.
function ci_build_filesystem {
    if [ -z ${CI_RELEASE_FILENAME+x} ]; then
        CI_RELEASE_FILENAME=$BOARD
    fi

    PYTHONPATH="$CI_BUILD_ROOT/tools/py_decl" \
    "$CI_BUILD_ROOT/tools/dir2uf2/dir2uf2" \
    --append-to "$CI_RELEASE_FILENAME.uf2" \
    --manifest "$CI_PROJECT_ROOT/uf2-manifest.txt" \
    --filename with-filesystem.uf2 \
    "$CI_PROJECT_ROOT/" || return $?

    rm -f with-filesystem.bin
    mv with-filesystem.uf2 "$CI_RELEASE_FILENAME-filesystem-only.uf2"

    log_inform "Built $CI_RELEASE_FILENAME-filesystem-only.uf2 and $CI_RELEASE_FILENAME-with-filesystem.uf2"
}

# Zip up just the Enviro Python files, for copying onto an existing install
function ci_build_zip {
    if [ -z ${CI_RELEASE_FILENAME+x} ]; then
        CI_RELEASE_FILENAME=$BOARD
    fi

    STAGING_DIR="$CI_BUILD_ROOT/zip/enviro"
    rm -rf "$CI_BUILD_ROOT/zip"
    mkdir -p "$STAGING_DIR"

    while read -r pattern; do
        [ -z "$pattern" ] && continue
        for file in $CI_PROJECT_ROOT/$pattern; do
            [ -e "$file" ] || continue
            target="$STAGING_DIR/${file#$CI_PROJECT_ROOT/}"
            mkdir -p "$(dirname "$target")"
            cp "$file" "$target"
        done
    done < "$CI_PROJECT_ROOT/uf2-manifest.txt"

    (cd "$CI_BUILD_ROOT/zip" && zip -r "$CI_BUILD_ROOT/$CI_RELEASE_FILENAME.zip" enviro)
}

if [ -z ${CI_USE_ENV+x} ] || [ -z ${CI_PROJECT_ROOT+x} ] || [ -z ${CI_BUILD_ROOT+x} ]; then
    SCRIPT_PATH=${BASH_SOURCE-$0}
    SCRIPT_PATH=$(dirname "$SCRIPT_PATH")
    CI_PROJECT_ROOT=$(realpath "$SCRIPT_PATH/..")
    CI_BUILD_ROOT=$(pwd)
fi

ci_debug
