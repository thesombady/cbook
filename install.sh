#!/bin/bash

OS=""
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if [ -f /etc/os-release ]; then
        OS=$(grep ^ID= /etc/os-release | cut -d= -f2 | tr -d '"')
    else
        OS="Linux"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    OS="Windows"
else
    OS="Unknown"
fi


# # List of required commands
dependencies=("fzf" "grep")

# Function to check if a command exists
check_dependency() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "\e[31mDependency: $1 is not installed\e[0m"
        missing_deps=true
    else
        echo -e "\e[34mDependency: $1 is installed\e[0m"
    fi
}

check_python_version() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
        PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

        if [[ "$PYTHON_MAJOR" -eq 3 && "$PYTHON_MINOR" -ge 11 ]]; then
            echo -e "\e[34mPython $PYTHON_VERSION is installed (meets requirement)\e[0m"
        else
            echo -e "\e[31mPython $PYTHON_VERSION found, but version 3.11+ is required\e[0m"
            missing_deps=true
        fi
    else
        echo -e "\e[31mPython 3 is not installed\e[0m"
        missing_deps=true
    fi
}

# Flag to track missing dependencies
missing_deps=false

# Loop through dependencies and check each
for dep in "${dependencies[@]}"; do
    check_dependency "$dep"
done
 
# Check Python version (must be >= 3.11)

check_python_version

# Final message
if $missing_deps; then
    echo -e "\e[31mSome dependencies are missing. Please install them before proceeding.\e[0m"
    case "$OS" in
        ubuntu|debian)
            echo "  sudo apt install <package>"
            ;;
        fedora|rhel|centos)
            echo "  sudo dnf install <package>"
            ;;
        arch)
            echo "  sudo pacman -S <package>"
            ;;
        macOS)
            echo "  brew install <package>"
            ;;
        Windows)
            echo "  Use Chocolatey (choco install <package>) or Winget (winget install <package>)"
            ;;
        *)
            echo "Unknown os: $OS"
            exit 1
            ;;
    esac
    exit 1
else
    echo -e "\e[34mAll dependencies are installed\e[0m"
    mkdir ~/.cbook/
    cp address.book ~/.cbook/
    echo "A template Adressbook has been created in ~/.cbook/address.book"
    echo -e "Linking to \e[31m/usr/local/bin\e[0m."
    echo "Do you wish to continue with installation? (yes/no)"
    read confirm
    case "$confirm" in
        yes|y)
            bash link.sh
            ;;
        no|n)
            echo "Will not proceed with linking"
            ;;
    esac
    exit 0
fi
