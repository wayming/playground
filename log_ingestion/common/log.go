package common

import (
	"fmt"
	"sync"
)

type Log struct {
	TenantID  string            `json:"tenant_id"`
	Labels    map[string]string `json:"labels"`
	Timestamp int64             `json:"timestamp"`
	Line      string            `json:"line"`
}

type LogSafe struct {
	logs     []Log
	logMutex sync.RWMutex
}

func NewLogSafe() *LogSafe {
	return &LogSafe{
		logs:     []Log{},
		logMutex: sync.RWMutex{},
	}
}

func (s *LogSafe) Push(log Log) {
	s.logMutex.Lock()
	fmt.Println("Pushing log: ", log)
	fmt.Println("before: ", s.logs)
	s.logs = append(s.logs, log)
	fmt.Println("after: ", s.logs)
	s.logMutex.Unlock()
}

func (s *LogSafe) Dump() []Log {
	s.logMutex.RLock()
	logs := s.logs
	s.logMutex.RUnlock()
	return logs
}

func (s *LogSafe) Query(query string) []Log {
	s.logMutex.RLock()
	logs := s.logs
	s.logMutex.RUnlock()
	return logs
}
