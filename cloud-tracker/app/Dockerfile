FROM ubuntu:22.04

LABEL maintainer="STFC Scientific Computing"
LABEL description="STFC Cloud Tracker – Apache + mod_wsgi + Flask"

ENV DEBIAN_FRONTEND=noninteractive
ENV APACHE_RUN_USER=www-data
ENV APACHE_RUN_GROUP=www-data
ENV APACHE_LOG_DIR=/var/log/apache2

# ── System packages ──────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    apache2 \
    libapache2-mod-wsgi-py3 \
    python3 \
    python3-pip \
    python3-dev \
    libpq-dev \
    gcc \
    openssl \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Enable Apache modules ────────────────────────────────
RUN a2enmod wsgi ssl rewrite headers expires

# ── Python dependencies ──────────────────────────────────
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# ── Application code ─────────────────────────────────────
WORKDIR /var/www/app
COPY . /var/www/app/
RUN chown -R www-data:www-data /var/www/app

# ── Apache configuration ─────────────────────────────────
COPY apache-app.conf /etc/apache2/sites-available/cloudtracker.conf
RUN a2dissite 000-default.conf && a2ensite cloudtracker.conf

# ── Self-signed certificate (fallback) ───────────────────
# Mount real certs via: -v /path/to/ssl:/etc/ssl/cloudtracker:ro
RUN mkdir -p /etc/ssl/cloudtracker && \
    openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
        -keyout /etc/ssl/cloudtracker/server.key \
        -out    /etc/ssl/cloudtracker/server.crt \
        -subj   "/C=GB/ST=Oxfordshire/L=Didcot/O=STFC/CN=cloud-tracker.stfc.ac.uk"

# ── Entrypoint ────────────────────────────────────────────
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 80 443

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["apache2ctl", "-D", "FOREGROUND"]
