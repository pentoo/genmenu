#!/usr/bin/python
#
# This code in distributed under GPLv2
# Copyright Michael Zanetta grimmlin@pentoo.ch
#
# WARNING !!! UGLY CODE AHEAD !!!
#

import sys,os,re,shutil

#from output import red, green, blue, bold
import csv

from lxml import etree
from StringIO import StringIO

db = []

PORTDIR="/var/db/pkg/"
BASEDIR = '/usr/share/genmenu/'
APPSDIR = '/usr/share/genmenu/desktop'
MENUDIR = '/usr/share/genmenu/directory'
ENVDIR = '/etc/env.d/'

star = "  *  "
arrow = " >>> "
warn = " !!! "

class directoryfile:

    Header = "[Desktop Entry]"
    Name = "Name="
    Comment = "Comment="
    Icon = "Icon=/usr/share/genmenu/pixmaps/"
    Type = "Type=Directory"

    def setName(self, Name):
        self.Name += Name

    def setComment(self, Comment):
        self.Comment += Comment

    def setIcon(self, Icon):
        self.Icon += Icon

    def getDirectoryFile(self):
        return self.Header, self.Name, self.Comment, self.Icon, self.Type

    def writeDirectoryFile(self, dest):
        try:
            file = open(dest , "w")
        except:
            sys.stderr.write("Unable to open " + dest + " for writing\n")
            sys.stderr.write("Verify that you have write permissions")
            return -1
        for x in self.Header, self.Name, self.Comment, self.Icon, self.Type:
            file.write(x + "\n")
        file.close()

class desktopfile:

    Header = "[Desktop Entry]"
    Name = "Name="
    GenName = "GenericName="
    Exec = "Exec="
    Icon = "Icon=/usr/share/genmenu/pixmaps/"
    Type = "Type=Application"

    def setName(self, Name):
        self.Name += Name

    def setGenName(self, GenName):
        self.GenName += GenName

    def setIcon(self, Icon):
        self.Icon += Icon

    def setExec(self, Exec):
        self.Exec += Exec

    def getDesktopFile(self):
        return self.Header, self.Name, self.GenName, self.Exec, self.Icon, self.Type

    def writeDesktopFile(self, dest):
        try:
            file = open(dest , "w")
        except:
            sys.stderr.write("Unable to open " + dest + " for writing\n")
            sys.stderr.write("Verify that you have write permissions")
            return -1
        for x in self.Header, self.Name, self.GenName, self.Exec, self.Icon, self.Type:
            file.write(x + "\n")
        file.close()


def getHomeDir():
    ''' Try to find user's home directory, otherwise return /root.'''
    try:
        path1=os.path.expanduser("~")
    except:
        path1=""
    try:
        path2=os.environ["HOME"]
    except:
        path2=""
    try:
        path3=os.environ["USERPROFILE"]
    except:
        path3=""

    if not os.path.exists(path1):
        if not os.path.exists(path2):
            if not os.path.exists(path3):
                return '/root'
            else: return path3
        else: return path2
    else: return path1

HOME = getHomeDir()
ICONDIR = HOME + '/.local/share/applications/'
LOCALDIR = HOME + '/.local/share/desktop-directories/'

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

#REM Almost done, need to sanitize tabbed output
def listdb():
    print green("*****************************************")
    print green("    Listing all supported packages ")
    print green("*****************************************")
    print "Package\t\tMenu category"
    for y in range(db.__len__()):
        if db[y][0].__len__() < 15:
            tab="\t\t"
        else:
            tab="\t"
        print db[y][0] + tab + db[y][1]


def listpackages(pkgdir):
    """List packages installed as in the portage database directory (usually /var/db/pkg)"""
    packages = []
    categories = os.listdir(pkgdir)
    for category in categories:
        catdir = os.path.join(pkgdir, category)
        applications = os.listdir(catdir)
        for application in applications:
            packages.append(category + "/" + re.sub("-[0-9].*", "", application, 1))
    packages.sort()
    return packages
 
def settermenv():
    """This function creates the apropriate environment variable for the $E17TERM"""
    file = open(ENVDIR + "99pentoo-term" , "w")
    file.write("P2TERM=\"" + options.p2term + "\"")
    file.newlines
    file.close()

# Adds a desktop entry in the specified category, always under Pentoo.

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

def add_menu_entry(root_menu, root_category, category):
    '''This adds a menu element entry 'category' under the root_category menu'''
    menu = find_menu_entry(root_menu, category)
    if menu == None:
        new_menu_entry = etree.SubElement(root_menu, "Menu")
        new_name_entry = etree.SubElement(new_menu_entry, "Name")
        new_name_entry.text = category
        directory_entry_file = category + ".directory"
        file = os.path.join(LOCALDIR, directory_entry_file)
        if not options.simulate:
            if not os.path.exists(LOCALDIR):
                try:
                    os.makedirs(LOCALDIR)
                except:
                    sys.stderr.write("Unable to create " + LOCALDIR + "\n")
                    sys.stderr.write("Verify that you have write permissions in " + LOCALDIR + "\n")
                    return -1
            try:
                if os.path.exists(os.path.join(MENUDIR, directory_entry_file)):
                    shutil.copyfile(os.path.join(MENUDIR, directory_entry_file), file)
                else:
                    # We try to make it by hand
                    nme = create_menu_entry(category, root_category)
                    directory_entry_file = root_category + "-" + category + ".directory"
                    file = os.path.join(LOCALDIR, directory_entry_file) 
                    nme.writeDirectoryFile(file)
            except:
                sys.stderr.write("Unable to copy " + directory_entry_file + " to " + LOCALDIR + "\n")
                sys.stderr.write("Verify that you have write permissions in " + LOCALDIR + "\n")
                return -1
        new_directory_entry = etree.SubElement(new_menu_entry, "Directory")
        new_directory_entry.text = directory_entry_file
        new_includelist = etree.SubElement(new_menu_entry, "Include")
        return new_menu_entry

def append_desktop_entry(menu, iconfile):
    entrypoint = find_option(menu, "Include")
    new_desktop_entry = etree.SubElement(entrypoint, "Filename")
    new_desktop_entry.text = iconfile

def create_menu_entry(name, category, comments = ""):
    '''This function creates a simple .directory entry'''
    me = directoryfile()
    me.setName(name)
    me.setIcon(category + ".png")
    me.setComment(comments)
    return me

def create_desktop_entry(name, category, binname, params, genname):
    '''This function creates a simple .desktop entry'''
    de = desktopfile()
    de.setName(name.capitalize())
    de.setIcon(category + ".png")
    de.setGenName(genname)
    de.setExec(options.p2term + " -e launch " + binname + " " + params)
    return de

def make_menu_entry(root_menu, iconfiles, category, params, genname):
    root_category = category.split(" ")[0]
    # TODO
    # This adds/search the root category for correct submenus creations
    if not category == 'none':
        for submenus in category.split(" "):
            # Add the same here for the "all" subentry
            if submenus == root_category:
                base_menu = find_menu_entry(root_menu, root_category)
                if base_menu == None:
                    base_menu = add_menu_entry(root_menu, root_category, root_category)
                menu = base_menu
            else:
                if options.vverbose:
                    print submenus
         
                menu = find_menu_entry(base_menu, submenus)
                if menu == None:
                    menu = add_menu_entry(base_menu, root_category, submenus)
                base_menu = menu
    # Only adds the entry under specific category
    for iconfile in iconfiles.split(" "):
        if not os.path.exists(ICONDIR):
            os.makedirs(ICONDIR)
        if not iconfile.endswith(".desktop"):
            # We need to create a new .desktop entry
            nde = create_desktop_entry(iconfile, category.split(" ")[0], iconfile, params, genname)
            file = os.path.join(ICONDIR, iconfile + ".desktop")
            nde.writeDesktopFile(file)
            iconfile += ".desktop"
        else:
            # We copy the .desktop file to the local desktop dir
            file = os.path.join(APPSDIR, iconfile)
            if os.path.exists(file):
                if options.verbose:
                    print arrow + "Copying " + iconfile + " to " + ICONDIR
                if not options.simulate:
                # Copy the file
                    try:
                        shutil.copyfile(file, ICONDIR + iconfile)
                        os.system("sed -i -e 's/P2TERM/" + options.p2term + "/' " + ICONDIR + iconfile)
                    except:
                        sys.stderr.write("Unable to copy " + iconfile + " to " + ICONDIR + "\n")
                        sys.stderr.write("Verify that you have write permissions in " + ICONDIR + "\n")
                        return -1
            else:
                sys.stderr.write("File " + file + "does not exists \n")
                return -1
        if not category == 'none':
            append_desktop_entry(menu, iconfile)
        if options.vverbose:
            print etree.tostring(root_menu, pretty_print=True)
            print iconfile + " " + category


def genxml(root_menu, configdir):
    '''Generate the applications.menu XMl file in the user's directory.'''
    dtd = etree.DTD(os.path.join(BASEDIR, "lib", "menu-1.0.dtd"))
    if dtd.validate(root_menu) == 0:
        print dtd.error_log.filter_from_errors()
        return -1
    if options.verbose:
        #menu = etree.parse(root_menu)
        print etree.tostring(root_menu, pretty_print=True)
    if not options.simulate:
        if not os.path.exists(configdir):
            os.makedirs(configdir)
        root_menu.write(configdir + '/applications.menu')

def main():
    '''
    This program is used to generate the menu in enlightenment for the pentoo livecd
    '''
    try:
        readcsv()
    except:
        print >> sys.stderr, "cannot read csv file"
        return -1

    if options.testmodule:
        a = desktopfile()
        a.setName("Toto")
        a.setExec("toto")
        a.setIcon("toto.png")
        a.writeDesktopFile("./toto.desktop")
        return 0
    
    if options.listsupported:
        listdb()
        return 0

    if options.simulate:
        print star + "Starting simulation"

    if options.listonly:
        print star + "Listing supported packages installed"
        print "Package\t\tIcon file\t\tMenu category"

    if options.extramenu:
        menu = etree.parse(os.path.join(BASEDIR, "lib", "pentoo.menu"))
    else:
        menu = etree.parse(os.path.join(BASEDIR, "lib", "applications.menu"))

    pkginstalled = []
    pkginstalled = listpackages(PORTDIR)
    notthere = []
    below = "Pentoo"
    root_menu = find_menu_entry(menu.getroot(),below)
    
    for y in range(db.__len__()):
        if pkginstalled.__contains__(db[y][0]):
            if options.listonly:
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
                    make_menu_entry(root_menu, db[y][2], db[y][1], params, genname)
                except:
                    print >> sys.stderr, "Something went wrong, obviously..."
                    return -1
        else:
            notthere.append(db[y][0])

    #    settermenv()
    if options.vverbose:
        # Final move, show the unfound icons in the db
        print warn + "Missing applications :"
        print star + "The following applications are available but not installed"
        for i in range(notthere.__len__()):
            print arrow + notthere[i]
    #print etree.tostring(root_menu, pretty_print=True)
    if not options.simulate:

        if options.extramenu:
            genxml(menu, HOME + '/.e/e/extra_menu/')
        else:
            genxml(menu, HOME + '/.config/menus/')

if __name__ == "__main__":

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-l", "--list", action="store_true", dest="listonly", default=False,
                      help="Show supported installed packages")
    parser.add_option("-T", "--test", action="store_true", dest="testmodule", default=False,
                      help="Testing module during dev")
    parser.add_option("-a", "--add", action="store_true", dest="addcsventry", default=False,
                      help="Test xml")
    parser.add_option("-e", "--extramenu", action="store_true", dest="extramenu", default=False,
                      help="Put the pentoo menu at top")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
                      help="Show what's going on")
    parser.add_option("-V", "--very-verbose", action="store_true", dest="vverbose", default=False,
                      help="Show supported installed packages")
    parser.add_option("-L", "--list-supported", action="store_true", dest="listsupported", default=False,
                      help="Show supported installed packages")
    parser.add_option("-t", "--term", dest="p2term", default="xterm",
                      help="Sets the terminal used for cli-only tools")
    parser.add_option("-n", "--dry-run", action="store_true", dest="simulate", default=False,
                      help="Simulate only, show missing desktop files"
                           " and show what will be done")
    (options, args) = parser.parse_args()

    try:
        main()
    except KeyboardInterrupt:
        # If interrupted, exit nicely
        print >> sys.stderr, 'Interrupted.'
