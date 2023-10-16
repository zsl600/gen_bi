FROM python:3.11-bullseye
COPY . /app
WORKDIR /app

RUN pip3 install --retries 1 --timeout 5 --no-cache-dir -r requirements.txt

EXPOSE 5000

RUN groupadd -r nonrootgrp -g 333 && \
    useradd -u 334 -r -g nonrootgrp -s /sbin/nologin -c "non-root user" dockeruser

RUN chown dockeruser /app

USER dockeruser

#Needed for awslogs to pick up print lines
ENV PYTHONUNBUFFERED=1

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]


