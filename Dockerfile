FROM python:3.8-slim-buster

ENV APP_HOME /MercarieProject 
ENV PYTHONUNBUFFERED True
WORKDIR $APP_HOME

ADD requirments.txt . 
RUN pip install --no-cach-dir -r requirments.txt && pip install --no-cach-dir gunicorn
RUN groupadd -r app && useradd -r -g app app 


COPY . / 
USER app 

CMD exec gunicorn --bind :$PORT --log-level info --workers 1 --threads 8 --timeout 0 app:server