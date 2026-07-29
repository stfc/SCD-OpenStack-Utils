FROM alpine:3.19

RUN apk add --no-cache postgresql15-client dcron bash tzdata

COPY backup.sh /usr/local/bin/backup.sh
RUN chmod +x /usr/local/bin/backup.sh

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

RUN mkdir -p /backups

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
