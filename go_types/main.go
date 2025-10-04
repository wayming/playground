package main

import "fmt"

func main() {
	var s = "测试"
	fmt.Println(s)
	fmt.Printf("len: %d\n", len(s))
	fmt.Printf("%c,%c,%c\n", s[0], s[1], s[2])
}
