FROM python:2
WORKDIR /usr/src/app
COPY omaha_server/requirements*.txt ./
RUN pip install --no-cache-dir -r requirements_dev.txt
CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]
