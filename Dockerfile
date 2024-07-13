FROM python:3.12

WORKDIR /app

COPY ./requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY src /app/src

RUN chmod +x /app/src/gud

# symlink
RUN ln -s /app/src/gud /usr/local/bin/gud