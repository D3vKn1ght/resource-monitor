package main

import (
    "fmt"
    "os"
    "runtime"
    "strconv"
    "syscall"

    "github.com/shirou/gopsutil/cpu"
    "github.com/shirou/gopsutil/mem"
    "github.com/shirou/gopsutil/disk"
)

func GetSystemInfo() (map[string]interface{}, error) {
    systemInfo := make(map[string]interface{})

    // Lấy thông tin về CPU
    cpuInfo, err := cpu.Info()
    if err != nil {
        return nil, err
    }
    cpuCores, err := cpu.Counts(true)
    if err != nil {
        return nil, err
    }
    systemInfo["cpu_model"] = cpuInfo[0].ModelName
    systemInfo["cpu_cores"] = cpuCores

    // Lấy thông tin về RAM
    vmStat, err := mem.VirtualMemory()
    if err != nil {
        return nil, err
    }
    systemInfo["total_ram_mb"] = vmStat.Total / 1024 / 1024
    systemInfo["used_ram_mb"] = vmStat.Used / 1024 / 1024
    systemInfo["available_ram_mb"] = vmStat.Available / 1024 / 1024

    // Lấy thông tin về bộ nhớ
    diskStat, err := disk.Usage("/")
    if err != nil {
        return nil, err
    }
    systemInfo["total_disk_gb"] = diskStat.Total / 1024 / 1024 / 1024
    systemInfo["used_disk_gb"] = diskStat.Used / 1024 / 1024 / 1024
    systemInfo["free_disk_gb"] = diskStat.Free / 1024 / 1024 / 1024

    // Lấy thông tin về hệ điều hành và kiến trúc
    systemInfo["os"] = runtime.GOOS
    systemInfo["architecture"] = runtime.GOARCH

    // Lấy thông tin về bộ nhớ ảo
    pageSize := os.Getpagesize()
    var stat syscall.Sysinfo_t
    err = syscall.Sysinfo(&stat)
    if err != nil {
        return nil, err
    }
    systemInfo["total_virtual_memory_mb"] = strconv.FormatUint(uint64(stat.Totalram)*uint64(pageSize)/1024/1024, 10)

    return systemInfo, nil
}

func main() {
    systemInfo, err := GetSystemInfo()
    if err != nil {
        fmt.Printf("Lỗi khi lấy thông tin hệ thống: %v\n", err)
        return
    }

    // In ra các giá trị trong map
    for key, value := range systemInfo {
        fmt.Printf("%s: %v\n", key, value)
    }
}
