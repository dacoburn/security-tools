from core.connectors.bandit.classes import BanditTestResult
from mdutils import MdUtils
from typing import Union


class Bandit:
    @staticmethod
    def process_output(data: dict, cwd: str) -> dict:
        results = data.get("results")
        tests = []
        metrics = {
            "tests": {},
            "severities": {},
            "output": [],
            # "code": []
        }
        if results is not None and len(results) > 0:
            for test in results:
                test_result = BanditTestResult(**test, cwd=cwd)
                tests.append(test_result)
                test_name = f"{test_result.test_id}_{test_result.test_name}_{test_result.issue_severity}"
                if test_result.issue_severity not in metrics["severities"]:
                    metrics["severities"][test_result.issue_severity] = 1
                else:
                    metrics["severities"][test_result.issue_severity] += 1

                if test_name not in metrics["tests"]:
                    metrics["tests"][test_name] = 1
                else:
                    metrics["tests"][test_name] += 1
                metrics["output"].append(test_result)
                # metrics["code"].append(test_result.code)
        return metrics

    @staticmethod
    def create_output(data: dict, marker: str, repo: str, commit: str, cwd: str) -> Union[str, None]:
        bandit_result = Bandit.process_output(data, cwd=cwd)
        md = MdUtils(file_name="sast_bandit_comments.md")
        output_str = None
        if len(bandit_result['output']) > 0:
            md.new_line()
            md.new_line(marker)
            md.new_line()
            for output in bandit_result["output"]:
                output: BanditTestResult
                if hasattr(output, "url"):
                    file = output.url.replace("REPO_REPLACE", repo).replace("COMMIT_REPLACE", commit)
                    file_name = f"[{output.filename}]({file})"
                else:
                    file_name = f"`{output.filename}`"
                md.new_line(f"**{output.issue_text}**")
                md.new_line(f"**Severity**: `{output.issue_severity}`")
                md.new_line(f"**Filename:** {file_name}")
                md.insert_code(output.code, language='python')
                md.new_line("<br>")
                md.new_line()
            md.create_md_file()
            output_str = md.file_data_text.lstrip()
        return output_str
