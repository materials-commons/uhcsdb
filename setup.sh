#!/bin/bash
# usage: ./setup.sh
#
# This script will set up the UHCSDB application. This includes
# downloading the data from https://materialsdata.nist.gov/handle/11256/940,
# generating thumbnails and images, placing the data in the correct
# spot, installing python dependencies, creating the secret_key, and
# prompting for ports, etc... that the webserver should run on.
#

function determine_download_command() {
    DOWNLOAD_COMMAND=""

    echo ""
    if command -v curl &>/dev/null; then
        DOWNLOAD_COMMAND=curl
    elif command -v wget &>/dev/null; then
        DOWNLOAD_COMMAND=wget
    else
        echo "Neither 'curl' or 'wget' commands found found. These are required to download the data."
        echo "Please install either curl or wget and ensure it is in your path."
        exit 1
    fi

    echo "Using ${DOWNLOAD_COMMAND} to download the data for UHCSDB."
}

function check_if_convert_is_installed() {
    if ! command -v convert &>/dev/null; then
        echo "The 'convert' command cannot be found. Please ensure that it is in installed and in your path."
        echo "The 'convert' command is usually available in the imagemagick package."
        exit 1
    fi
}

function cleanup_existing_setup() {
    rm -rf downloadtmp
    rm -rf venv
    rm -rf uhcsdb/static/thumbs
    rm -rf uhcsdb/static/micrographs
    rm -rf uhcsdb/static/representations
    rm -rf uhcsdb/static/embed
    rm -f uhcsdb/microstructures.sqlite
    rm -f uhcsdb/secret_key
}

function download_and_unpack_all_data() {
    echo "Downloading and unpacking data..."
    echo ""
    download_and_unpack microstructures.sqlite
    download_and_unpack micrographs.zip
    download_and_unpack embed.zip
    download_and_unpack figures.zip
    download_and_unpack representations.zip
}

function download_and_unpack() {
    DOWNLOAD=$1
    echo "Downloading ${DOWNLOAD}..."
    if [ "${DOWNLOAD_COMMAND}" = "curl" ]; then
        curl "${HANDLE_DOWNLOAD_URL}/${DOWNLOAD}?isAllowed=y" -o "${DOWNLOAD}" >/dev/null 2>&1
    else
        wget "${HANDLE_DOWNLOAD_URL}"/"${DOWNLOAD}"
    fi

    ext="${DOWNLOAD##*.}"
    if [ "${ext}" = "zip" ]; then
        echo "Unpacking zip archive..."
        unzip "${DOWNLOAD}" >/dev/null 2>&1
    fi

    echo ""
}

function convert_images() {
    echo "Converting images..."
    mkdir micrographs/png
    for image in micrographs/*; do
        pngname=$(basename "${image%.*}".png)
        convert -resize 50% "${image}" micrographs/png/"${pngname}" 2>/dev/null
    done
}

function create_thumbnails() {
    echo "Creating thumbnails..."
    mkdir micrographs/thumbs
    for image in micrographs/*; do
        pngname=$(basename "${image%.*}".png)
        convert -resize 148x120 "${image}" micrographs/thumbs/"${pngname}" 2>/dev/null
    done
}

function move_temporary_files_and_dirs() {
    echo "Setting up data and images..."
    mv micrographs/thumbs ../uhcsdb/static
    mv micrographs/png ../uhcsdb/static/micrographs
    mv microstructures.sqlite ../uhcsdb
    mv representations ../uhcsdb/static
    mv embed ../uhcsdb/static
}

function install_python_dependencies() {
    echo "Creating Python Virtual Environment.."
    cd ..
    python3 -m venv venv
    source venv/bin/activate

    echo "Installing python dependencies..."
    pip install -qr requirements.txt
    pip install -q gunicorn
}

function create_secret_key() {
    while true; do
        read -p "Enter secret key: " -r
        if [ "${REPLY}" != "" ]; then
            echo -n "${REPLY}" >../uhcsdb/secret_key
            break
        fi
    done
}

HANDLE_DOWNLOAD_URL=https://materialsdata.nist.gov/bitstream/handle/11256/940

determine_download_command
check_if_convert_is_installed
cleanup_existing_setup

if [ ! -d "downloadtmp" ]; then
    mkdir downloadtmp
fi

cd downloadtmp || exit 1

download_and_unpack_all_data
convert_images
create_thumbnails
move_temporary_files_and_dirs
create_secret_key
install_python_dependencies

echo ""
echo "UHCSDB setup is complete."
echo ""
echo "The python depencies have been installed into a virtual environment. You should activate this"
echo "virtual env before running the web application. To activate type: source venv/bin/activate"
echo ""
echo "To start the web application please run the uhcsdb/launch.sh command."
echo "By default the webserver will use ports 8000 and 8010. If you want to run on"
echo "different ports set the environment variables UHCSDB_PORT and UHCSDB_BOKEH_PORT."
echo "Please see uhcsdb/launch.sh for more details."

