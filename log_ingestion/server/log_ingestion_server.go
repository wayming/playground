/*
Simple go web server to receive logs and store them in memory
*/
package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"

	"log_ingestion/common"
)

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
		if err != nil 
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
