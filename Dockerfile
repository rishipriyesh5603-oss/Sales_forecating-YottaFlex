FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python run.py --reps 100 --accounts 100 --opportunities 1000 --quarters 4
EXPOSE 8000
CMD ["uvicorn","src.api:app","--host","0.0.0.0","--port","8000"]
