FROM python:3.12

WORKDIR /app

COPY ./requirements.txt /app
RUN python3 -m venv venv
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src /app/src

COPY ./installation.sh /app/installation.sh
RUN chmod +x ./installation.sh
RUN ./installation.sh


# RUN chmod +x /app/src/gud

# # symlink
# RUN ln -s /app/src/gud /usr/local/bin/gud