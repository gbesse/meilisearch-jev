FROM python:3.12-slim

WORKDIR /app
COPY --chown=65532:65532 jev_common.py meilisearch_jev.py ./
USER 65532:65532
ENV PORT=8765 PYTHONUNBUFFERED=1
EXPOSE 8765
CMD ["python", "meilisearch_jev.py", "--serve", "--host", "0.0.0.0"]
