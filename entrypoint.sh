#!/bin/bash

# Set default values for exclusion and rule options if not provided
TRUFFLEHOG_EXCLUDE_DIR=${INPUT_TRUFFLEHOG_EXCLUDE_DIR:-}
TRUFFLEHOG_RULES=${INPUT_TRUFFLEHOG_RULES:-}

BANDIT_EXCLUDE_DIR=${INPUT_BANDIT_EXCLUDE_DIR:-}
BANDIT_RULES=${INPUT_BANDIT_RULES:-}

GOSEC_EXCLUDE_DIR=${INPUT_GOSEC_EXCLUDE_DIR:-}
GOSEC_RULES=${INPUT_GOSEC_RULES:-}

TRIVY_EXCLUDE_DIR=${INPUT_TRIVY_EXCLUDE_DIR:-}
TRIVY_RULES=${INPUT_TRIVY_RULES:-}

echo "Running Bandit"
# Run Bandit with exclusion directories and rules if specified
bandit_cmd="bandit -r $GITHUB_WORKSPACE -f json -o /tmp/bandit_output.json"
if [[ -n "$BANDIT_EXCLUDE_DIR" ]]; then
  bandit_cmd+=" --exclude $BANDIT_EXCLUDE_DIR"
fi
if [[ -n "$BANDIT_RULES" ]]; then
  bandit_cmd+=" --skip $BANDIT_RULES"
fi
eval $bandit_cmd || :

echo "Running gosec"
# Run Gosec with exclusion directories and rules if specified
gosec_cmd="gosec -fmt json -out /tmp/gosec_output.json "
if [[ -n "$GOSEC_EXCLUDE_DIR" ]]; then
  gosec_cmd+=" -exclude-dir=$GOSEC_EXCLUDE_DIR"
fi
if [[ -n "$GOSEC_RULES" ]]; then
  gosec_cmd+=" -severity=$GOSEC_RULES"
fi
gosec_cmd+=" $GITHUB_WORKSPACE/..."
eval $gosec_cmd || :

echo "Running Trivy"
# Run Trivy with exclusion directories and rules if specified
trivy_cmd="trivy fs --format json --output /tmp/trivy_output.json"
if [[ -n "$TRIVY_EXCLUDE_DIR" ]]; then
  trivy_cmd+=" --skip-dirs $TRIVY_EXCLUDE_DIR"
fi
if [[ -n "$TRIVY_RULES" ]]; then
  trivy_cmd+=" --severity $TRIVY_RULES"
fi
trivy_cmd+=" $GITHUB_WORKSPACE"
eval $trivy_cmd || :

echo "Running Trufflehog"
# Run Trufflehog with exclusion directories and rules if specified
trufflehog_cmd="trufflehog filesystem "
TRUFFLEHOG_EXCLUDE_FILE=$(mktemp)
if [[ -n "$TRUFFLEHOG_EXCLUDE_DIR" ]]; then
  IFS=',' read -ra EXCLUDE_DIRS <<< "$TRUFFLEHOG_EXCLUDE_DIR"
  for dir in "${EXCLUDE_DIRS[@]}"; do
    echo "$dir" >> "$TRUFFLEHOG_EXCLUDE_FILE"
  done
  trufflehog_cmd+=" -x $TRUFFLEHOG_EXCLUDE_FILE"
fi
if [[ -n "$TRUFFLEHOG_RULES" ]]; then
  trufflehog_cmd+=" --rules $TRUFFLEHOG_RULES"
fi
trufflehog_cmd+=" --no-verification -j $GITHUB_WORKSPACE > /tmp/trufflehog_output.json"
eval $trufflehog_cmd || :

# Execute the custom Python script to process findings
mv /tmp/*.json .
python socket_external_tools_runner.py