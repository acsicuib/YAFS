import os


class myConfig:

    def __init__(self):

        self.graphicTerminal = True
        self.verbose_log = False
        self.myConfiguration = 'small'
        self.resultFolder = 'conf'

        try:
            os.stat(self.resultFolder)
        except:
            os.mkdir(self.resultFolder)
