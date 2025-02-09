#!/bin/bash
OS=$1
case "$OS" in
    ubuntu|debian)
        cp cbook.py cbook
        sudo chmod +x cbook
        ;;
    fedora|rhel|centos)
        cp cbook.py cbook
        sudo chmod +x cbook
        ;;
    arch)
        cp cbook.py cbook
        sudo chmod +x cbook
        
        ;;
    macOS)
        cp cbook.py cbook
        chmod +x cbook
        ;;
    Windows)
        echo "To use cbook, execute cbook.bat"
        echo "Add cbook.bat to the path"
        exit 0
        ;;
    *)
        echo "Unknown Os: $OS"
        exit 1
        ;;
esac

echo "Symbolicly link to /usr/local/bin/"

OS=$1
case "$OS" in
    ubuntu|debian)
        sudo ln -s cbook /usr/local/bin
        ;;
    fedora|rhel|centos)
        sudo ln -s cbook /usr/local/bin
        ;;
    arch)
        sudo ln -s cbook /usr/local/bin
        ;;
    macOS)
        ln -s cbook /usr/local/bin
        ;;
    *)
        echo "Unknown Os: $OS"
        exit 1
        ;;
esac

exit 0
