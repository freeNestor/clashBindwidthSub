// package main

// func main() {
// 	collectCounter()
// 	runPromHttp()
// }

package main

import (
	"os"
	"sync"
)

var (
	is sync.Map
	sc = make(chan os.Signal, 1)
)

func main() {
	RunClashFlow()
}
