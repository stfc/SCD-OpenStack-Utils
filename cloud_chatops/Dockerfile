FROM python:3
WORKDIR /slack_app
COPY .. /slack_app/
RUN pip3 install --requirement /slack_app/requirements.txt
CMD ["python3", "async_bot.py"]