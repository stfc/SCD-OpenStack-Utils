FROM python:3.10

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV AQ_URL=NOT_SET \
    AQ_PREFIX=NOT_SET

ENV RABBIT_HOST=NOT_SET \
    RABBIT_PORT=NOT_SET \
    RABBIT_USERNAME=NOT_SET \
    RABBIT_PASSWORD=NOT_SET


CMD [ "python", "./entrypoint.py"]
