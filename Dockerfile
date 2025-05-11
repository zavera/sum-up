FROM python:3.9-slim

WORKDIR /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy transformers torch openai

# Set environment variables (update these as needed)
ENV DB_URI=your_cloud_db_uri
ENV SUMMARIZATION_MODEL=your-summarization-model
# OPENAI_API_KEY should be set securely at runtime, not hardcoded here

# Expose port
EXPOSE 8000

# Start the app with uvicorn
CMD ["uvicorn", "summarize:app", "--host", "0.0.0.0", "--port", "8000"]


#docker run -e OPENAI_API_KEY=sk-... -e DB_URI=... -e SUMMARIZATION_MODEL=... -p 8000:8000 your-image-name
