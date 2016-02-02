#!/usr/bin/env python
#
# proxy-tray - A simple appindicator script for opening a SOCKS5 proxy via
#              SSH and settings the system proxy settings to use it

# Copyright 2015 Joel Best
#
# Based on sample Python code by Neil Jagdish Patel and Jono Bacon here:
# https://wiki.ubuntu.com/DesktopExperienceTeam/ApplicationIndicators
#
# This program is free software: you can redistribute it and/or modify it 
# under the terms of either or both of the following licenses:
#
# 1) the GNU Lesser General Public License version 3, as published by the 
# Free Software Foundation; and/or
# 2) the GNU Lesser General Public License version 2.1, as published by 
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the applicable version of the GNU Lesser General Public 
# License for more details.
#
# You should have received a copy of both the GNU Lesser General Public 
# License version 3 and version 2.1 along with this program.  If not, see 
# <http://www.gnu.org/licenses/>
#

import gobject
import gtk
import appindicator
import os
import sys
import subprocess
import time
import atexit

# File used as SSH master controller
control_master = '/tmp/proxytray-ssh-ctrl'
ssh_process = None


# Set user@hostname here or in $HOME/.proxytrayrc as a single line
user_at_host = ''

# If not specified in source, try and read from ~/.proxytrayrc
if user_at_host == '':
  config_file = os.path.expanduser("~/.proxytrayrc")
  if os.path.exists(config_file):
    with open(os.path.expanduser("~/.proxytrayrc"), 'r') as f:
      user_at_host = f.readline().rstrip()
  else:
    print "Error: proxy host must be specified in source or ~/.proxytrayrc"
    exit(1)



def enable_response(w, buf):
    global ssh_process

    if ind.get_status() == appindicator.STATUS_ACTIVE:

	# Open SSH master connection with a control socket in /tmp
        ssh_process = subprocess.Popen(['ssh', '-oPasswordAuthentication=no', '-oBatchMode=yes', '-D', '8080', '-M', '-S', control_master, '-f', '-C', '-q', '-N', user_at_host])

	time.sleep(2) # Time to connect

	if os.path.exists(control_master):
          
          # Set the system proxy to localhost:8080
          subprocess.call(['gsettings', 'set', 'org.gnome.system.proxy', 'mode', 'manual'])
          subprocess.call(['gsettings', 'set', 'org.gnome.system.proxy.socks', 'host', 'localhost'])
          subprocess.call(['gsettings', 'set', 'org.gnome.system.proxy.socks', 'port', '8080'])

          # Change icon and toggle the menu to disable
          ind.set_status(appindicator.STATUS_ATTENTION)
          enable_menu_item.get_child().set_label("Disable SSH Proxy")
        else:
          message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
          message.set_markup("Failed to start SSH connection! Make sure the command \"ssh %s\" works!" % user_at_host)
          message.run()
	  message.destroy()
          print "Failed to start SSH connection! Make sure the command \"ssh %s\" works!" % user_at_host
          #exit(1)
    else:
        subprocess.call(['ssh', '-S', control_master, '-O', 'exit', user_at_host])

        # Unset the system proxy
        subprocess.call(['gsettings', 'set', 'org.gnome.system.proxy', 'mode', 'none'])

        ind.set_status(appindicator.STATUS_ACTIVE)
        enable_menu_item.get_child().set_label("Enable SSH Proxy")

def exit_response(w, buf):
  exit()

def cleanup():
  global ssh_process

  if ssh_process is not None:

    # Revert proxy settings
    subprocess.call(['gsettings', 'set', 'org.gnome.system.proxy', 'mode', 'none'])

    if os.path.exists(control_master):
      # Ask SSH to exit (nicely)
      subprocess.call(['ssh', '-S', control_master, '-O', 'exit', user_at_host])

    # Just to be sure
    ssh_process.kill()


if __name__ == "__main__":
  path = os.path.abspath(os.path.dirname(sys.argv[0]))
  ind = appindicator.Indicator ("proxy-tray",
                                path+"/proxy.png",
                                appindicator.CATEGORY_APPLICATION_STATUS)
  ind.set_status (appindicator.STATUS_ACTIVE)
  ind.set_attention_icon (path+"/proxy-active.png")

  # disable proxies to start
  subprocess.call(['gsettings', 'set', 'org.gnome.system.proxy', 'mode', 'none'])

  # create a menu
  menu = gtk.Menu()

  # create some menu items
  enable_label = "Enable SSH Proxy"
  enable_menu_item = gtk.MenuItem(enable_label)
  exit_label = "Exit"
  exit_menu_item = gtk.MenuItem(exit_label)

  # Add items toi menu
  menu.append(enable_menu_item)
  menu.append(exit_menu_item)

  # connect menu items up with response functions
  enable_menu_item.connect("activate", enable_response, enable_label) 
  exit_menu_item.connect("activate", exit_response, exit_label)

  # show the items
  enable_menu_item.show()
  exit_menu_item.show()

  ind.set_menu(menu)
  
  atexit.register(cleanup)

  gtk.main()
