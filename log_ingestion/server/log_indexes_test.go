package main

import (
	"testing"
)

func TestLabelIndex_AddLabelValue(t *testing.T) {

	t.Run("AddLabelValue_SingleLableType", func(t *testing.T) {
		l := &LabelIndex{
			labels:           make(map[string]map[string]int),
			availableIndexes: make(map[string][]int),
		}
		l.addLabel("app")
		l.addLabelValue("app", "api")
		l.addLabelValue("app", "web")
		l.addLabelValue("app", "worker")
		t.Log(l.Dump())
	})

	t.Run("AddLabelValue_MultiLableType", func(t *testing.T) {
		l := &LabelIndex{
			labels:           make(map[string]map[string]int),
			availableIndexes: make(map[string][]int),
		}
		l.addLabel("app")
		l.addLabel("env")
		l.addLabelValue("app", "api")
		l.addLabelValue("app", "web")
		l.addLabelValue("app", "worker")
		l.addLabelValue("env", "prod")
		l.addLabelValue("env", "dev")
		l.addLabelValue("env", "test")
		t.Log(l.Dump())
	})
}
