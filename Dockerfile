FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variables (adjust if needed)
ENV PORT=5000

# Expose the port Railway will use
EXPOSE 5000

# Use Gunicorn to serve the Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "sqlflask:app"]

# Copy entrypoint script and make it executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set default environment variable (optional)
ENV FLASK_ENV=production

# Use the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
