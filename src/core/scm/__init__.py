from src.core.scm.github import Github


class SCM:
    scm: str
    github: Github
    repo_name: str
    pr_num: int
    timeout: int

    def __init__(
            self,
            timeout: int = None,
            scm: str = "github",
    ) -> None:
        self.scm = scm
        if self.scm.lower() == 'github':
            self.github = Github(request_timeout=timeout)


