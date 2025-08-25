package main

import (
	"fmt"
	"math/rand"
	"time"
)

func RandomIndexes(length int) []int {
	indexes := make([]int, length)
	for i := 0; i < length; i++ {
		indexes[i] = i
	}

	rand.New(rand.NewSource(time.Now().UnixNano()))
	rand.Shuffle(len(indexes), func(i, j int) {
		indexes[i], indexes[j] = indexes[j], indexes[i]
	})
	return indexes
}

type LabelIndex struct {
	labels           map[string]map[string]int // Lable Name -> Lable Value -> Index Bit
	availableIndexes map[string][]int          // Lable Name -> Available Indexes
}

func NewLabelIndex() *LabelIndex {
	return &LabelIndex{
		labels:           make(map[string]map[string]int),
		availableIndexes: make(map[string][]int),
	}
}

func (l *LabelIndex) addLabel(label string) {
	if _, ok := l.labels[label]; !ok {
		l.labels[label] = make(map[string]int)
		l.availableIndexes[label] = RandomIndexes(32)
	}
}

func (l *LabelIndex) addLabelValue(label string, value string) {
	if _, ok := l.labels[label]; !ok {
		l.addLabel(label)
	}
	if _, ok := l.labels[label][value]; !ok {
		nextIndex := l.availableIndexes[label][0]
		l.availableIndexes[label] = l.availableIndexes[label][1:]
		l.labels[label][value] = nextIndex
	}
}

func (l *LabelIndex) Dump() []string {
	messages := []string{}
	messages = append(messages, "LabelIndex:\n")
	for label, values := range l.labels {
		messages = append(messages, fmt.Sprintf("Label: %s\n", label))
		for value, index := range values {
			messages = append(messages, fmt.Sprintf("  Value: %s, Index: %d\n", value, index))
		}
	}
	return messages
}
