FROM google/cloud-sdk:slim

RUN apt-get update && apt-get install -y \
    jq \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

CMD ["/bin/bash"]
