import types
import sys
import logging
import io
import zipfile
import tarfile
import os
try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen

log_level = logging.DEBUG
log_format = '%(message)s'

logger = logging.getLogger(__name__)
logger.setLevel(log_level)
log_handler = logging.StreamHandler()
log_handler.setLevel(log_level)
log_formatter = logging.Formatter(log_format)
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)

RELOAD = False
import importlib



class HttpImporter(object):

    TAR_ARCHIVE = 'tar'
    ZIP_ARCHIVE = 'zip'
    WEB_ARCHIVE = 'html'
    ARCHIVE_TYPES = [
        ZIP_ARCHIVE,
        TAR_ARCHIVE,
        WEB_ARCHIVE
    ]

    def __init__(self, modules, base_url, zip_pwd=None):

        self.module_names = modules
        self.base_url = base_url + '/'
        self.in_progress = {}
        self.__zip_pwd = zip_pwd

        try:
            self.filetype, self.archive = self._detect_filetype(base_url)
            logger.info("[+] Filetype detected '%s' for '%s'" % (self.filetype, self.base_url))
        except IOError:
            raise ImportError("URL content cannot be detected or opened (%s)" % self.base_url)

        self.is_archive = False
        if self.filetype in [HttpImporter.TAR_ARCHIVE, HttpImporter.ZIP_ARCHIVE]:
            self.is_archive = True

        if self.is_archive:
            logger.info("[+] Archive file loaded successfully from '%s'!" % self.base_url)
            self._paths = self._list_archive(self.archive)


    def _mod_to_file_paths(self, fullname, compiled=False):
        suffix = '.pyc' if compiled else '.py'
        # get the python module name
        py_filename = fullname.replace(".", os.sep) + suffix
        # get the filename if it is a package/subpackage
        py_package = fullname.replace(".", os.sep, fullname.count(".") - 1) + "/__init__" + suffix

        if self.is_archive:
            return {'module': py_filename, 'package': py_package}
        else:
            # if self.in_progress:
            # py_package = fullname.replace(".", '/') + "/__init__" + suffix
            return {
            'module': self.base_url + py_filename,
            'package': self.base_url + py_package
            }

    def _mod_in_archive(self, fullname, compiled=False):
        paths = self._mod_to_file_paths(fullname, compiled=compiled)
        return set(self._paths) & set(paths.values())

    def find_module(self, fullname, path=None):
        logger.debug("FINDER=================")
        logger.debug("[!] Searching %s" % fullname)
        logger.debug("[!] Path is %s" % path)
        logger.info("[@] Checking if in declared remote module names >")
        if fullname.split('.')[0] not in self.module_names:
            logger.info("[-] Not found!")
            return None

        if fullname in self.in_progress:
            return None

        self.in_progress[fullname] = True

        logger.info("[@] Checking if built-in >")
        try:
            try:    # After Python3.5
                loader = importlib.util.find_spec(fullname, path)  # noqa
            except AttributeError:
                loader = importlib.find_loader(fullname, path)  # noqa
            if loader:
                logger.info("[-] Found locally!")
                return None
        except ImportError:
            pass
        logger.info("[@] Checking if it is name repetition >")
        if fullname.split('.').count(fullname.split('.')[-1]) > 1:
            logger.info("[-] Found locally!")
            return None

        if self.is_archive:
            logger.info("[@] Checking if module exists in loaded Archive file >")
            if self._mod_in_archive(fullname) is None:
                logger.info("[-] Not Found in Archive file!")
                return None

        logger.info("[*] Module/Package '%s' can be loaded!" % fullname)
        del(self.in_progress[fullname])
        return self

    def load_module(self, name):
        logger.debug("LOADER=================")
        logger.debug("[+] Loading %s" % name)
        if name in sys.modules and not RELOAD:
            logger.info('[+] Module "%s" already loaded!' % name)
            return sys.modules[name]

        if name.split('.')[-1] in sys.modules and not RELOAD:
            logger.info('[+] Module "%s" loaded as a top level module!' % name)
            return sys.modules[name.split('.')[-1]]

        try:
            mod_dict = self._open_module_src(name)
            module_src = mod_dict['source']
            filepath = mod_dict['path']
            module_type = mod_dict['type']

        except ValueError:
            logger.info("[-] '%s' is not a module:" % name)
            logger.warning("[!] '%s' not found in HTTP repository. Moving to next Finder." % name)
            return None

        logger.debug("[+] Importing '%s'" % name)

        mod = types.ModuleType(name)

        mod.__loader__ = self
        mod.__file__ = filepath
        if module_type == 'package':
            mod.__package__ = name
        else:
            mod.__package__ = name.split('.')[0]

        try:
            mod.__path__ = ['/'.join(mod.__file__.split('/')[:-1]) + '/']
        except:  # noqa
            mod.__path__ = self.base_url
        logger.debug("[+] Ready to execute '%s' code" % name)
        sys.modules[name] = mod
        exec(module_src, mod.__dict__)
        logger.info("[+] '%s' imported successfully!" % name)
        return mod

    def _open_module_src(self, fullname, compiled=False):

        paths = self._mod_to_file_paths(fullname, compiled=compiled)
        mod_type = 'module'
        if self.is_archive:
            try:
                correct_filepath_set = set(self._paths) & set(paths.values())
                filepath = correct_filepath_set.pop()
            except KeyError:
                raise ImportError("Module '%s' not found in archive" % fullname)

            content = self._open_archive_file(self.archive, filepath, 'r', zip_pwd=self.__zip_pwd).read()
            src = content
            logger.info('[+] Source from archived file "%s" loaded!' % filepath)
        else:
            content = None
            filepath = None
            for mod_type in paths.keys():
                filepath = paths[mod_type]
                try:
                    logger.debug("[*] Trying '%s' for module/package %s" % (filepath,fullname))
                    content = urlopen(filepath).read()
                    break
                except IOError:
                    logger.info("[-] '%s' is not a %s" % (fullname,mod_type))

            if content is None:
                raise ValueError("Module '%s' not found in URL '%s'" % (fullname,self.base_url))

            src = content
            logger.info("[+] Source loaded from URL '%s'!'" % filepath)

        return {
            'source': src,
            'path': filepath,
            'type': mod_type
        }

    @staticmethod
    def _detect_filetype(base_url):
        # request base url
        resp_obj = urlopen(base_url)
        resp = resp_obj.read()
        resp_io = io.BytesIO(resp)
        content_type = resp_obj.headers['Content-Type']

        # check content type of html
        if "text" in content_type:
            logger.info(
                "[+] Response of '%s' is HTML. - Content-Type: %s" % (base_url, resp_obj.headers['Content-Type']))
            return HttpImporter.WEB_ARCHIVE, resp
        elif "zip" in content_type:
            zip_file = zipfile.ZipFile(resp_io)
            logger.info("[+] Response of '%s' is a ZIP file" % base_url)
            return HttpImporter.ZIP_ARCHIVE, zip_file
        elif 'tar' in content_type:
            tar = tarfile.open(fileobj=resp_io, mode='r:*')
            logger.info("[+] Response of '%s' is a Tarball" % base_url)
            return HttpImporter.TAR_ARCHIVE, tar
        else:
            raise IOError("Content of URL '%s' is Invalid" % base_url)

    @staticmethod
    def _open_archive_file(archive_obj, filepath, mode='r', zip_pwd=None):
        if isinstance(archive_obj, tarfile.TarFile):
            return archive_obj.extractfile(filepath)
        if isinstance(archive_obj, zipfile.ZipFile):
            return archive_obj.open(filepath, mode, pwd=zip_pwd)

        raise ValueError("Object is not a ZIP or TAR archive")

    @staticmethod
    def _list_archive(archive_obj):
        if isinstance(archive_obj, tarfile.TarFile):
            return archive_obj.getnames()
        if isinstance(archive_obj, zipfile.ZipFile):
            return [x.filename for x in archive_obj.filelist]

        raise ValueError("Object is not a ZIP or TAR archive")


def remote_repo(modules, base_url='http://localhost:8000/', zip_pwd=None):
    importer = HttpImporter(modules, base_url, zip_pwd=zip_pwd)
    sys.meta_path.insert(0, importer)  # noqa


__all__ = [
    'HttpImporter',
    'remote_repo',
]
