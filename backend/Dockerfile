FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Add the script to wait for the database
COPY wait_for_db.py . 
CMD ["python3", "run.py"]