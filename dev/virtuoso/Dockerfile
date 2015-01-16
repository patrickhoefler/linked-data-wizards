FROM debian:jessie
RUN \
  apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get install -y virtuoso-opensource
RUN \
  sed -i "s/^\(NumberOfBuffers\s*= \)[0-9]*/\18000/" /etc/virtuoso-opensource-6.1/virtuoso.ini && \
  sed -i "s/^\(MaxDirtyBuffers\s*= \)[0-9]*/\16000/" /etc/virtuoso-opensource-6.1/virtuoso.ini
COPY grant-sparql-update.sh /
EXPOSE 8890 1111
CMD virtuoso-t -f -c /etc/virtuoso-opensource-6.1/virtuoso.ini
