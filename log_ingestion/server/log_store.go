package main

import (
	"fmt"
	"log_ingestion/common"
)

/*
LogBucket
*/
type LogBucket struct {
	logs  []common.Log
	index map[string]string
}

func NewLogBucket() *LogBucket {
	return &LogBucket{
		logs:  []common.Log{},
		index: map[string]string{},
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
	logBuckets []LogBucket
}

func NewInMemoryLogStore() *InMemoryLogStore {
	return &InMemoryLogStore{
		logBuckets: []LogBucket{},
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
		bucket.logs = append(bucket.logs, log)
		return
	}

	fmt.Println("Creating new bucket for key ", log.Labels)
	bucket = NewLogBucket()
	bucket.index = log.Labels
	bucket.logs = append(bucket.logs, log)
	s.logBuckets = append(s.logBuckets, *bucket)
}

func (s *InMemoryLogStore) Query(labels map[string]string) []common.Log {
	var logs []common.Log
	for _, bucket := range s.FindBucketsMatchLabels(labels) {
		logs = append(logs, bucket.logs...)
	}
	return logs
}

func (s *InMemoryLogStore) Dump() []common.Log {
	var logs []common.Log
	for _, bucket := range s.logBuckets {
		logs = append(logs, bucket.logs...)
	}
	return logs
}
