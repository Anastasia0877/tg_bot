FROM python:3.10
WORKDIR /bot
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt