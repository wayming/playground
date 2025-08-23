/*
Simple go web server to receive logs and store them in memory
*/
package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"sync"

	"log_ingestion/common"
)

var count int = 0

type LogStore interface {
	Push(log common.Log)
	Query(query string) []common.Log
	Dump() []common.Log
}

type InMemoryLogStore struct {
	logs  []common.Log
	mutex sync.Mutex
}

func (s *InMemoryLogStore) Push(log common.Log) {
	s.mutex.Lock()
	s.logs = append(s.logs, log)
	s.mutex.Unlock()
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
		count++
		fmt.Printf("Log to push: %d\n", count)
		body, err := io.ReadAll(r.Body)
		if err != nil {
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		log := common.Log{}
		err = json.Unmarshal(body, &log)
		if err != nil {
			fmt.Printf("Error unmarshalling log: %v\n", err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		logStore.Push(log)
		fmt.Printf("Log pushed: %+v, total: %d\n", log, len(logStore.Dump()))
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
