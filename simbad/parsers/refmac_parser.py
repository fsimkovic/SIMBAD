"""Returns scores from a refmac log file"""

__author__ = "Adam Simpkin"
__date__ = "03 May 2017"
__version__ = "0.1"


class RefmacParser(object):
    """Class to mine information from a refmac log file"""

    def __init__(self, logfile):
        self._logfile = None

        self.init_r_free = 1.0
        self.init_r_fact = 1.0
        self.final_r_free = 1.0
        self.final_r_fact = 1.0
        self.version = None

        self.logfile = logfile

        self.parse()

    @property
    def logfile(self):
        """Return logfile"""
        return self._logfile

    @logfile.setter
    def logfile(self, logfile):
        """Define logfile"""
        self._logfile = logfile

    def parse(self):
        """Parse information from the logfile"""

        with open(self.logfile) as f:
            for line in f:
                if line.startswith(" ### CCP4") and "version" in line:
                    self.version = line.split()[5]
                elif line.startswith('           R factor'):
                    fields = line.strip().split()
                    self.init_r_fact = float(fields[-2])
                    self.final_r_fact = float(fields[-1])
                elif line.startswith('             R free'):
                    fields = line.strip().split()
                    self.init_r_free = float(fields[-2])
                    self.final_r_free = float(fields[-1])
                else:
                    pass
        return
