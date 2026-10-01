FROM redis:8.10.0-alpine3.23

RUN echo "vm.overcommit_memory = 1" > /etc/sysctl.conf

COPY ./redis/redis.conf /etc/redis/redis.conf

EXPOSE 6379

CMD ["redis-server"]
