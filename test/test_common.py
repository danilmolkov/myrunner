import os

import myrunner.myrunner as mr
from myrunner.hclReader import HclReader

class TestMyRunner:
    def __init__(self, runlist_name: str | None, data=None) -> None:
        if data is not None and runlist_name is None:
            self.hcl = HclReader(data)
        else:
            self.runners_path = f'{os.path.dirname(__file__)}/runners'
            self.hcl = HclReader(f'{self.runners_path}/{runlist_name}')
        self.runs = self.hcl.getruns()
        self.setting = self.hcl.getsettings()
        self.imports = self.hcl.getimports()

    def command(self, runToRun: str) -> int:
        return mr.commandRun(self.runs, runToRun, self.imports)