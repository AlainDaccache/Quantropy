# Bare minimum Dockerfile configuration. First, make sure you're cd'ed into the Quantropy directory
#    To build the Docker image: 'docker build -t matilda .' (do not forget the dot at the end)
#    To run the Docker image: 'docker run -d -p 5000:5000 matilda'

FROM python:3.8-slim

MAINTAINER Alain Daccache "alaindacc@gmail.com"

# && \ isn’t Docker specific, but tells Linux to run the next command as part of the existing line
# (instead of using multiple RUN directives, you can use just one)
RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

# Copy files from the first parameter (the source .) to the destination parameter (in this case, /app)
# We copy just the requirements.txt first, in a seperate build step (before adding the entire application into the image)
# to leverage Docker cache (i.e. avoid invalidating the Docker build cache every time you're copying the entire application into the image)
COPY ./requirements.txt /app/requirements.txt

# Sets the working directory (all following instructions operate within this directory) of the Docker container
WORKDIR /app

# pip installs from requirements.txt as normal.
RUN pip install -r requirements.txt

COPY . .

# ENTRYPOINT configures the container to run as an executable; only the last ENTRYPOINT instruction executes
ENTRYPOINT [ "python" ]
CMD [ "matilda/__init__.py" ]
