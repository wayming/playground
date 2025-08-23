// simple go web server hello world
package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"

	"log_ingestion/common"
)

type LogStore interface {
	Push(log common.Log)
	Query(query string) []common.Log
	Dump() []common.Log
}

type InMemoryLogStore struct {
	logs []common.Log
}

func (s *InMemoryLogStore) Push(log common.Log) {
	s.logs = append(s.logs, log)
}

func (s *InMemoryLogStore) Query(query string) []common.Log {
	return s.logs
}

func (s *InMemoryLogStore) Dump() []common.Log {
	return s.logs
}

/*
curl -X POST http://localhost:8080/api/v1/push -H "Content-Type: application/json" -d '

	{
	    "tenant_id": "team-a",
	    "labels": {"app":"api","env":"prod"},
	    "timestamp": 1732000000000,
	    "line": "GET /login 200 OK"
	}

'
*/
func push_log_handler_closure(logStore LogStore) func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		body, err := io.ReadAll(r.Body)
		if err != nil {
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		log := common.Log{}
		err = json.Unmarshal(body, &log)
		if err != nil {
			fmt.Println(err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		logStore.Push(log)
		w.WriteHeader(http.StatusOK)
	}
}

func dump_log_handler_closure(logStore LogStore) func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(logStore.Dump())
	}
}

func main() {
	logStore := &InMemoryLogStore{}
	http.HandleFunc("/api/v1/push", push_log_handler_closure(logStore))
	http.HandleFunc("/api/v1/dump", dump_log_handler_closure(logStore))
	http.ListenAndServe(":8080", nil)
}
