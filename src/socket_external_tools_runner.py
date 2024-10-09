import json
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("example")

from core import marker
from core.scm import SCM
from core.connectors.bandit import Bandit
from core.connectors.gosec import Gosec
from core.connectors.trufflehog import Trufflehog


def load_json(name, connector: str, connector_type: str = 'single') -> dict:
    json_data = {}
    if connector_type == 'single':
        file = open(name, 'r')
        try:
            json_data = json.load(file)
        except Exception as err:
            print(f"Unable to load result for {connector}")
            print(err)
        file.close()
    else:
        file = open(name, 'r')
        json_data = {"Issues": []}
        for line in file.readlines():
            try:
                entry = json.loads(line)
                json_data['Issues'].append(entry)
            except Exception as error:
                print(f"Unable to load entry {line} for {connector}")
                print(error)
    return json_data


scm = SCM()
tool_bandit_name = "Bandit"
tool_gosec_name = "Gosec"
tool_trufflehog_name = "Trufflehog"
bandit_name = "bandit_output.json"
gosec_name = "gosec_output.json"
trufflehog_name = "trufflehog_output.json"
bandit_data = load_json(bandit_name, 'bandit')
gosec_data = load_json(gosec_name, 'gosec')
truffle_data = load_json(trufflehog_name, 'truffle', 'multi')

bandit_marker = marker.replace("REPLACE_ME", tool_bandit_name)
bandit_result = Bandit.create_output(bandit_data, bandit_marker, scm.github.repo, scm.github.commit, scm.github.cwd)
gosec_marker = marker.replace("REPLACE_ME", tool_gosec_name)
gosec_result = Gosec.create_output(gosec_data, gosec_marker, scm.github.repo, scm.github.commit, scm.github.cwd)
trufflehog_marker = marker.replace("REPLACE_ME", tool_trufflehog_name)
truffle_result = Trufflehog.create_output(
    truffle_data,
    trufflehog_marker,
    scm.github.repo,
    scm.github.commit,
    scm.github.cwd
)

scm.github.post_comment(tool_bandit_name, bandit_marker, bandit_result)
scm.github.post_comment(tool_gosec_name, gosec_marker, gosec_result)
scm.github.post_comment(tool_trufflehog_name, trufflehog_marker, truffle_result)