from src.core.connectors.gosec.classes import GosecTestResult
from mdutils import MdUtils
from typing import Union


class Gosec:
    @staticmethod
    def process_output(data: dict, cwd: str) -> dict:
        results = data.get("Issues")
        tests = []
        metrics = {
            "tests": {},
            "severities": {},
            "output": [],
            # "code": []
        }
        for test in results:
            test_result = GosecTestResult(**test, cwd=cwd)
            tests.append(test_result)
            test_name = f"{test_result.rule_id}_{test_result.severity}"
            if test_result.severity not in metrics["severities"]:
                metrics["severities"][test_result.severity] = 1
            else:
                metrics["severities"][test_result.severity] += 1

            if test_name not in metrics["tests"]:
                metrics["tests"][test_name] = 1
            else:
                metrics["tests"][test_name] += 1
            metrics["output"].append(test_result)
            # metrics["code"].append(test_result.code)

        return metrics

    @staticmethod
    def create_output(data: dict, marker: str, repo: str, commit: str, cwd: str) -> Union[str, None]:
        gosec_result = Gosec.process_output(data, cwd=cwd) # nosec
        output_str = None
        md = MdUtils(file_name="sast_gosec_comments.md")
        if len(gosec_result['output']) > 0:
            md.new_line()
            md.new_line(marker)
            md.new_line()
            for output in gosec_result["output"]:
                output: GosecTestResult
                if hasattr(output, "url"):
                    file = output.url.replace("REPO_REPLACE", repo).replace("COMMIT_REPLACE", commit)
                    file_name = f"[{output.file}]({file})"
                else:
                    file_name = output.file
                md.new_line(f"**{output.details}**")
                md.new_line(f"**Severity**: `{output.severity}`")
                md.new_line(f"**Filename:** {file_name}")
                md.insert_code(output.code, language='go')
                md.new_line("<br>")
                md.new_line()
            md.create_md_file()
            output_str = md.file_data_text.lstrip()
        return output_str
