all: client server

.PHONY: client server

client:
	go build -o bin/log_ingestion_client ./client

server:
	go build -o bin/log_ingestion_server ./server
