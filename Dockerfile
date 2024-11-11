FROM arm64v8/ubuntu

RUN apt update && apt -y upgrade && apt -y install python3 python3-venv
WORKDIR /app
COPY requirements.txt /app
RUN python3 -m venv .venv
RUN .venv/bin/pip install -r requirements.txt

COPY app /app/app
COPY tests /app/tests

CMD [".venv/bin/python", "appmy_proj.py"]
