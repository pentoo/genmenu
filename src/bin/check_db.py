#!/usr/bin/python
#
# This code in distributed under GPLv3
# Copyright Anton Bolshakov blshkv@pentoo.ch
#
# Pre-release 0.0001 alpha

import sys,os,re,shutil,subprocess

#from output import red, green, blue, bold
import csv

from lxml import etree
from StringIO import StringIO

db = []

# path to the db.csv file
BASEDIR="../share/genmenu/"
# path to the pentoo portage
PENTOODIR="/pentoo/portage/trunk/pentoo/"

star = "  *  "
arrow = " >>> "
warn = " !!! "

def readcsv():
    '''Reads the db from the csv file'''
    try:
        reader = csv.reader(open(BASEDIR + "db.csv", "rb"))
    except:
        return -1
    for row in reader:
        db.append(row)

def appendcsv():
    '''Appends a line in the csv file'''
    '''Structure is as follow : cat-portage/appname,cat-pentoo,bin1[ bin2]'''
    writer = csv.writer
    #reader = csv.reader(open(BASEDIR + "db.csv", "rb"))
    #for row in reader:
    #    DB.append(row)

def listdb():
    print "*****************************************"
    print "    Listing all supported packages "
    print "*****************************************"
    print "Package\t\tMenu category"
    for y in range(db.__len__()):
        if db[y][0].__len__() < 15:
            tab="\t\t"
        else:
            tab="\t"
        print db[y][0] + tab + db[y][1]

def readebuild(path):
    '''Reads and parces ebuild file'''
    pkg = []
    try:
        ebuild = open(path, "rb")
    except:
        return -1
    for row in ebuild:
        if row.startswith("#"):
            continue
        matchObj = re.match( r'.*\s(.*/[\w-]*)', row)
        if matchObj:
            pkg.append(matchObj.group(1))

    return pkg


def listpackages(pkgdir):
    """List packages in the pentoo ebuilds (pentoo-*.ebuild)"""

packages = []
categories = [ "analyzer", "bluetooth", "cracking", "database", "exploit",
               "footprint", "forensics", "forging", "fuzzers", "mitm", "mobile", "proxies",
               "radio", "rce", "scanner", "voip", "wireless" ]

for category in categories:
    catdir=PENTOODIR+"pentoo-"+category+"/"
    catfiles = os.listdir(catdir)

    for catfile in catfiles:
	if catfile.endswith(".ebuild"):
	    packages = readebuild(catdir+catfile)

#    packages.sort()
    for package in packages:
      	if package.startswith("#"):
	    continue
      	matchObj = re.match( r'.*/(.*)', package)
	if matchObj:
	    print package + "," + category + "," + matchObj.group(1)


def find_option(submenu, tag):
    for x in submenu.iterchildren():
        if x.tag == tag:
            return x
        else:
            tmp = find_option(x, tag)
            if not tmp == None:
                return tmp

def find_menu_entry(menu, submenu, option=None):
    try:
        for x in menu.iterchildren():
            if x.text == submenu:
                if not option == None:
                    return find_option(x.getparent(), option)
                else:
                    return x.getparent() 
            else:
                tmp = find_menu_entry(x, submenu, option)
                if not tmp == None:
                    return tmp
    except:
        return menu

def main():
    '''
    This program is used to generate list of installed packages from Pentoo ebuild
    '''
#    try:
#       readcsv()
#    except:
#        print >> sys.stderr, "cannot read csv file"
#        return -1

#    listdb()
    listpackages(PENTOODIR)
    return 0

    print star + "Listing supported packages installed"
    print "Package\t\tIcon file\t\tMenu category"

    pkginstalled = []
    pkginstalled = listpackages(PENTOODIR)
    notthere = []
    genname=""
    params=""

    for y in range(db.__len__()):
        if pkginstalled.__contains__(db[y][0]):
            if 1 == 1:
                print db[y][0] + "\t" + db[y][2] + "\t\t" + db[y][1] + "\t"
            else:
                # calls makemenuentry file.eap, menu category
                try:
                    if db[y].__len__() == 4:
                        params = db[y][3]
                    elif db[y].__len__() == 5:
                        params = db[y][3]
                        genname = db[y][4]
                    else:
                        params = "-h"
                        genname = ""
                except:
                    print >> sys.stderr, "!!! Unable to generate entry for " + db[y][0] + "please report this to grimmlin@pentoo.ch"
                    pass
        else:
            notthere.append(db[y][0])

    # Final move, show the unfound icons in the db
    print warn + "Missing applications :"
    print star + "The following applications are available but not installed"
    for i in range(notthere.__len__()):
        print arrow + notthere[i]

    sys.exit()


if __name__ == "__main__":

    try:
        main()
    except KeyboardInterrupt:
        # If interrupted, exit nicely
        print >> sys.stderr, 'Interrupted.'

