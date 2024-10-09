import json
import os
from github import Github, Repository, PullRequest, IssueComment
from core import log


repo: Repository
pull_request: PullRequest
timeout = 30
repo_name = os.getenv("GITHUB_REPOSITORY")
# Load the event data to get the pull request number
event_path = os.getenv("GITHUB_EVENT_PATH")
with open(event_path, 'r') as f:
    event_data = json.load(f)
# Extract the pull request number from the event data
pr_number = event_data["pull_request"]["number"] if "pull_request" in event_data else None
if pr_number is None:
    log.warn("Unable to get PR number from event data, assuming not a PR")
    exit(0)
commit_sha = os.getenv("GITHUB_SHA")
gh_api_token = os.getenv("GH_API_TOKEN") or os.getenv("GITHUB_TOKEN") or os.getenv("github_token")
working_directory = os.getenv("GITHUB_WORKSPACE")

if working_directory is None:
    log.error("Unable to get Github Working Directory from GITHUB_WORKSPACE")
    exit(1)

if commit_sha is None:
    log.error("Unable to get Github Commit Hash from GITHUB_SHA")
    exit(1)

if repo_name is None:
    log.error("Unable to get Github Repo from GITHUB_REPOSITORY")
    exit(1)

if pr_number is None:
    log.error("Unable to get Github PR from GITHUB_EVENT_PULL_REQUEST_NUMBER")
    exit(1)

if gh_api_token is None:
    log.error("Unable to get Github Token from GH_API_TOKEN")
    exit(1)

g = Github(gh_api_token)
repo = g.get_repo(repo_name)
pull_request = repo.get_pull(int(pr_number))


class Github:
    request_timeout: int
    repo: str
    commit: str
    cwd: str

    def  __init__(self, request_timeout: int = None, **kwargs):
        if request_timeout is not None:
            global timeout
            timeout = request_timeout
        self.repo = repo_name
        self.commit = commit_sha
        self.cwd = working_directory
        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)

    def __str__(self):
        return json.dumps(self.__dict__)

    # Define function to find and replace existing comments or create new ones
    @staticmethod
    def post_comment(tool_name: str, marker: str, issues: str = None):
        # Construct the comment body with a hidden marker line
        comment_body = f"# {tool_name} Results\n<br>\n"
        comment_body += f"{issues}\n"

        # Search for an existing comment with the marker
        existing_comment = None
        for comment in pull_request.get_issue_comments():
            if marker in comment.body:
                existing_comment: IssueComment
                existing_comment = comment
                break

        # Update the existing comment or create a new one
        if issues:
            if existing_comment:
                existing_comment.edit(comment_body)
            else:
                pull_request.create_issue_comment(comment_body)
        else:
            if existing_comment is not None:
                existing_comment.delete()
