FROM python:3.12

WORKDIR /app

RUN python3 -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ gud-finahdinner