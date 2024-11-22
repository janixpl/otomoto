FROM arm64v8/python:3.12

RUN apt update && apt -y upgrade && apt -y install python3 python3-venv
WORKDIR /app
COPY requirements.txt .
RUN python3 -m venv /app/.venv && \
    /app/.venv/bin/pip install --no-cache-dir --upgrade pip && \
    /app/.venv/bin/pip install --no-cache-dir -r requirements.txt

COPY app .
COPY data ./data
COPY tests ./tests

EXPOSE 5001
ENV PATH="/app/.venv/bin:$PATH"

CMD ["python3", "my_proj.py"]
