package main

import (
	"fmt"
	"sync"

	"log_ingestion/common"
)

type BucketIndex struct {
	labelsToLevel map[string]int
	mutex         sync.Mutex
	root          *LableIndexNode
}

func NewBucketIndex() *BucketIndex {
	return &BucketIndex{
		labelsToLevel: make(map[string]int),
		root:          NewLableIndexNode(""),
	}
}

func (h *BucketIndex) AddLabel(label string) {
	if _, ok := h.labelsToLevel[label]; !ok {
		h.mutex.Lock()
		defer h.mutex.Unlock()
		if _, ok := h.labelsToLevel[label]; !ok {
			h.labelsToLevel[label] = len(h.labelsToLevel)
			h.root.Extend(label)
		}
	}
}

func (h *BucketIndex) AddLableSet(labels map[string]string) {
	for label, _ := range labels {
		h.AddLabel(label)
	}
}

const DEFAULT_BUCKET_NAME = "log_ingestion_default_bucket"

type LableIndexNode struct {
	label      string
	logsBucket []common.Log
	children   map[string]*LableIndexNode
}

func NewLableIndexNode(label string) *LableIndexNode {
	return &LableIndexNode{
		label:      label,
		logsBucket: []common.Log{},
		children:   make(map[string]*LableIndexNode),
	}
}

// Recursively search and extend the leaf node with another level
func (n *LableIndexNode) Extend(label string) {

	// if leaf node, extend to the next level and move the bucket to a default child node
	if len(n.children) == 0 {
		n.label = label
		n.children[DEFAULT_BUCKET_NAME] = NewLableIndexNode(label)

		// Move log bucket to default bucket
		n.children[DEFAULT_BUCKET_NAME].logsBucket = n.logsBucket
		n.logsBucket = []common.Log{}
	} else {
		// if not leaf node, search the next level
		for _, child := range n.children {
			child.Extend(label)
		}
	}
}

func (n *LableIndexNode) IsLeaf() bool {
	return len(n.children) == 0 || n.label == ""
}

func (n *LableIndexNode) Push(log common.Log) {
	// If leaf node, push to the bucket
	if n.IsLeaf() {
		n.logsBucket = append(n.logsBucket, log)
		return
	}

	// If not leaf node, push to the next level
	childKey := DEFAULT_BUCKET_NAME
	if _, ok := log.Labels[n.label]; ok {
		childKey = log.Labels[n.label]
	}

	// Push to the children
	if _, ok := n.children[childKey]; !ok {
		n.children[childKey] = NewLableIndexNode("")
	}
	n.children[childKey].Push(log)
}

func (n *LableIndexNode) Dump(path string) []string {
	if n.IsLeaf() {
		return []string{fmt.Sprintf("%s: %d logs", path, len(n.logsBucket))}
	}

	messages := []string{}
	for childKey, child := range n.children {
		messages = append(messages, child.Dump(path+"/"+childKey)...)
	}
	return messages
}
