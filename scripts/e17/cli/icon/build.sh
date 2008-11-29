#!/bin/sh

# a .eap file is just a .edj file with added meta data for application launch
# info. enlightenment_eapp can add/modify/delete this metadata. the script
# below is an example of building an eap icon from scratch.

# actually compile a edje file with all the gfx etc.
edje_cc $@ -id . -fd . icon.edc icon.eap

# add eapp properties to the file - they are ALL optional EXCEPT name and exe
# and exe is optional for directory .eapp files
enlightenment_eapp \
icon.eap \
-set-name "Application Name" \
-set-generic "Generic name" \
-set-comment "Comment on what this application does" \
-set-exe "execute_line" \
-set-win-name "window_name" \
-set-win-class "window_class" \
-set-icon-class "icon,class"

# other options u might want to use:
# -lang LANG
# -set-startup-notify 1/0 \
# -set-win-title "window_title*glob" \
# -set-win-role "window_role" \
# -set-wait-exit 1/0 \
#
# see enlightenment_eapp -h for more -set options
