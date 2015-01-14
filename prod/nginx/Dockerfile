FROM nginx:1.7
RUN \
  rm /etc/nginx/conf.d/default.conf && \
  rm /etc/nginx/conf.d/example_ssl.conf
COPY static /usr/share/nginx/html/static
COPY nginx.conf /etc/nginx/
COPY replace-and-run.sh /
RUN chmod 755 /replace-and-run.sh
CMD /replace-and-run.sh
