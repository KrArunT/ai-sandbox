FROM python:3.10-slim

# Create a non-root user
RUN useradd -m -u 1000 user

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

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
