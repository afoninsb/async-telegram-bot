FROM python:3.10-slim

ENV HOME /
ENV PYTHONPATH ${HOME}

RUN apt-get update && apt-get upgrade -y && apt-get install nano -y

WORKDIR ${HOME}/

COPY requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .

CMD ["python", "bot.py" ]
