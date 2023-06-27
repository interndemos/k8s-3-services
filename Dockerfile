FROM python:3.10-alpine

RUN python -m pip install --upgrade pip

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt

COPY . /app
CMD ["python3", "app.py" ]