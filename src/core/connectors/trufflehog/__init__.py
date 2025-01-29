import json

from core.connectors.trufflehog.classes import TrufflehogTestResult
from mdutils import MdUtils
from typing import Union


class Trufflehog:
    @staticmethod
    def process_output(data: dict, cwd: str, plugin_name: str = "") -> dict:
        results = data.get("Issues")
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
                test_result = TrufflehogTestResult(**test, cwd=cwd)
                test_result.plugin_name = plugin_name
                metadata = test_result.SourceMetadata.get('Data')
                if metadata is not None:
                    test_result.file = metadata['Filesystem']['file'].lstrip("./").lstrip("/")
                    test_result.file.replace(cwd, "")
                    test_result.line = metadata['Filesystem'].get('line')
                    if test_result.line is not None:
                        test_result.url = test_result.set_url()
                test_name = f"secret_{test_result.DetectorName}_{test_result.DecoderName}"
                if test_name not in metrics["tests"]:
                    metrics["tests"][test_name] = 1
                else:
                    metrics["tests"][test_name] += 1
                tests.append(test_result)
                metrics["output"].append(test_result)
                metrics["events"].append(json.dumps(test_result.__dict__))
                # metrics["code"].append(test_result.code)
        return metrics

    @staticmethod
    def create_output(data: dict, marker: str, repo: str, commit: str, cwd: str) -> (Union[str, None], dict):
        trufflehog_result = Trufflehog.process_output(data, cwd=cwd)
        md = MdUtils(file_name="secrets_trufflehog_comments.md")
        output_str = None
        if len(trufflehog_result['output']) > 0:
            md.new_line()
            md.new_line(marker)
            md.new_line()
            for output in trufflehog_result["output"]:
                output: TrufflehogTestResult
                if hasattr(output, "url"):
                    file = output.url.replace("REPO_REPLACE", repo).replace("COMMIT_REPLACE", commit)
                    file_name = f"[{output.file}]({file})"
                else:
                    file_name = f"`{output.file}`"
                md.new_line(f"**Detection:** {output.DetectorName} - {output.DecoderName}")
                md.new_line(f"**Source Type**: `{output.SourceName}`")
                md.new_line(f"**Filename:** {file_name}")
                # md.new_line(f"**Detected Secret:** {output.Raw}")
                md.new_line("<br>")
                md.new_line()
            md.create_md_file()
            output_str = md.file_data_text.lstrip()
        return output_str, trufflehog_result
