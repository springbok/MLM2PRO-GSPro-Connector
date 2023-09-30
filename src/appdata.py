import os
import shutil
import sys
import time
from contextlib import contextmanager
from functools import lru_cache
from typing import Optional

# For usage see https://appdata.readthedocs.io/en/latest/
# Code: https://github.com/VoIlAlex/appdata

@contextmanager
def _file_based_lock_context(lock):
    try:
        lock.acquire()
        yield lock
    finally:
        lock.release()


class FileBasedLock:
    def __init__(self, app_paths, name=None):
        self.app_paths = app_paths
        self.name = name

    def acquire(self):
        lock_path = self.app_paths.get_lock_file_path(name=self.name)
        while os.path.exists(lock_path):
            time.sleep(1)
        with open(lock_path, 'w+') as f:
            pass

    def release(self):
        lock_path = self.app_paths.get_lock_file_path(name=self.name)
        if os.path.exists(lock_path):
            os.remove(lock_path)

    def context(self):
        return _file_based_lock_context(self)


@lru_cache()
def get_home_folder():
    return os.getcwd() #Path.home().absolute()


@lru_cache()
def prepare_ext(ext: Optional[str]):
    if ext and len(ext) != 0:
        while ext.startswith('..'):
            ext = ext[1:]
        if len(ext) == 1 and ext[0] == '.':
            ext = ''

        if len(ext) != 0:
            if ext[0] != '.':
                ext = '.' + ext
    return ext or ''

class AppDataPaths:
    DEFAULT_EXT = '.ini'
    DEFAULT_LOG_FILE_NAME = 'app'
    DEFAULT_LOCK_FILE_NAME = 'lock'

    def __init__(
            self,
            name=None,
            default_config_ext=None,
            logs_folder_name='logs',
            locks_folder_name='locks',
            home_folder_path=None,
    ):
        """
        :param name: name of the project. Uses cwd name as default.
        """
        self.name = name if name else os.path.split(os.getcwd())[1]
        self.default_config_ext = default_config_ext
        self.home_folder_path = home_folder_path or get_home_folder()
        self.logs_folder_name = logs_folder_name
        self.locks_folder_name = locks_folder_name

        assert self.name
        assert self.home_folder_path

    def get_config_path(self, name=None, ext=None, create=False):
        """
        Allows to get app config path.
        :param name: name of the application. Uses app name as default.
        :return: path to the config.
        """
        ext = ext if ext is not None else self.default_config_ext \
            if self.default_config_ext is not None else self.DEFAULT_EXT

        # Not empty extension should start with . (dot)
        ext = prepare_ext(ext)
        name = name if name is not None else 'default'

        # Full name
        if len(name) == 0:
            if len(ext) != 0:
                full_name = ext
            else:
                full_name = 'config'
        else:
            full_name = name + ext

        path = os.path.join(self.app_data_path, full_name)
        return path

    def get_log_file_path(self, name=None, create=False):
        if name:
            name = name
        elif self.name:
            name = self.name
        else:
            name = self.DEFAULT_LOG_FILE_NAME
        path = os.path.join(self.logs_path, name + '.log')
        return path

    def get_lock_file_path(self, name=None):
        if name:
            name = name
        elif self.name:
            name = self.name
        else:
            name = self.DEFAULT_LOCK_FILE_NAME
        path = os.path.join(self.locks_path, name + '.lock')
        return path

    def check_for_exceptions(self, raise_exceptions=False):
        try:
            if not os.path.exists(self.app_data_path):
                raise RuntimeError('App data folder should exist. Run setup(...) to initialize the required files.')
            if not os.path.exists(self.config_path):
                raise RuntimeError('Config file should exist. Run setup(...) to initialize the required files.')
            if not os.path.exists(self.logs_path):
                raise RuntimeError('Logs folder should exist. Run setup(...) to initialize the required files.')
            if not os.path.exists(self.log_file_path):
                raise RuntimeError('Default log file should exist. Run setup(...) to initialize the required files.')
            if not os.path.exists(self.locks_path):
                raise RuntimeError('Locks folder should exist. Run setup(...) to initialize the required files.')
        except Exception as e:
            if raise_exceptions:
                raise
            return False
        return True

    def setup(self, override=False):
        if override:
            self.clear()
        app_data_path = self.app_data_path
        if not os.path.exists(app_data_path):
            os.makedirs(app_data_path)

        config_path = self.config_path
        if not os.path.exists(config_path):
            with open(config_path, 'w+'):
                pass

        logs_path = self.logs_path
        if not os.path.exists(logs_path):
            os.makedirs(logs_path)

        log_file_path = self.log_file_path
        if not os.path.exists(log_file_path):
            with open(log_file_path, 'w+'):
                pass

        locks_path = self.locks_path
        if not os.path.exists(locks_path):
            os.makedirs(locks_path)

    def clear(self, everything=False):
        if everything:
            app_data_path = self.app_data_path
            if os.path.exists(app_data_path):
                shutil.rmtree(app_data_path)
        else:
            # Here all the config files should
            # be deleted by one
            config_path = self.config_path
            if os.path.exists(config_path):
                os.remove(self.config_path)

            logs_path = self.logs_path
            if os.path.exists(logs_path):
                shutil.rmtree(logs_path)

            locks_path = self.locks_path
            if os.path.exists(locks_path):
                if not os.path.isdir(locks_path):
                    os.remove(locks_path)
                else:
                    for file in os.listdir(locks_path):
                        os.remove(
                            os.path.join(locks_path, file)
                        )

    @property
    def require_setup(self) -> bool:
        return not os.path.exists(self.app_data_path) \
               or not os.path.exists(self.config_path) \
               or not os.path.exists(self.logs_path) \
               or not os.path.exists(self.log_file_path) \
               or not os.path.exists(self.locks_path)

    @property
    def app_data_path(self):
        if self.name is None or self.name == '':
            name = self.default_name
        else:
            name = self.name

        if sys.platform == 'linux':
            app_data_folder_name = f'.{name}'
        else:
            app_data_folder_name = 'appdata'


        return os.path.join(self.home_folder_path, app_data_folder_name)

    @property
    def logs_path(self):
        if self.logs_folder_name:
            return os.path.join(self.app_data_path, self.logs_folder_name)
        else:
            return self.app_data_path

    @property
    def locks_path(self):
        if self.locks_folder_name:
            return os.path.join(self.app_data_path, self.locks_folder_name)
        else:
            return self.app_data_path

    @property
    def lock_file_path(self):
        return self.get_lock_file_path()

    @property
    def config_path(self):
        """
        Allows to get default app config path.
        :return: path to the default config.
        """
        return self.get_config_path()

    @property
    def log_file_path(self):
        return self.get_log_file_path()

    @property
    def default_name(self):
        return os.path.split(os.getcwd())[1]

    def lock(self):
        return FileBasedLock(self)