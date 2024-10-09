# Use the official Python image as a base
FROM python:3.9
COPY src/socket_external_tools_runner.py /app/
COPY src/core /app/
COPY entrypoint.sh /app/

WORKDIR /app

# Install system dependencies and Gosec
RUN apt-get update && \
    apt-get install -y curl git wget && \
    curl -sfL https://raw.githubusercontent.com/securego/gosec/master/install.sh | sh -s latest && \
    mv gosec /usr/local/bin/

# Install Trivy
RUN wget https://github.com/aquasecurity/trivy/releases/latest/download/trivy_0.27.1_Linux-64bit.deb && \
    dpkg -i trivy_0.27.1_Linux-64bit.deb && \
    rm trivy_0.27.1_Linux-64bit.deb

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
