FROM python:3.10-slim

# Create a non-root user
RUN useradd -m -u 1000 user

# Install system dependencies (curl, git for nvm/app)
RUN apt-get update && apt-get install -y curl git \
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

# Install NVM, Node.js 24, and PNPM
ENV NVM_DIR /home/user/.nvm
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash \
    && . "$NVM_DIR/nvm.sh" \
    && nvm install 24 \
    && corepack enable pnpm

# Expose port (HF Spaces defaults to 7860)
EXPOSE 7860

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
