FROM python:3.11-slim
LABEL maintainer="Shakti Nayak <nshakti.10@gmail.com>"

ENV PYTHONUNBUFFERED 1
ENV HNSWLIB_NO_NATIVE 1
ENV DEBUG 0
WORKDIR /code
RUN apt-get update && apt-get install -y build-essential ffmpeg libsm6 libxext6
RUN pip install pipenv
COPY ./Pipfile ./Pipfile.lock /code/
RUN pipenv install --system --deploy --ignore-pipfile
ADD medscan/ /code
RUN python3 manage.py collectstatic --no-input
EXPOSE 45680

CMD ["./run.sh"]
