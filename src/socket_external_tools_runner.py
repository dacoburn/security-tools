import json
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("example")

from core import marker
from core.scm import SCM
from core.connectors.bandit import Bandit
from core.connectors.gosec import Gosec
from core.connectors.trufflehog import Trufflehog
from core.load_plugins import load_sumo_logic_plugin, load_ms_sentinel_plugin
import os


SCM_DISABLED = os.getenv("SOCKET_SCM_DISABLED", "false").lower() == "true"
GIT_DIR = os.getenv("GITHUB_REPOSITORY", None)
if not GIT_DIR and SCM_DISABLED:
    print("GIT_DIR is not set and is required if SCM_DISABLED=true")
    exit(1)


def format_events(events):
    formatted_events = []

    for event in events:
        if isinstance(event, str):  # If it's a JSON string, parse it into a dictionary
            try:
                event = json.loads(event)  # Convert string to dictionary
            except json.JSONDecodeError:
                print(f"Skipping invalid event: {event}")
                continue  # Skip invalid JSON entries

        formatted_events.append(event)  # Append properly formatted event

    return formatted_events


def load_json(name, connector: str, connector_type: str = 'single') -> dict:
    json_data = {}
    if connector_type == 'single':
        try:
            file = open(name, 'r')
            json_data = json.load(file)
            file.close()
        except FileNotFoundError:
            print(f"No results found for {connector}")
    else:
        try:
            file = open(name, 'r')
            json_data = {"Issues": []}
            for line in file.readlines():
                try:
                    entry = json.loads(line)
                    json_data['Issues'].append(entry)
                except Exception as error:
                    print(f"Unable to load entry {line} for {connector}")
                    print(error)
        except FileNotFoundError:
            print(f"No results found for {connector}")
    return json_data


sumo_client = load_sumo_logic_plugin()
ms_sentinel = load_ms_sentinel_plugin()

tool_bandit_name = "Bandit"
tool_gosec_name = "Gosec"
tool_trufflehog_name = "Trufflehog"
bandit_name = "bandit_output.json"
gosec_name = "gosec_output.json"
trufflehog_name = "trufflehog_output.json"
bandit_data = load_json(bandit_name, 'bandit')
gosec_data = load_json(gosec_name, 'gosec')
truffle_data = load_json(trufflehog_name, 'truffle', 'multi')


if bandit_data or gosec_data or truffle_data:
    if not SCM_DISABLED:
        scm = SCM()
        bandit_marker = marker.replace("REPLACE_ME", tool_bandit_name)
        bandit_output, bandit_result = Bandit.create_output(
            bandit_data,
            bandit_marker,
            scm.github.repo,
            scm.github.commit,
            scm.github.cwd
        )
        gosec_marker = marker.replace("REPLACE_ME", tool_gosec_name)
        gosec_result = Gosec.create_output(
            gosec_data,
            gosec_marker,
            scm.github.repo,
            scm.github.commit,
            scm.github.cwd
        )
        trufflehog_marker = marker.replace("REPLACE_ME", tool_trufflehog_name)
        truffle_output, truffle_result = Trufflehog.create_output(
            truffle_data,
            trufflehog_marker,
            scm.github.repo,
            scm.github.commit,
            scm.github.cwd
        )
        scm.github.post_comment(tool_bandit_name, bandit_marker, bandit_result)
        scm.github.post_comment(tool_gosec_name, gosec_marker, gosec_result)
        scm.github.post_comment(tool_trufflehog_name, trufflehog_marker, truffle_output)

        bandit_events = bandit_result.get("events", [])
        gosec_events = gosec_result.get("events", [])
        truffle_events = truffle_result.get("events", [])
        print("Issues detected with Security Tools. Please check PR comments")
    else:
        bandit_events = Bandit.process_output(bandit_data, GIT_DIR, bandit_name)
        gosec_events = Gosec.process_output(gosec_data, GIT_DIR, gosec_name)
        truffle_events = Trufflehog.process_output(truffle_data, GIT_DIR, trufflehog_name)

    if sumo_client:
        print("Issues detected with Security Tools. Please check Sumologic Events")
        print(errors) if (errors := sumo_client.send_events(bandit_events.get("events"), bandit_name)) else []
        print(errors) if (errors := sumo_client.send_events(gosec_events.get("events"), gosec_name)) else []
        print(errors) if (errors := sumo_client.send_events(truffle_events.get("events"), trufflehog_name)) else []
    if ms_sentinel:
        print("Issues detected with Security Tools. Please check Microsoft Sentinel Events")
        ms_bandit_name = f"SocketSecurityToolsBandit"
        ms_gosec_name = f"SocketSecurityToolsGosec"
        ms_trufflehog_name = f"SocketSecurityToolsTrufflehog"
        ms_bandit_events = format_events(bandit_events.get("events"))
        ms_gosec_events = format_events(gosec_events.get("events"))
        ms_trufflehog_events = format_events(truffle_events.get("events"))
        print(errors) if (errors := ms_sentinel.send_events(ms_bandit_events, ms_bandit_name)) else []
        print(errors) if (errors := ms_sentinel.send_events(ms_gosec_events, ms_gosec_name)) else []
        print(errors) if (errors := ms_sentinel.send_events(ms_trufflehog_events, ms_trufflehog_name)) else []
    exit(1)
else:
    print("No issues detected with Socket Security Tools")