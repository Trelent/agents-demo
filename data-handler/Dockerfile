FROM python:3.12-slim

RUN pip install --no-cache-dir csvkit

COPY skills/ /skills/

CMD ["sh", "-c", "while true; do \
    if [ -f /shutdown/terminate ]; then exit 0; fi; \
    sleep 1; \
done"]
