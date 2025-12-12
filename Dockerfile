FROM python:3.10-slim

# Create a non-root user
RUN useradd -m -u 1000 -s /bin/bash user

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
ENV NODE_VERSION 24.12.0

RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash \
    && . "$NVM_DIR/nvm.sh" \
    && nvm install ${NODE_VERSION} \
    && nvm use ${NODE_VERSION} \
    && nvm alias default ${NODE_VERSION} \
    && corepack enable pnpm \
    && echo 'export NVM_DIR="$HOME/.nvm"' >> ~/.bashrc \
    && echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> ~/.bashrc

# Update PATH to include Node.js binaries
ENV PATH $NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH

# Expose port (HF Spaces defaults to 7860)
EXPOSE 7860

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
