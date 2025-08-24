package main

import (
	"log_ingestion/common"
	"sync"
	"testing"
	"time"
)

func TestBucketIndex_AddLableSet(t *testing.T) {

	t.Run("AddLableSet", func(t *testing.T) {
		h := &BucketIndex{
			labelsToLevel: make(map[string]int),
			mutex:         sync.Mutex{},
			root:          NewLableIndexNode(""),
		}
		h.AddLableSet(map[string]string{"app": "api", "env": "prod"})
		if len(h.labelsToLevel) != 2 {
			t.Errorf("expected 2 labels, got %d", len(h.labelsToLevel))
		}
		t.Log(h.labelsToLevel)
		t.Log(h.root.Dump(""))

		h.AddLableSet(map[string]string{"env": "dev"})
		if len(h.labelsToLevel) != 2 {
			t.Errorf("expected 2 labels, got %d", len(h.labelsToLevel))
		}
		t.Log(h.labelsToLevel)
		t.Log(h.root.Dump(""))

		h.AddLableSet(map[string]string{"app": "api", "instance": "instance1"})
		if len(h.labelsToLevel) != 3 {
			t.Errorf("expected 3 labels, got %d", len(h.labelsToLevel))
		}
		t.Log(h.labelsToLevel)
		t.Log(h.root.Dump(""))

	})

}

func TestLableIndexNode_Push(t *testing.T) {
	t.Run("Push", func(t *testing.T) {
		index := NewBucketIndex()
		labelSet := map[string]string{"app": "api", "env": "prod"}
		index.AddLableSet(labelSet)
		index.root.Push(common.Log{
			TenantID:  "team-a",
			Labels:    labelSet,
			Timestamp: time.Now().UnixNano() / 1e6, // ms
			Line:      "GET /login 200 OK",
		})
		t.Log(index.root.Dump(""))
	})

}
