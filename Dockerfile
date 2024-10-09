# Use the official Python image as a base
FROM python:3.9
COPY src/socket_external_tools_runner.py /app/
COPY src/core /app/
COPY entrypoint.sh /app/
ENV PATH=$PATH:/usr/local/go/bin
WORKDIR /app

# Setup Golang
RUN curl -sfL https://go.dev/dl/go1.23.2.linux-amd64.tar.gz > go1.23.2.linux-amd64.tar.gz
RUN rm -rf /usr/local/go && tar -C /usr/local -xzf go1.23.2.linux-amd64.tar.gz

# Install system dependencies and Gosec
RUN apt-get update && \
    apt-get install -y curl git wget
RUN curl -sfL https://raw.githubusercontent.com/securego/gosec/master/install.sh  | sh -s v2.21.4

# Install Trivy
RUN curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin v0.18.3

# Install Bandit and Trufflehog using pip
RUN pip install bandit trufflehog

# Copy the entrypoint script and make it executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh


COPY requirements.txt /scripts/requirements.txt
# Install Python dependencies from requirements.txt
RUN pip install -r /scripts/requirements.txt

# Define entrypoint
ENTRYPOINT ["/entrypoint.sh"]
