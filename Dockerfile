FROM python:3

RUN pip install requests 

COPY main.py /

ENTRYPOINT [ "python3", "main.py" ]
