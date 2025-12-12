FROM python:3.10-slim

# Create a non-root user
RUN useradd -m -u 1000 user

# Install system dependencies (Node.js)
RUN apt-get update && apt-get install -y curl gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install uv

# Copy application code
COPY  . .

# Make sure permissions are correct
RUN chown -R user:user /app

# Switch to non-root user
USER user

# Expose port (HF Spaces defaults to 7860)
EXPOSE 7860

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
