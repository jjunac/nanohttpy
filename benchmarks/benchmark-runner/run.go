package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"math"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/shirou/gopsutil/cpu"
	"github.com/shirou/gopsutil/host"
	"github.com/shirou/gopsutil/mem"
	"gopkg.in/yaml.v3"
)

func assertNoErr(err error) {
	if err != nil {
		panic(err)
	}
}

func FloatToInt64(x float64) int64 {
	return int64(math.Round(x))
}

func discoverBenchConfigs(todo []string) (configs []HttpBenchConfig) {
	configs = make([]HttpBenchConfig, 0)
	runAll := (len(todo) == 0)
	if runAll {
		log.Println("No argument provided, will run all")
	} else {
		log.Println("Only the following benchmark will be run:", todo)
	}
	todoSet := make(map[string]struct{}, 0)
	for _, arg := range todo {
		todoSet[arg] = struct{}{}
	}

	cfgFiles, err := filepath.Glob("./**/benchmark.yaml")
	assertNoErr(err)

	for _, cfgFile := range cfgFiles {
		cfgYaml, err := ioutil.ReadFile(cfgFile)
		assertNoErr(err)

		var benchConfigs struct {
			Benchmarks []HttpBenchConfig
		}
		err = yaml.Unmarshal(cfgYaml, &benchConfigs)
		assertNoErr(err)

		for _, cfg := range benchConfigs.Benchmarks {
			_, mustDo := todoSet[cfg.Name]
			if !runAll && !mustDo {
				continue
			}

			cfg.Dir = filepath.Dir(cfgFile)
			configs = append(configs, cfg)
		}
	}
	return
}

func main() {
	args := os.Args[1:]

	results := make([]HttpBenchResult, 0)
	configs := discoverBenchConfigs(args)

	// Find the longest name to adjust the log prefix size
	longestName := 0
	for _, cfg := range configs {
		if len(cfg.Name) > longestName {
			longestName = len(cfg.Name)
		}
	}
	prefixFmt := fmt.Sprintf("%%-%ds | ", longestName)

	for _, cfg := range configs {
		log.Default().SetPrefix(fmt.Sprintf(prefixFmt, cfg.Name))
		log.Printf("Config loaded: %+v", cfg)

		bench := NewHttpBench(&cfg, []HttpBenchStage{
			{"Warmup", 8, 10 * time.Second, false},
			{"Load test", 8, 10 * time.Second, true},
		})
		res, ok := bench.Run(ApiHello())

		if ok {
			results = append(results, res...)
		}

		log.Default().SetPrefix("")
	}

	if len(results) == 0 {
		fmt.Println("No benchmark found")
		return
	}

	log.Print("#################### Global results ####################\n\n")

	hostInfo, _ := host.Info()
	cpuInfo, _ := cpu.Info()
	memInfo, _ := mem.VirtualMemory()
	fmt.Println("System information:")
	fmt.Println("OS: ", strings.Title(hostInfo.Platform), hostInfo.PlatformVersion, "Kernel", strings.Title(hostInfo.OS), hostInfo.KernelVersion, hostInfo.KernelArch)
	fmt.Println("CPU:", cpuInfo[0].Cores, "X", cpuInfo[0].ModelName)
	fmt.Println("RAM:", memInfo.Total/(1024*1024*1024), "GB")
	fmt.Println()

	table := make([][]string, len(results))
	for i, result := range results {
		floatToStr := func(x float64) string {
			return fmt.Sprintf("%.3f", x)
		}
		table[i] = []string{
			strings.ReplaceAll(result.Name, " ", "_"),
			floatToStr(float64(result.Operations) / result.ExecTime.Seconds()),
			floatToStr(float64(result.ExecTime.Microseconds()/result.Operations) / 1000),
			floatToStr(float64(result.MaxRSS) / 1024),
		}
	}
	maxWidth := make([]int, len(table[0]))
	for i := range table {
		for j := range table[i] {
			if width := len(table[i][j]); width > maxWidth[j] {
				maxWidth[j] = width
			}
		}
	}

	rowFmt := fmt.Sprintf("%%-%ds    %%%ds req/s    %%%ds ms/req    RSS: %%%ds MB\n", maxWidth[0], maxWidth[1], maxWidth[2], maxWidth[3])
	for _, row := range table {
		fmt.Printf(rowFmt, row[0], row[1], row[2], row[3])
	}
}
