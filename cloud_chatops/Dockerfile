FROM python:3
WORKDIR /opt/cloud_chatops
COPY src /opt/cloud_chatops
COPY requirements.txt /opt/cloud_chatops/
RUN pip3 install --requirement requirements.txt
CMD ["python3", "main.py"]