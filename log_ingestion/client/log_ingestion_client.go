package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strconv"
	"sync"
	"time"

	"log_ingestion/common"
)

type LogClient struct {
	baseURL    string
	httpClient *http.Client
	counter    int
	mutex      sync.Mutex
}

func NewLogClient(baseURL string, timeout time.Duration) *LogClient {
	return &LogClient{
		baseURL: baseURL,
		httpClient: &http.Client{
			Timeout: timeout,
		},
		counter: 0,
	}
}

func (c *LogClient) Push(log common.Log) error {
	jsonData, err := json.Marshal(log)
	if err != nil {
		return err
	}

	req, err := http.NewRequest("POST", c.baseURL+"/api/v1/push", bytes.NewReader(jsonData))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("User-Agent", "log-ingestion-client")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}
	c.mutex.Lock()
	c.counter++
	fmt.Printf("Log pushed: %d\n", c.counter)
	c.mutex.Unlock()
	return nil
}

func (c *LogClient) Dump() ([]common.Log, error) {
	req, err := http.NewRequest("GET", c.baseURL+"/api/v1/dump", nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("User-Agent", "log-ingestion-client")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	var logs []common.Log
	err = json.Unmarshal(body, &logs)
	if err != nil {
		return nil, err
	}

	fmt.Printf("%d logs dumped\n", len(logs))
	return logs, nil
}

func push_stream(logClient *LogClient, tenantID string, streamID int, logCount int, streamDone chan bool) {
	fmt.Printf("Pushing logs for tenant: %s stream: %d, logs: %d\n", tenantID, streamID, logCount)
	for i := 0; i < logCount; i++ {
		logClient.Push(common.Log{
			TenantID:  tenantID,
			Labels:    map[string]string{"app": "api", "env": Labels[i%len(Labels)]},
			Timestamp: time.Now().UnixNano() / 1e6, // ms
			Line:      "GET /login 200 OK",
		})
	}
	streamDone <- true
}

func push_tenant(logClient *LogClient, tenantID string, streamCount int, logCount int, done chan bool) {
	fmt.Printf("Pushing logs for tenant: %s\n", tenantID)
	streamDone := make(chan bool)
	for i := 0; i < streamCount; i++ {
		go push_stream(logClient, tenantID, i, logCount, streamDone)
	}
	for i := 0; i < streamCount; i++ {
		<-streamDone
	}
	done <- true
}

var Labels []string = []string{
	"prod",
	"dev",
	"test",
}

/*
-api Push | Dump
-tenants <count>
-streams <count>
-logs <count>
*/
func usage(error string) {
	fmt.Println("Usage: log_ingestion_client -api Push | Dump -tenants <count> -streams <count> -logs <count>")
	fmt.Println("-tenants <count>         - Number of tenants")
	fmt.Println("-streams <count>         - Number of streams per tenant")
	fmt.Println("-logs <count>            - Number of logs per stream")
	fmt.Println("-api <Push | Dump>       - API to call")
	if error != "" {
		fmt.Println(error)
	}
	os.Exit(1)
}

func main() {
	api := ""
	tenants := 1
	streams := 1
	logs := 1
	baseURL := "http://localhost:8080"
	timeout := time.Second
	for idx := 1; idx < len(os.Args); idx++ {
		arg := os.Args[idx]
		if arg == "-api" {
			idx++
			api = os.Args[idx]
			if api != "Push" && api != "Dump" {
				usage("api must be Push or Dump")
			}
		} else if arg == "-tenants" {
			idx++
			tenants, _ = strconv.Atoi(os.Args[idx])
			if tenants < 1 {
				usage("tenants must be greater than 0")
			}
		} else if arg == "-streams" {
			idx++
			streams, _ = strconv.Atoi(os.Args[idx])
			if streams < 1 {
				usage("streams must be greater than 0")
			}
		} else if arg == "-logs" {
			idx++
			logs, _ = strconv.Atoi(os.Args[idx])
			if logs < 1 {
				usage("logs must be greater than 0")
			}
		} else {
			usage("unknown argument: " + arg)
		}
	}

	fmt.Printf("Pushing logs for %d tenants, %d streams per tenant, %d logs per stream\n", tenants, streams, logs)
	logClient := NewLogClient(baseURL, timeout)
	if api == "Push" {
		done := make(chan bool)
		for i := 0; i < tenants; i++ {
			go push_tenant(logClient, fmt.Sprintf("team-%d", i), streams, logs, done)
		}
		for i := 0; i < tenants; i++ {
			<-done
			fmt.Printf("%d tenants done\n", i+1)
		}
	} else if api == "Dump" {
		logClient.Dump()
	}
}
