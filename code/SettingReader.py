# Modules
import ConfigParser


class SettingReader:
    """SettingReader reads settings and provides them on demand"""

    def __init__(self, settings_file):
        # use default value
        if settings_file is None:
            settings_file = 'default_settings.ini'
            pass
        self.settings_file = settings_file

        # create parser
        self.config = ConfigParser.ConfigParser()

        # read settings file
        self.config.read(self.settings_file)

        # identify sections
        sections = self.config.sections()

        # create settings dictionary
        self.values = {}
        for section in sections:
            self.values[section] = self.configSectionMap(section)
            pass

    def configSectionMap(self, section):
        dict1 = {}
        options = self.config.options(section)
        for option in options:
            try:
                dict1[option] = self.config.get(section, option)
                if dict1[option] == -1:
                    DebugPrint("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                dict1[option] = None
        return dict1
