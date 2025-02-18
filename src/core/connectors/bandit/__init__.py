from core.connectors.bandit.classes import BanditTestResult
from mdutils import MdUtils
from typing import Union
import json


class Bandit:
    @staticmethod
    def process_output(data: dict, cwd: str, plugin_name: str = None) -> dict:
        results = data.get("results")
        tests = []
        metrics = {
            "tests": {},
            "severities": {},
            "output": [],
            "events": []
            # "code": []
        }
        if results is not None and len(results) > 0:
            for test in results:
                test_result = BanditTestResult(**test, cwd=cwd)
                test_result.plugin_name = plugin_name
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
                metrics["events"].append(json.dumps(test_result.__dict__))
                # metrics["code"].append(test_result.code)
        return metrics

    @staticmethod
    def create_output(data: dict, marker: str, repo: str, commit: str, cwd: str) -> (Union[str, None], dict):
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
        return output_str, bandit_result

    @staticmethod
    def transform_bandit_event(event):
        """Transforms a Bandit security event into the correct Sentinel schema."""
        return {
            "TimeGenerated": datetime.utcnow().isoformat(),
            "SourceComputerId": event.get("cwd", "Unknown"),
            "OperationStatus": event.get("issue_severity", "Unknown"),
            "Detail": event.get("issue_text", "Unknown"),
            "OperationCategory": event.get("test_name", "Static Analysis"),
            "Solution": event.get("more_info", "No remediation guide available"),
            "Message": event.get("issue_text", "Unknown issue"),
            "FilePath": event.get("filename", "Unknown"),
            "URL": event.get("url", "N/A"),
            "Timestamp": event.get("timestamp", datetime.utcnow().isoformat()),
            "Plugin": "Bandit",
            "Severity": event.get("issue_severity", "Unknown"),
            "TestID": event.get("test_id", "Unknown"),
            "CWE_ID": event.get("issue_cwe", {}).get("id", "Unknown"),
            "CWE_Link": event.get("issue_cwe", {}).get("link", "Unknown")
        }
