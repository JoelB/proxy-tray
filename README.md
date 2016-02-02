# Proxy Tray

##### An indicator applet to quickly switch to an SSH SOCKS proxy

This script provides a tray icon to quickly open a SOCKS proxy with SSH through a 
specific host and set the system-wide proxy settings to use it. This is useful if
you use an SSH jump host and sometime need to quickly proxy through (e.g. to access 
internal intranet resources). This applet will only affect connections from applications
that use the GNOME system proxy settings.

## Usage

Create the file $HOME/.proxytrayrc with a single line containing the user and host
```
  $ cat ~/.proxytrayrc
  username@example.com
```
  
Alternatively, you can set the user_at_host value directly in proxy-tray.py

**NOTE**: You must be set up for public-key authentication without being
          prompted for a password (agent-based keys work).
          
          
## Credits and Licensing

The applet itself is based on the Python tutorial here:
https://wiki.ubuntu.com/DesktopExperienceTeam/ApplicationIndicators

The project is licensed under the GNU General Public Licenses version 3. Please see the
LICENSE file for more details
