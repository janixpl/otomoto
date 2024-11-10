FROM arm64v8/ubuntu

COPY ./app /app
WORKDIR /app
RUN apt update && apt -y upgrade && apt -y install python3 python3-venv

RUN python3 -m venv .venv
RUN .venv/bin/pip install -r requirements.txt

CMD [".venv/bin/python", "text-processing.py"]