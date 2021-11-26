FROM python:3
RUN apt-get update
COPY ./src ./src
COPY ./requirements.txt ./requirements.txt
RUN pip install -r /requirements.txt
RUN mkdir /logs
EXPOSE 64000
ENTRYPOINT ["python3"]
CMD ["/src/main.py"]
