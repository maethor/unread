#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
 
from __future__ import (unicode_literals, absolute_import, 
                        division, print_function)

import imaplib, json, pynotify, getopt, sys, os

from config import *

#default imap port is 993, change otherwise
try:
    M=imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    M.login(IMAP_USER, IMAP_PASSWORD)
except:
    print("Cannot log in")
    sys.exit(1)

totalunread = 0
totalnew = 0
boxes = dict()

def usage():
    print ("Usage: unread [OPTION]")
    print ("")
    print ("-h, --help      Display this help")
    print ("-n, --new       Display new messages since the last check (default)")
    print ("-u, --unread    Display unread messages")
    print ("-t, --total     Only print the total")
    print ("-f, --force     Display even if there is no message")


try:
    opts, args = getopt.getopt(sys.argv[1:], "hnutf", ["help", "new", "unread", "total", "force"])
except getopt.GetoptError as err:
    # print help information and exit:
    print(str(err)) # will print something like "option -a not recognized"
    usage()
    sys.exit(2)
display_new = True
display_unread = False
display_total = False
display_force = False
for o, a in opts:
    if o in ("-h", "--help"):
        usage()
        sys.exit()
    elif o in ("-u", "--unread"):
        display_unread = True
        display_new = False
    elif o in ("-n", "--new"):
        display_new = True
    elif o in ("-t", "--total"):
        display_total = True
    elif o in ("-f", "--force"):
        display_force = True
    else:
        assert False, "unhandled option"


try:
    with open("/tmp/mailcounts", "r") as f:
        boxes = json.loads(f.read())
except:
    pass

for inbox in IMAP_MAILBOXES:
    status, counts = M.status(inbox,"(MESSAGES UNSEEN)")
    if status == "OK":
        unread = int(counts[0].split()[4][:-1])
        if (inbox in boxes):
            ex_unread = boxes[inbox]["unread"]
        else:
            boxes[inbox] = dict()
            ex_unread = 0
        new = unread - ex_unread
        new = (new if new > 0 else 0)
        boxes[inbox]["new"] = new
        boxes[inbox]["unread"] = unread
        totalnew += new
        totalunread += unread
    else:
        if (inbox not in boxes):
            boxes[inbox] = dict()
        boxes[inbox]["new"] = "?"
        boxes[inbox]["unread"] = "?"

M.logout()

try:
    with open("/tmp/mailcounts", "w") as f:
        f.write(json.dumps(boxes))
except:
    pass

if display_new and (totalnew > 0 or display_force):
    string = ""
    for key, values in boxes.iteritems():
        if (values["new"] > 0 and values["new"] != "?") or display_force:
            string += "\n- %s : %s" % (key, values["new"])

    pynotify.init ("Mailcount")
    n=pynotify.Notification ("%d nouveaux emails" % totalnew, string, os.path.dirname(os.path.realpath(__file__)) + "/icons/mail-message.png")
    n.set_timeout(5000)
    n.show ()

if display_unread and (totalunread > 0 or display_force):
    string = ""
    for key, values in boxes.iteritems():
        if (values["unread"] > 0 and values["new"] != "?") or display_force:
            string += "\n- %s : %s" % (key, values["unread"])

    pynotify.init ("Mailcount")
    n=pynotify.Notification ("%d emails non-lus" % totalunread, string, os.path.dirname(os.path.realpath(__file__)) + "/icons/mail-message.png")
    n.set_timeout(5000)
    n.show ()

if display_total:
    if display_unread:
        print(totalunread)
    else:
        print(totalnew)
