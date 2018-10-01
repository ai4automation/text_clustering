FROM python:3.6
WORKDIR /opt
RUN pip install -r requirements.txt
RUN python -m spacy download en
COPY . .
EXPOSE 3000

ENTRYPOINT ["python", "./cluster_api.py"]
