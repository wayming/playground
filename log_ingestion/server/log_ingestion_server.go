/*
Simple go web server to receive logs and store them in memory
*/
package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"sort"
	"sync"

	"log_ingestion/common"
)

type LogStore interface {
	Push(log common.Log)
	Query(query string) []common.Log
	Dump() []common.Log
}

type InMemoryLogStore struct {
	// tenant -> label set -> logs
	tenantedLogs  map[string]map[string]*common.LogSafe
	tenantedMutex sync.RWMutex
}

func NewInMemoryLogStore() *InMemoryLogStore {
	return &InMemoryLogStore{
		tenantedLogs:  map[string]map[string]*common.LogSafe{},
		tenantedMutex: sync.RWMutex{},
	}
}

func (s *InMemoryLogStore) LableSetKey(labels map[string]string) string {
	lableKeys := make([]string, 0, len(labels))
	for key := range labels {
		lableKeys = append(lableKeys, key)
	}
	sort.Strings(lableKeys)

	labelSetKey := ""
	for _, key := range lableKeys {
		labelSetKey += fmt.Sprintf("%s=%s", key, labels[key])
	}
	return labelSetKey
}

func (s *InMemoryLogStore) Push(log common.Log) {
	if _, ok := s.tenantedLogs[log.TenantID]; !ok {
		s.tenantedMutex.Lock()
		if _, ok := s.tenantedLogs[log.TenantID]; !ok {
			s.tenantedLogs[log.TenantID] = map[string]*common.LogSafe{}
		}
		s.tenantedMutex.Unlock()
	}

	labelSetKey := s.LableSetKey(log.Labels)
	if _, ok := s.tenantedLogs[log.TenantID][labelSetKey]; !ok {
		s.tenantedLogs[log.TenantID][labelSetKey] = common.NewLogSafe()
	}
	s.tenantedLogs[log.TenantID][labelSetKey].Push(log)
}

func (s *InMemoryLogStore) Query(query string) []common.Log {
	// TODO: implement query
	return s.tenantedLogs[query][query].Query(query)
}

func (s *InMemoryLogStore) Dump() []common.Log {
	logs := []common.Log{}
	s.tenantedMutex.RLock()
	for _, logSafe := range s.tenantedLogs {
		for _, logSafe := range logSafe {
			logs = append(logs, logSafe.Dump()...)
		}
	}
	s.tenantedMutex.RUnlock()
	return logs
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
			fmt.Printf("Error unmarshalling log: %v\n", err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}

		// Override tenant ID if X-Scope-OrgID is set
		if r.Header.Get("X-Scope-OrgID") != log.TenantID {
			log.TenantID = r.Header.Get("X-Scope-OrgID")
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
	logStore := NewInMemoryLogStore()
	http.HandleFunc("/api/v1/push", push_log_handler_closure(logStore))
	http.HandleFunc("/api/v1/dump", dump_log_handler_closure(logStore))
	http.ListenAndServe(":8080", nil)
}
