FROM google/nodejs:0.10.33

RUN npm install -g aglio

WORKDIR /data
EXPOSE 3000
CMD ["make"]