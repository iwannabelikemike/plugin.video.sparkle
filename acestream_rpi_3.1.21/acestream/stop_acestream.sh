#!/bin/sh
PATH=/sbin:/usr/sbin:/bin:/usr/bin
ACEADDON="`dirname \"$0\"`"
ACECHROOT="androidfs"
 
if ! [ $(id -u) = 0 ]; then
        PERMISSION=sudo
fi

#terminar acestream.sh
$PERMISSION pkill -9 -f "/system/data/data/org.acestream.engine/files/python/bin/python" &>/dev/null
#terminar chroot
$PERMISSION pkill -9 -f "/system/bin/acestream.sh" &>/dev/null
#desmontar
$PERMISSION umount $ACEADDON/$ACECHROOT/proc
$PERMISSION umount $ACEADDON/$ACECHROOT/sys
$PERMISSION umount $ACEADDON/$ACECHROOT/dev
