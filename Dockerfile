FROM python:3.13-alpine AS development

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r /tmp/requirements.txt

FROM development AS runtime

RUN python -m pip uninstall -y pip \
    && rm -f /usr/local/lib/python3.13/ensurepip/_bundled/pip-*.whl
