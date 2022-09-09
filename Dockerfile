# Use non-slim image as includes GCC
FROM python:3.10-bullseye

WORKDIR /app
COPY requirements.txt requirements.txt
# Install git to download utils library
RUN apt update && apt -yq install git
RUN python3 -m pip install --upgrade pip && pip install -r requirements.txt
COPY . .

EXPOSE 8080

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8080"]
