FROM python:3.5.6
WORKDIR /opt
COPY requirements.txt /opt
RUN pip install -r requirements.txt
RUN python -m spacy download en
RUN python -m nltk.downloader stopwords
COPY . .
EXPOSE 5000

ENTRYPOINT ["python", "./main.py"]
