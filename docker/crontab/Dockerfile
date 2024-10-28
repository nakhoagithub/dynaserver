FROM alpine AS base

RUN apk add --no-cache mongodb-tools

WORKDIR /app

COPY . .

RUN /usr/bin/crontab /app/crontab.txt

RUN chmod +x /app/scripts/mongo-backup.sh

CMD [ "crond", "-f" ]