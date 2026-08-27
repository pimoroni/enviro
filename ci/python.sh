SCRIPT_PATH=${BASH_SOURCE-$0}
SCRIPT_PATH=$(dirname "$SCRIPT_PATH")
SCRIPT_PATH=$(realpath "$SCRIPT_PATH")

function qa_prepare_all {
    pip install ruff
}

function qa_check {
    ruff check --config "$SCRIPT_PATH/ruff.toml" "$@"
}

function qa_fix {
    ruff check --config "$SCRIPT_PATH/ruff.toml" --fix "$@"
}

function qa_firmware_check {
    qa_check main.py enviro/
}

function qa_firmware_fix {
    qa_fix main.py enviro/
}
