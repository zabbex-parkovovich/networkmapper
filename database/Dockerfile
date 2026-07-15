FROM postgres:15-alpine

COPY init.sql /docker-entrypoint-initdb.d/

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

EXPOSE 5432
