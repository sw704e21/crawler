#!/bin/bash

cd "/var/www/cryptoserver/crawler/" || exit

git pull

cd ..

docker kill crawler

docker image build -t crawler -f crawler/Dockerfile crawler

docker run -d -p 64000:64000 -v logs:/logs --name crawler crawler