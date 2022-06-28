FROM python:3

ADD ./ /usr/local/
RUN pip install boto3 
RUN pip install flask 
RUN pip install requests 

EXPOSE 80/tcp
EXPOSE 443/tcp
EXPOSE 5000/tcp

ENTRYPOINT python /usr/local/application.py
