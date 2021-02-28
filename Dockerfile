# bare minimum Dockerfile configuration

FROM python:3

# copying only the requirements.txt file in a separate build step before adding the entire application into the image
# to avoid invalidating the Docker build cache every time you're copying the entire application into the image
COPY requirements.txt /requirements.txt

RUN pip install -r requirements.txt

WORKDIR matilda

COPY . /

# CMD [ "python", "./testy.py" ] # just test