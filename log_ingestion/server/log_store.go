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

func NewLogBucket(index map[string]string) *LogBucket {
	return &LogBucket{
		logSet: common.LogSafe{},
		index:  index,
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
	tenantedMutex  sync.RWMutex
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
		tenantedMutex:  sync.RWMutex{},
	}
}

func (s *InMemoryLogStore) addNewBucket(index map[string]string) *LogBucket {
	s.bucketsGroupMutex.Lock()
	defer s.bucketsGroupMutex.Unlock()

	fmt.Println("Adding new bucket for key ", index)
	bucket := s.findBucketsExactMatchUnsafe(index)
	if bucket != nil {
		fmt.Println("Found exact match bucket for key ", index)
		return bucket
	}
	s.logBuckets = append(s.logBuckets, *NewLogBucket(index))
	fmt.Println("All buckets: ", s.logBuckets)
	return &s.logBuckets[len(s.logBuckets)-1]
}

func (s *InMemoryLogStore) findBucketsExactMatchUnsafe(index map[string]string) *LogBucket {
	for i := range s.logBuckets {
		bucket := &s.logBuckets[i]
		if len(bucket.index) != len(index) {
			continue
		}
		ret := bucket
		for label, value := range index {
			if value != bucket.index[label] {
				ret = nil
				break
			}
		}
		if ret != nil {
			return ret
		}
	}
	return nil
}

func (s *InMemoryLogStore) FindBucketsExactMatch(index map[string]string) *LogBucket {
	// TODO
	s.bucketsGroupMutex.RLock()
	defer s.bucketsGroupMutex.RUnlock()
	return s.findBucketsExactMatchUnsafe(index)
}

func (s *InMemoryLogStore) FindBucketsIncludeIndex(index map[string]string) []*LogBucket {
	var buckets []*LogBucket
	s.bucketsGroupMutex.RLock()
	defer s.bucketsGroupMutex.RUnlock()
	for i := range s.logBuckets {
		bucket := &s.logBuckets[i]
		match := true
		for label, value := range index {
			if value != bucket.index[label] {
				match = false
				break
			}
		}
		if match {
			buckets = append(buckets, bucket)
		}
	}
	return buckets
}

func (s *InMemoryLogStore) Push(log common.Log) {
	fmt.Println("Pushing log: ", log)
	var bucket *LogBucket
	{
		s.bucketsGroupMutex.RLock()
		bucket = s.findBucketsExactMatchUnsafe(log.Labels)
		s.bucketsGroupMutex.RUnlock()
	}

	fmt.Println("Bucket found: ", bucket)
	// Push and return if found
	if bucket != nil {
		fmt.Println("Found exact match bucket for key ", log.Labels)
		bucket.logSet.Push(log)
		return
	}

	bucket = s.addNewBucket(log.Labels)
	bucket.logSet.Push(log)
}

func (s *InMemoryLogStore) Query(labels map[string]string) []common.Log {
	s.bucketsGroupMutex.RLock()
	defer s.bucketsGroupMutex.RUnlock()
	var logs []common.Log
	for _, bucket := range s.FindBucketsIncludeIndex(labels) {
		logs = append(logs, bucket.logSet.Dump()...)
	}
	return logs
}

func (s *InMemoryLogStore) Dump() []common.Log {
	var logBuckets []LogBucket
	{
		s.bucketsGroupMutex.RLock()
		logBuckets = s.logBuckets
		s.bucketsGroupMutex.RUnlock()
	}
	var logs []common.Log
	for _, bucket := range logBuckets {
		logs = append(logs, bucket.logSet.Dump()...)
	}
	return logs
}

func (s *TenantedInMemoryStore) Push(log common.Log) {
	if _, ok := s.tenantedStores[log.TenantID]; !ok {
		s.tenantedMutex.Lock()
		if _, ok := s.tenantedStores[log.TenantID]; !ok {
			s.tenantedStores[log.TenantID] = NewInMemoryLogStore()
		}
		s.tenantedMutex.Unlock()
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
