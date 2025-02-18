import json
from core import base_github
from datetime import datetime, timezone

class GosecTestResult:
    severity: str
    confidence: str
    cwe: dict
    rule_id: str
    details: str
    file: str
    code: str
    line: str
    column: str
    nosec: bool
    suppressions: str
    cwd: str
    timestamp: str
    plugin_name: str

    def __init__(self, **kwargs):
        if kwargs:
            for key, val in kwargs.items():
                setattr(self, key, val)
        if hasattr(self, 'file') and hasattr(self, 'cwd'):
            self.file = self.file.replace(self.cwd, '')
        self.file = self.file.lstrip("./").lstrip("/")
        if hasattr(self, 'file') and hasattr(self, 'line'):
            self.url = f"{base_github}/REPO_REPLACE/blob/COMMIT_REPLACE/{self.file}#L{self.line}"
        self.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S,%f")[:-3] + " +0000"

    def __str__(self):
        return json.dumps(self.__dict__)
