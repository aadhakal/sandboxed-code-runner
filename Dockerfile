FROM python:3.11

RUN apt-get update && apt-get install -y \
    build-essential git autoconf bison flex gcc libtool make pkg-config \
    libnl-route-3-dev libprotobuf-dev protobuf-compiler \
    && git clone --depth 1 https://github.com/google/nsjail.git /tmp/nsjail \
    && cd /tmp/nsjail && make && cp nsjail /usr/local/bin/ \
    && apt-get clean && rm -rf /tmp/nsjail /var/lib/apt/lists/*

RUN pip install flask==2.3.3 gunicorn==21.2.0 numpy==1.24.3 pandas==2.0.3 requests==2.31.0 scipy==1.11.1 matplotlib==3.7.2

WORKDIR /app
COPY app.py .
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--timeout", "60", "app:app"]