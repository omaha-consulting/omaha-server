FROM python:2

WORKDIR /usr/src/app

COPY ./requirements/base.txt ./
RUN pip install --no-cache-dir -r base.txt


CMD [ "python", "/usr/src/app/manage.py", "runserver", "0.0.0.0:8000" ]
