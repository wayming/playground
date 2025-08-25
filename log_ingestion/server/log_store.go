package main

import (
	"fmt"
	"log_ingestion/common"
	"sync"
)

/*
LogBucket
*/
type LogBucket struct {
	logSet common.LogSafe
	index  map[string]string
}

func NewLogBucket() *LogBucket {
	return &LogBucket{
		logSet: common.LogSafe{},
		index:  map[string]string{},
	}
}

/*
InMemoryLogStore
*/
type LogStore interface {
	Push(log common.Log)
	Query(labels map[string]string) []common.Log
	Dump() []common.Log
}
type InMemoryLogStore struct {
	logBuckets        []LogBucket
	bucketsGroupMutex sync.RWMutex
}
type TenantedInMemoryStore struct {
	tenantedStores map[string]*InMemoryLogStore
}

func NewInMemoryLogStore() *InMemoryLogStore {
	return &InMemoryLogStore{
		logBuckets:        []LogBucket{},
		bucketsGroupMutex: sync.RWMutex{},
	}
}

func NewTenantedInMemoryStore() *TenantedInMemoryStore {
	return &TenantedInMemoryStore{
		tenantedStores: make(map[string]*InMemoryLogStore),
	}
}

func (s *InMemoryLogStore) FindBucketsExactMatch(labels map[string]string) *LogBucket {
	for _, bucket := range s.logBuckets {
		if len(bucket.index) != len(labels) {
			continue
		}
		ret := &bucket
		for label, value := range bucket.index {
			if value != labels[label] {
				ret = nil
				break
			}
		}
		return ret
	}
	return nil
}

func (s *InMemoryLogStore) FindBucketsMatchLabels(labels map[string]string) []*LogBucket {
	var buckets []*LogBucket
	for _, bucket := range s.logBuckets {
		for label, value := range labels {
			if value != bucket.index[label] {
				break
			}
		}
		buckets = append(buckets, &bucket)
	}
	return buckets
}

func (s *InMemoryLogStore) Push(log common.Log) {

	bucket := s.FindBucketsExactMatch(log.Labels)
	if bucket != nil {
		fmt.Println("Found exact match bucket for key ", log.Labels)
		bucket.logSet.Push(log)
		return
	}

	s.bucketsGroupMutex.Lock()
	defer s.bucketsGroupMutex.Unlock()

	fmt.Println("Creating new bucket for key ", log.Labels)
	bucket = NewLogBucket()
	bucket.index = log.Labels
	bucket.logSet.Push(log)
	s.logBuckets = append(s.logBuckets, *bucket)
}

func (s *InMemoryLogStore) Query(labels map[string]string) []common.Log {
	s.bucketsGroupMutex.RLock()
	defer s.bucketsGroupMutex.RUnlock()
	var logs []common.Log
	for _, bucket := range s.FindBucketsMatchLabels(labels) {
		logs = append(logs, bucket.logSet.Dump()...)
	}
	return logs
}

func (s *InMemoryLogStore) Dump() []common.Log {
	var logs []common.Log
	for _, bucket := range s.logBuckets {
		logs = append(logs, bucket.logSet.Dump()...)
	}
	return logs
}

func (s *TenantedInMemoryStore) Push(log common.Log) {
	if _, ok := s.tenantedStores[log.TenantID]; !ok {
		s.tenantedStores[log.TenantID] = NewInMemoryLogStore()
	}
	s.tenantedStores[log.TenantID].Push(log)
}

func (s *TenantedInMemoryStore) Query(labels map[string]string) []common.Log {
	var logs []common.Log
	for _, store := range s.tenantedStores {
		logs = append(logs, store.Query(labels)...)
	}
	return logs
}

func (s *TenantedInMemoryStore) Dump() []common.Log {
	var logs []common.Log
	for _, store := range s.tenantedStores {
		logs = append(logs, store.Dump()...)
	}
	return logs
}
