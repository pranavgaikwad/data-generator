FROM centos/python-36-centos7:latest

COPY file-generator.py /usr/local/bin/file-generator

COPY file-operations.py /usr/local/bin/file-operations

COPY entrypoint.sh /usr/local/bin/entrypoint

CMD /usr/local/bin/entrypoint
