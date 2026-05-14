FROM python:3.10-slim

RUN useradd -m -u 1000 user

USER user

WORKDIR /app

ENV PATH="/home/user/.local/bin:$PATH"

COPY --chown=user requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=user . .

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]