FROM prom/prometheus:main

COPY config.yml /etc/prometheus/config.yml
COPY alert.rules /etc/prometheus/alert.rules

CMD ["--config.file=/etc/prometheus/config.yml", \
     "--storage.tsdb.path=/prometheus", \
     "--web.console.libraries=/usr/share/prometheus/console_libraries", \
     "--web.console.templates=/usr/share/prometheus/consoles", \
     "--web.enable-lifecycle"]