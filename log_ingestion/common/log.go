package common

type Log struct {
	TenantID  string            `json:"tenant_id"`
	Labels    map[string]string `json:"labels"`
	Timestamp int64             `json:"timestamp"`
	Line      string            `json:"line"`
}
