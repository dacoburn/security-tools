# Security Tools Scanning

The purpose of this action is to run various security tools, process their output, and then comment the results on a PR. It is expected to only run this on PRs

## Example Usage

```yaml
name: Security Scan Workflow

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write  # Set required permissions here

    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Run Security Scan and Comment Action
        uses: dacoburn/security-tools@1.0.2
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          trufflehog_exclude_dir: "node_modules/*,vendor,.git/*"
          bandit_exclude_dir: "tests,migrations,tests,test,.venv,venv"
          bandit_rules: "B101,B102,B105,B106,B107,B110,B603,B605,B607"
          gosec_rules: "critical,high,medium"
          trivy_exclude_dir: "/path/to/ignore"
```
