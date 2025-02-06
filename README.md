# FCPS

This tool allows the user to spray credentials to test for ForceChangePassword rights over other users in the Username list.
First, gather a username list by using enum4linux, impacket-GetADUsers, etc.

For some CTF machines, Bloodhound doesn't show ForceChangePassword rights over other users. In those cases, you try each user in a special group manually.

In this blog by Juggarnaut-sec, the methodology is explained further "our current user “vcreed” is a member of that group. Very often, when we find an “IT support” type of custom group (or user) with Help Desk, Service Desk, Support, IT, etc. in their name, there’s a pretty good chance that the group / user will have delegate privileges that allow them to force a password reset" https://juggernaut-sec.com/ad-recon-msrpc-over-smb/#Manually_Enumerating_Users_Groups_and_More_%E2%80%93_rpcclient

```
Usage: FCPS.py [-h] -d DOMAIN -u CONTROLLED_USER -p CONTROLLED_USER_PASSWORD -i DOMAIN_CONTROLLER_IP -f
               USERNAME_LIST -n NEW_PASSWORD

Automate password changes via rpcclient

options:
  -h, --help            show this help message and exit
  -d DOMAIN, --domain DOMAIN
                        Target domain name (e.g., example.com)
  -u CONTROLLED_USER, --controlled_user CONTROLLED_USER
                        User with permission to change passwords
  -p CONTROLLED_USER_PASSWORD, --controlled_user_password CONTROLLED_USER_PASSWORD
                        Password for the controlled user
  -i DOMAIN_CONTROLLER_IP, --domain_controller_ip DOMAIN_CONTROLLER_IP
                        Domain Controller IP address
  -f USERNAME_LIST, --username_list USERNAME_LIST
                        Path to file containing usernames
  -n NEW_PASSWORD, --new_password NEW_PASSWORD
                        New password to set for users
```


![image](https://github.com/user-attachments/assets/3ba16968-4338-439b-a6d0-f4b44025b54b)


