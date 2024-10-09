import json
from core import base_github


class BanditTestResult:
    code: str
    col_offset: int
    end_col_offset: int
    filename: str
    issue_confidence: str
    issue_cw: dict
    issue_severity: str
    issue_text: str
    line_number: int
    line_range: list
    more_info: str
    test_id: str
    test_name: str
    url: str
    cwd: str

    def __init__(self, **kwargs):
        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)

        if hasattr(self, 'filename') and hasattr(self, 'cwd'):
            self.filename = self.filename.replace(self.cwd, '')
        if not hasattr(self, "issue_cw"):
            self.issue_cw = {}
        if not hasattr(self, "line_range"):
            self.line_range = []
        self.filename = self.filename.lstrip("./").lstrip("/")
        if hasattr(self, 'filename') and hasattr(self, 'line_number'):
            self.url = f"{base_github}/REPO_REPLACE/blob/COMMIT_REPLACE/{self.filename}#{self.line_number}"

    def __str__(self):
        return json.dumps(self.__dict__)
