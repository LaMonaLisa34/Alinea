FROM python:3.13-alpine AS development

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN addgroup -S app \
    && adduser -S -G app app

WORKDIR /app
RUN chown app:app /app

COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r /tmp/requirements.txt

USER app

FROM development AS runtime

USER root
RUN python -m pip uninstall -y pip \
    && rm -f /usr/local/lib/python3.13/ensurepip/_bundled/pip-*.whl

USER app
