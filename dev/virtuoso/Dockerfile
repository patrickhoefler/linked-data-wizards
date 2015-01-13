FROM debian:jessie
RUN \
  apt-get update && \
  echo "virtuoso-opensource-6.1 virtuoso-opensource-6.1/dba-password password dba" >> virtuosocdebonf && \
  echo "virtuoso-opensource-6.1 virtuoso-opensource-6.1/dba-password-again password dba" >> virtuosocdebonf && \
  debconf-set-selections virtuosodebconf && \
  DEBIAN_FRONTEND=noninteractive apt-get install -y virtuoso-opensource
RUN \
  sed -i "s/^\(NumberOfBuffers\s*= \)[0-9]*/\18000/" /etc/virtuoso-opensource-6.1/virtuoso.ini && \
  sed -i "s/^\(MaxDirtyBuffers\s*= \)[0-9]*/\16000/" /etc/virtuoso-opensource-6.1/virtuoso.ini
EXPOSE 8890 1111
CMD virtuoso-t -f -c /etc/virtuoso-opensource-6.1/virtuoso.ini
