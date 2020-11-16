# maybe try alpine
FROM ubuntu:20.04

WORKDIR /usr/src/app

RUN apt update -y && \ 
    apt upgrade -y && \
    apt-get install -y --no-install-recommends curl && \
    apt-get install -y --no-install-recommends libssl-dev && \
    apt-get install -y --no-install-recommends python3-pip && \
    apt-get install -y --no-install-recommends build-essential

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends pkg-config

# install rust
RUN curl --proto '=https' --tlsv1.2 https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH /root/.cargo/bin:$PATH

# path differences?
COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 5000

CMD cargo run
