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

# Run Bandit with exclusion directories and rules if specified
bandit_cmd="bandit -r . -f json -o /tmp/bandit_output.json"
if [[ -n "$BANDIT_EXCLUDE_DIR" ]]; then
  bandit_cmd+=" --exclude $BANDIT_EXCLUDE_DIR"
fi
if [[ -n "$BANDIT_RULES" ]]; then
  bandit_cmd+=" --skip $BANDIT_RULES"
fi
eval $bandit_cmd

# Run Gosec with exclusion directories and rules if specified
gosec_cmd="gosec -fmt json -out /tmp/gosec_output.json ./..."
if [[ -n "$GOSEC_EXCLUDE_DIR" ]]; then
  gosec_cmd+=" -exclude-dir=$GOSEC_EXCLUDE_DIR"
fi
if [[ -n "$GOSEC_RULES" ]]; then
  gosec_cmd+=" -severity=$GOSEC_RULES"
fi
eval $gosec_cmd

# Run Trivy with exclusion directories and rules if specified
trivy_cmd="trivy fs --format json --output /tmp/trivy_output.json ."
if [[ -n "$TRIVY_EXCLUDE_DIR" ]]; then
  trivy_cmd+=" --ignore $TRIVY_EXCLUDE_DIR"
fi
if [[ -n "$TRIVY_RULES" ]]; then
  trivy_cmd+=" --severity $TRIVY_RULES"
fi
eval $trivy_cmd

# Run Trufflehog with exclusion directories and rules if specified
trufflehog_cmd="trufflehog filesystem --json . > /tmp/trufflehog_output.json"
if [[ -n "$TRUFFLEHOG_EXCLUDE_DIR" ]]; then
  trufflehog_cmd+=" --exclude_dirs $TRUFFLEHOG_EXCLUDE_DIR"
fi
if [[ -n "$TRUFFLEHOG_RULES" ]]; then
  trufflehog_cmd+=" --rules $TRUFFLEHOG_RULES"
fi
eval $trufflehog_cmd

# Execute the custom Python script to process findings
python socket_external_tools_runner.py