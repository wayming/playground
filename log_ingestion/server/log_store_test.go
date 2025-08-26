package main

import (
	"log_ingestion/common"
	"testing"
	"time"
)

func TestInMemoryLogStore_Push(t *testing.T) {
	t.Run("PushSingle", func(t *testing.T) {
		s := &InMemoryLogStore{
			logBuckets: []LogBucket{},
		}
		s.Push(common.Log{
			TenantID:  "team-a",
			Labels:    map[string]string{"app": "api", "env": "prod"},
			Timestamp: time.Now().UnixNano() / 1e6, // ms
			Line:      "GET /login 200 OK",
		})
		if len(s.logBuckets) != 1 {
			t.Errorf("expected 1 log bucket, got %d", len(s.logBuckets))
		}
		t.Log(s.logBuckets[0].index)
		t.Log(s.logBuckets[0].logSet.Dump())
	})

	t.Run("PushMulti", func(t *testing.T) {
		s := &InMemoryLogStore{
			logBuckets: []LogBucket{},
		}
		s.Push(common.Log{
			TenantID:  "team-a",
			Labels:    map[string]string{"app": "api"},
			Timestamp: time.Now().UnixNano() / 1e6, // ms
			Line:      "GET /login 200 OK",
		})
		s.Push(common.Log{
			TenantID:  "team-a",
			Labels:    map[string]string{"env": "prod"},
			Timestamp: time.Now().UnixNano() / 1e6, // ms
			Line:      "GET /login 200 OK",
		})
		s.Push(common.Log{
			TenantID:  "team-a",
			Labels:    map[string]string{"app": "api", "env": "prod"},
			Timestamp: time.Now().UnixNano() / 1e6, // ms
			Line:      "GET /login 200 OK",
		})

		if len(s.logBuckets) != 3 {
			t.Errorf("expected 3 log buckets, got %d", len(s.logBuckets))
		}
		t.Log(s.Dump())
	})

}
