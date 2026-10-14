FROM python:3.12-slim

WORKDIR /suite

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Reports are written to /suite/reports; mount a volume there to keep them.
CMD ["pytest", "--html=reports/report.html", "--self-contained-html", "--junitxml=reports/junit.xml"]
