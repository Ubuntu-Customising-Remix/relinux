'''
Various APT Utilities
@author: MiJyn
'''

import apt


# Version Comparison Operations
lt = 0x00
le = 0x01
eq = 0x02
ge = 0x03
gt = 0x04


# Initializes APT
def initApt():
    apt.apt_pkg.init()


# Returns an APT cache
# Note that this can take around 2-30 seconds
def getCache():
    return apt.apt_pkg.Cache()


# Returns an APT DepCache
# Used for package managing
def getDepCache(cache):
    return apt.apt_pkg.DepCache(cache)


# Returns a package in an APT cache
def getPkg(pkg, cache):
    return cache[pkg]


# Returns the package version
def getPkgVersion(pkg):
    return pkg.installed.version


# Returns an AcquireProgress
def getAcquireProgress():
    return apt.progress.base.AcquireProgress()


# Returns an InstallProgress
def getInstallProgress():
    return apt.progress.base.InstallProgress()


# Compares versions
def compVersions(v1, v2, operation):
    comp = apt.VersionCompare(v1, v2)
    if operation == lt:
        if comp < 0:
            return True
        else:
            return False
    elif operation == le:
        if comp <= 0:
            return True
        else:
            return False
    elif operation == eq:
        if comp == 0:
            return True
        else:
            return False
    elif operation == ge:
        if comp >= 0:
            return True
        else:
            return False
    elif operation == gt:
        if comp > 0:
            return True
        else:
            return False


# Helper function for checking if a package is installed within a depcache
def _depCacheInstalled(package, depcache):
    if (depcache.is_auto_installed(package) or depcache.is_garbage(package) or
        depcache.is_inst_broken(package) or depcache.is_now_broken(package) or
        depcache.is_upgradeable(package)):
        return True
    else:
        return False


# Installs a package
def instPkg(package, depcache, reinstall = True):
    if _depCacheInstalled(package, depcache):
        if reinstall:
            depcache.set_reinstall(package)
            return True
        else:
            return False
    else:
        depcache.mark_install(package, True, True)
        return True


# Removes a package
def remPkg(package, depcache, purge = True):
    if _depCacheInstalled(package, depcache):
        depcache.mark_delete(package, purge)
        return True
    else:
        return False


# Commits the changes
def commitChanges(depcache, ap, ip):
    if depcache.inst_count > 0 or depcache.del_count > 0:
        depcache.commit(ap, ip)
        return True
    else:
        return False
