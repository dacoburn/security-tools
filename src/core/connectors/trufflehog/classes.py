import json
from src.core import base_github


class TrufflehogTestResult:
    SourceMetadata: dict
    SourceID: int
    SourceType: int
    SourceName: str
    DetectorType: int
    DetectorName: str
    DecoderName: str
    Verified: bool
    Raw: str
    RawV2: str
    Redacted: str
    ExtraData: dict
    StructuredData: str
    file: str
    line: int
    cwd: str

    def __init__(self, **kwargs):
        if kwargs:
            for key, val in kwargs.items():
                setattr(self, key, val)
        if hasattr(self, 'file') and hasattr(self, 'cwd'):
            self.file = self.file.replace(self.cwd, '')

    def __str__(self):
        return json.dumps(self.__dict__)

    def set_url(self):
        if hasattr(self, 'file') and hasattr(self, 'line'):
            return  f"{base_github}/REPO_REPLACE/blob/COMMIT_REPLACE/{self.file}#L{self.line}"
