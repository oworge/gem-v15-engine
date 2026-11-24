FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi && \
    pip install --no-cache-dir flask requests numpy scipy

EXPOSE 7860
ENV PORT=7860
CMD ["python", "-c", "import os, app; port = int(os.environ.get('PORT', 7860)); app.app.run(host='0.0.0.0', port=port)"]
