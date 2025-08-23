// simple go web server hello world
package main

import (
	"fmt"
	"io"
	"net/http"
)

/*
{
  "streams": [
    {
      "stream": {
        "app": "nginx",
        "env": "prod"
      },
      "values": [
        ["1732000000000000000", "GET /index.html 200 OK"],
        ["1732000001000000000", "GET /login 302 Redirect"]
      ]
    }
  ]
}
*/
func push_log_handler(w http.ResponseWriter, r *http.Request) {
	body, err := io.ReadAll(r.Body)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		return
	}
	fmt.Println(string(body))
	w.WriteHeader(http.StatusOK)
}

// curl -X POST http://localhost:8080/api/v1/push -H "Content-Type: application/json" -d '{"streams":[{"stream":{"app":"nginx","env":"prod"},"values":[["1732000000000000000","GET /index.html 200 OK"],["1732000001000000000","GET /login 302 Redirect"]]}}}'
func main() {
    http.HandleFunc("/api/v1/push", push_log_handler)
    http.ListenAndServe(":8080", nil)
}
