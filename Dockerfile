FROM python:3.8

COPY main.py /usr/local/bin/file-generator

COPY entrypoint.sh /usr/local/bin/entrypoint

RUN chmod +x /usr/local/bin/entrypoint /usr/local/bin/file-generator

CMD /usr/local/bin/entrypoint

