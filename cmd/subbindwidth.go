package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os/exec"
	"strconv"
	"strings"
	"sync"
	"time"

	"golang.org/x/time/rate"
)

// 模拟用户流量数据
var userInfo = struct {
	upload   int64
	download int64
	total    int64
	expire   int64
}{
	upload:   303456789,
	download: 987654321,
	total:    10 * 1024 * 1024 * 1024, // 10 GB
	expire:   1735689200,              // Unix 时间戳（例如：2024-12-31）
}
var cookieHostdare, cookieVmiss string
var urlp string
var browserLock = new(sync.Mutex)
var limiterHostdare = rate.NewLimiter(rate.Every(5*time.Minute), 1)
var limiterVmiss = rate.NewLimiter(rate.Every(5*time.Minute), 1)

// 模拟的 Clash 订阅内容（YAML 格式）
const clashConfig = `
proxies:
proxy-groups:
rules:
`

// 处理订阅请求
func subHandler(w http.ResponseWriter, r *http.Request) {
	if !limiterHostdare.Allow() {
		w.WriteHeader(http.StatusTooManyRequests)
		w.Write([]byte(`{"msg":"Too Many Requests"}`))
		return
	}
	browserLock.Lock()
	defer browserLock.Unlock()
	// 模拟每次请求都增加一点 download 流量
	// userInfo.download += 1024 * 1024                      // +1MB 每次请求
	userInfo.expire = time.Now().AddDate(0, 0, 30).Unix() // 30天后过期
	b, i, o := GETWebDataCurl(urlp, cookieHostdare)
	// 设置响应头中的流量信息
	w.Header().Set("Content-Type", "application/x-yaml")
	w.Header().Set("subscription-userinfo",
		fmt.Sprintf("upload=%d; download=%d; total=%d; expire=%d",
			int64(i),
			int64(o),
			int64(b),
			userInfo.expire))

	// 输出 Clash 配置
	_, _ = fmt.Fprint(w, clashConfig)
}
func subHandlerJP(w http.ResponseWriter, r *http.Request) {
	if !limiterVmiss.Allow() {
		w.WriteHeader(http.StatusTooManyRequests)
		w.Write([]byte(`{"msg":"Too Many Requests"}`))
		return
	}
	browserLock.Lock()
	defer browserLock.Unlock()
	// 模拟每次请求都增加一点 download 流量
	// userInfo.download += 1024 * 1024                      // +1MB 每次请求
	userInfo.expire = time.Now().AddDate(0, 0, 30).Unix() // 30天后过期
	b, i, o := GETWebVmissDataCurl(cookieVmiss)
	// 设置响应头中的流量信息
	w.Header().Set("Content-Type", "application/x-yaml")
	w.Header().Set("subscription-userinfo",
		fmt.Sprintf("upload=%d; download=%d; total=%d; expire=%d",
			int64(i),
			int64(o),
			int64(b),
			userInfo.expire))

	// 输出 Clash 配置
	_, _ = fmt.Fprint(w, clashConfig)
}

func RunClashFlow() {
	http.HandleFunc("/sub/hostdare/los", subHandler)
	http.HandleFunc("/sub/vmiss/jp", subHandlerJP)

	fmt.Println("启动订阅服务在 http://localhost:8080")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		panic(err)
	}
}

func GETWebDataCurl(urlp, cookie string) (float64, float64, float64) {
	cmdName := "/bin/bash"
	cmdArgs := []string{"./scripts/readHostdare.sh"}
	cmdjq := "/usr/bin/jq"
	cmdjqArgs := []string{".bandwidth | {limit,used}"}

	cmd1 := exec.Command(cmdName, cmdArgs...)
	cmd2 := exec.Command(cmdjq, cmdjqArgs...)
	cmd2.Stdin, _ = cmd1.StdoutPipe()
	// cmd2.Stdout = os.Stdout
	// cmd2.Stderr = os.Stderr
	if err := cmd1.Start(); err != nil {
		fmt.Println("cmd1 run err: ", err)
	}
	output, err := cmd2.Output()
	if err != nil {
		fmt.Println("output err: ", err)
		return 0, 0, 0
	}
	if err := cmd1.Wait(); err != nil {
		fmt.Println("cmd1 wait err: ", err)
	}
	var data struct {
		Bandwidth float64 `json:"limit"`
		In        float64 `json:"total_in"`
		Out       float64 `json:"used"`
	}
	fmt.Println("hostdare output: ", string(output))
	err = json.Unmarshal(output, &data)
	if err != nil {
		fmt.Println("unmarshal err: ", err)
		return 0, 0, 0
	}
	// b, _ := strconv.ParseFloat(data.Bandwidth, 64)
	// i, _ := strconv.ParseFloat(data.In, 64)
	// o, _ := strconv.ParseFloat(data.Out, 64)
	return data.Bandwidth * 1024 * 1024, data.In * 1024 * 1024, data.Out * 1024 * 1024
}
func GETWebVmissDataCurl(cookie string) (float64, float64, float64) {
	cmdName := "/bin/bash"
	cmdArgs := []string{"./scripts/readVmiss.sh"}
	cmdjq := "/usr/bin/jq"
	cmdjqArgs := []string{". | {trafficUsed,trafficTotal}"}

	cmd1 := exec.Command(cmdName, cmdArgs...)
	cmd2 := exec.Command(cmdjq, cmdjqArgs...)
	cmd2.Stdin, _ = cmd1.StdoutPipe()
	if err := cmd1.Start(); err != nil {
		fmt.Println("cmd1 run err: ", err)
	}
	output, err := cmd2.Output()
	if err != nil {
		fmt.Println("output err: ", err)
		return 0, 0, 0
	}
	if err := cmd1.Wait(); err != nil {
		fmt.Println("cmd1 wait err: ", err)
	}
	var data struct {
		Bandwidth  float64 `json:"trafficTotal"`
		Used       string  `json:"trafficUsed"`
		UsedFormat float64
	}
	fmt.Println("vmiss output: ", string(output))
	err = json.Unmarshal(output, &data)
	if err != nil {
		fmt.Println("unmarshal err: ", err)
		return 0, 0, 0
	}
	unit := strings.Split(data.Used, " ")
	if len(unit) < 2 {
		return 0, 0, 0
	}
	// fmt.Println("data.used: ", unit)
	d, _ := strconv.ParseFloat(unit[0], 64)
	switch unit[1] {
	case "GB":
		data.UsedFormat = d * 1024 * 1024 * 1024
	case "MB":
		data.UsedFormat = d * 1024 * 1024
	case "KB":
		data.UsedFormat = d * 1024
	default:
		data.UsedFormat = d
	}
	return data.Bandwidth * 1024 * 1024 * 1024, 0, data.UsedFormat
}
