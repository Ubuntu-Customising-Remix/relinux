'''
Setup Dependencies
@author: Joel Leclerc (MiJyn) <lkjoel@ubuntu.com>
'''

from relinux import logger, aptutil, configutils, threadmanager, config, fsutil
import os
import copy
import threading

configs = config.Configuration["OSWeaver"]

# Fix installer dependencies
instdepends = {"deps": [], "tn": "Setup", "threadspan":-1}
class setupInst(threadmanager.Thread):
    def __init__(self, **kw):
        threadmanager.Thread.__init__(self, **kw)
        self.aptcache = copy.copy(config.AptCache)

    def finishfunc(self, event):
        self.quit()

    def getPkg(self, pkgname):
        return aptutil.getPkg(pkgname, self.aptcache)

    def instPkg(self, pkgname, relinuxdep = False):
        p = self.getPkg(pkgname)
        if not p.is_installed and relinuxdep:
            if not pkgname in configs[configutils.remafterinst][configutils.value]:
                configs[configutils.remafterinst][configutils.value].append(pkgname)
        aptutil.instPkg(p, True)

    def remPkg(self, pkgname, purge = True):
        p = self.getPkg(pkgname)
        aptutil.remPkg(p, purge)

    def runthread(self):
        self.event = threading.Event()
        self.ap = aptutil.AcquireProgress()
        self.ip = aptutil.InstallProgress(lambda: self.finishfunc(self.event))
        logger.logI(self.tn, logger.I, _("Setting up distro dependencies"))
        logger.logV(self.tn, logger.I, _("Setting up Ubiquity"))
        self.instPkg("ubiquity", True)
        if configutils.getValue(configs[configutils.instfront]).lower() == "kde":
            self.instPkg("ubiquity-frontend-kde", True)
            self.remPkg("ubiquity-frontend-gtk")
        else:
            self.instPkg("ubiquity-frontend-gtk", True)
            self.remPkg("ubiquity-frontend-kde")
            g = self.getPkg("ubiquity-frontend-kde")
            print("MI" + str(g.marked_install) + "MRE" + str(g.marked_reinstall) + "MU" + str(g.marked_upgrade))
        logger.logV(self.tn, logger.I, _("Setting up Popularity Contest"))
        if configutils.getValue(configs[configutils.popcon]):
            self.instPkg("popularity-contest")
        else:
            self.remPkg("popularity-contest")
        if configutils.getValue(configs[configutils.memtest]):
            logger.logV(self.tn, logger.I, _("Setting up memtest86+"))
            self.instPkg("memtest86+")
        logger.logV(self.tn, logger.I, _("Setting up other distro dependencies"))
        self.instPkg("ubuntu-minimal")
        self.instPkg("syslinux", True)
        self.instPkg("discover")
        self.instPkg("coreutils")
        self.instPkg("bash")
        self.instPkg("initramfs-tools")
        logger.logI(self.tn, logger.I, _("Setting up relinux generation dependencies"))
        self.instPkg("squashfs-tools", True)
        self.instPkg("genisoimage", True)
        configutils.saveBuffer(config.Configuration)    
        aptutil.commitChanges(self.aptcache, self.ap, self.ip)
        self.exec_()
instdepends["thread"] = setupInst


threads = [instdepends]
