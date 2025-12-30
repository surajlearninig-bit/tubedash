FROM ubuntu:22.04
WORKDIR /app
RUN apt update && apt install -y python3 python3-pip python3-dev gcc libpq-dev
COPY requirements.txt . 
RUN pip3 install --no-cache-dir -r requirements.txt
COPY static/ ./static/
COPY templates/ ./templates/
COPY app.py .
COPY database.py .
COPY models.py .
EXPOSE 8000
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8000"]
