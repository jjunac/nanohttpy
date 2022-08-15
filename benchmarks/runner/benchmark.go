package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"os/exec"
	"runtime"
	"strings"
	"syscall"
	"time"
)

type HttpBenchConfig struct {
	Name    string
	Command []string
	Port    int
	Env     []string
	Dir     string
}

type HttpBenchStage struct {
	Name            string
	ParallelClients int
	Duration        time.Duration
	KeepResults     bool
}

type HttpBenchResult struct {
	Name       string
	ExecTime   time.Duration
	Operations int64
	MaxRSS     int64
}

type HttpBench struct {
	Cfg            *HttpBenchConfig
	Stages         []HttpBenchStage
	StartupTimeout time.Duration
	cmd            *exec.Cmd
	client         *http.Client
}

func NewHttpBench(cfg *HttpBenchConfig, stages []HttpBenchStage) *HttpBench {
	transport := *http.DefaultTransport.(*http.Transport) // We de-ref the interface to have a copy
	transport.MaxIdleConns = 0
	transport.MaxIdleConnsPerHost = 100000
	transport.MaxConnsPerHost = 0

	return &HttpBench{
		Cfg:            cfg,
		Stages:         stages,
		StartupTimeout: 5 * time.Second,
		client:         &http.Client{Transport: &transport},
	}
}

func (b *HttpBench) startServer() {
	log.Print("Starting server with command ", b.Cfg.Command, "...")
	b.cmd = exec.Command(b.Cfg.Command[0], b.Cfg.Command[1:]...)
	b.cmd.Dir = b.Cfg.Dir
	b.cmd.Env = append(b.cmd.Env, b.Cfg.Env...)
	// b.cmd.Stdout = os.Stdout
	// b.cmd.Stderr = os.Stderr
	b.cmd.Start()
}

func (b *HttpBench) stopServer() {
	if b.cmd.Process == nil {
		log.Print("Server is already stopped")
		return
	}
	log.Print("Gracefully stopping server...")
	b.cmd.Process.Signal(os.Interrupt)
	timer := time.AfterFunc(3*time.Second, func() {
		log.Print("Server is taking too long, killing it !")
		b.cmd.Process.Kill()
	})
	_ = b.cmd.Wait()
	timer.Stop()
	log.Print("Server stopped")
}

func (b *HttpBench) parallelExec(n int, execTime time.Duration, f func(id int) bool) HttpBenchResult {
	starts := make(chan struct{}, n)
	stops := make(chan struct{}, n)
	results := make(chan int64, n)

	worker := func(id int, start <-chan struct{}, stop <-chan struct{}, result chan<- int64) {
		count := int64(0)
		<-start
	mainLoop:
		for {
			select {
			case <-stop:
				break mainLoop
			default:
				if f(id) {
					count++
				}
			}
		}
		result <- count
	}

	//  Create the workers
	for i := 0; i < n; i++ {
		go worker(i, starts, stops, results)
	}
	// Run the workers
	for i := 0; i < n; i++ {
		starts <- struct{}{}
	}
	startExec := time.Now()
	endExec := <-time.After(execTime)
	// Stop the workers
	for i := 0; i < n; i++ {
		stops <- struct{}{}
	}
	actualExecTime := endExec.Sub(startExec)
	// Aggregate the results
	total := int64(0)
	for i := 0; i < n; i++ {
		total += <-results
	}

	return HttpBenchResult{
		ExecTime:   actualExecTime,
		Operations: total,
	}
}

func (b *HttpBench) fire(url string) (body []byte, ok bool) {
	res, err := http.Get(url)
	if err != nil {
		return []byte{}, false
	}
	defer res.Body.Close()
	body, err = ioutil.ReadAll(res.Body)
	ok = (err == nil)
	return
}

func (b *HttpBench) Run(testCase *TestCase) (results []HttpBenchResult, ok bool) {
	b.startServer()

	url := fmt.Sprint("http://127.0.0.1:", b.Cfg.Port, testCase.Route)

	// Wait for server readiness + check Reply
	ready := func() bool {
		timeout := time.After(b.StartupTimeout)
		tick := time.Tick(500 * time.Millisecond)
		for {
			select {
			case <-timeout:
				// TODO: print output
				log.Println("The server is taking too long to start")
				return false
			case <-tick:

				if body, ok := b.fire(url); ok {
					if strings.TrimSpace(string(body)) == testCase.Expected {
						log.Println("Response validation passed")
						return true
					}
					log.Printf("Invalid response received:\n  Actual  : %s\n  Expected: %s\n", string(body), testCase.Expected)
					return false
				}
			}
		}
	}()
	ok = ready
	if ready {
		log.Println("Starting the benchmark...")

		for _, stage := range b.Stages {
			log.Printf("#################### Starting stage %s ####################", stage.Name)
			log.Printf("Will shoot with %d clients for %s", stage.ParallelClients, stage.Duration)
			result := b.parallelExec(stage.ParallelClients, stage.Duration, func(id int) bool {
				_, ok := b.fire(url)
				return ok
			})
			result.Name = b.Cfg.Name
			log.Printf(
				"Results: %d requets processed in %s (%f req/s)\n",
				result.Operations,
				result.ExecTime,
				float64(result.Operations)/result.ExecTime.Seconds(),
			)
			if stage.KeepResults {
				results = append(results, result)
			}
		}
	}

	b.stopServer()

	if b.cmd.ProcessState != nil {
		// NOTE: Unfortunately, it's difficult to get the max RSS in real time for each stage in a portable way (/proc)
		//       doesn't exists on MacOS. So for now we're just setting the final MaxRSS for every stage.
		maxRSS := b.cmd.ProcessState.SysUsage().(*syscall.Rusage).Maxrss
		// Contrary to Linux, on MacOS the MaxRSS is in **bytes**, see `man getrusage`
		if runtime.GOOS == "darwin" {
			maxRSS /= 1024
		}
		for i := range results {
			results[i].MaxRSS = maxRSS
		}
	}

	return
}
