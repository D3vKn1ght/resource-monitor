package main

import (
    "encoding/json"
    "fmt"
    "io/ioutil"
    "os"
    "time"

    "github.com/shirou/gopsutil/cpu"
    "github.com/shirou/gopsutil/mem"
    "github.com/shirou/gopsutil/disk"
    "github.com/shirou/gopsutil/host"
)

func ReadConfig(filename string) (map[string]interface{}, error) {
    file, err := os.Open(filename)
    if err != nil {
        return nil, err
    }
    defer file.Close()

    byteValue, err := ioutil.ReadAll(file)
    if err != nil {
        return nil, err
    }

    var config map[string]interface{}
    err = json.Unmarshal(byteValue, &config)
    if err != nil {
        return nil, err
    }

    return config, nil
}

func GetSystemInfo(my_config map[string]interface{}) (map[string]interface{}, error) {
    systemInfo := make(map[string]interface{})

    if my_config["cpu_info"].(bool) {
        cpuInfo := make(map[string]interface{})
        info, err := cpu.Info()
        if err != nil {
            return nil, err
        }
        cpuCores, err := cpu.Counts(true)
        if err != nil {
            return nil, err
        }
        cpuUsage, err := cpu.Percent(1*time.Second, false)
        if err != nil {
            return nil, err
        }
        cpuInfo["model"] = info[0].ModelName
        cpuInfo["cores"] = cpuCores
        cpuInfo["usage_percent"] = cpuUsage[0]
        systemInfo["cpu"] = cpuInfo
    }

    if my_config["memory_info"].(bool) {
        memoryInfo := make(map[string]interface{})
        vmStat, err := mem.VirtualMemory()
        if err != nil {
            return nil, err
        }
        memoryInfo["total_mb"] = vmStat.Total / 1024 / 1024
        memoryInfo["used_mb"] = vmStat.Used / 1024 / 1024
        memoryInfo["available_mb"] = vmStat.Available / 1024 / 1024
        memoryInfo["usage_percent"] = vmStat.UsedPercent
        systemInfo["memory"] = memoryInfo
    }

    if my_config["storage_info"].(bool) {
        storage := make(map[string]interface{})
        partitions, err := disk.Partitions(false)
        if err != nil {
            return nil, err
        }
        for _, partition := range partitions {
            usage, err := disk.Usage(partition.Mountpoint)
            if err != nil {
                return nil, err
            }
            storage[partition.Mountpoint] = map[string]interface{}{
                "total_gb": usage.Total / 1024 / 1024 / 1024,
                "used_gb":  usage.Used / 1024 / 1024 / 1024,
                "free_gb":  usage.Free / 1024 / 1024 / 1024,
                "usage_percent": usage.UsedPercent,
            }
        }
        systemInfo["storage"] = storage
    }

    hostStat, err := host.Info()
    if err != nil {
        return nil, err
    }
    systemInfo["os"] = hostStat.OS
    systemInfo["platform"] = hostStat.Platform
    systemInfo["architecture"] = hostStat.KernelArch

    return systemInfo, nil
}

func main() {
    config, err := ReadConfig("config.json")
    if err != nil {
        fmt.Printf("Lỗi khi đọc file config: %v\n", err)
        return
    }

    systemInfo, err := GetSystemInfo(config)
    if err != nil {
        fmt.Printf("Lỗi khi lấy thông tin hệ thống: %v\n", err)
        return
    }

    if cpuInfo, ok := systemInfo["cpu"].(map[string]interface{}); ok {
        fmt.Println("Thông tin CPU:")
        fmt.Printf("  Model: %s\n", cpuInfo["model"])
        fmt.Printf("  Số lõi: %d\n", cpuInfo["cores"])
        fmt.Printf("  Phần trăm sử dụng: %.2f%%\n", cpuInfo["usage_percent"])
    }

    if memoryInfo, ok := systemInfo["memory"].(map[string]interface{}); ok {
        fmt.Println("Thông tin bộ nhớ RAM:")
        fmt.Printf("  Tổng dung lượng: %v MB\n", memoryInfo["total_mb"])
        fmt.Printf("  Đã sử dụng: %v MB\n", memoryInfo["used_mb"])
        fmt.Printf("  Còn trống: %v MB\n", memoryInfo["available_mb"])
        fmt.Printf("  Phần trăm sử dụng: %.2f%%\n", memoryInfo["usage_percent"])
    }

    if storageInfo, ok := systemInfo["storage"].(map[string]interface{}); ok {
        fmt.Println("Thông tin các bộ nhớ lưu trữ:")
        for mountpoint, info := range storageInfo {
            diskInfo := info.(map[string]interface{})
            fmt.Printf("Mountpoint: %s\n", mountpoint)
            fmt.Printf("  Tổng dung lượng: %v GB\n", diskInfo["total_gb"])
            fmt.Printf("  Đã sử dụng: %v GB\n", diskInfo["used_gb"])
            fmt.Printf("  Còn trống: %v GB\n", diskInfo["free_gb"])
            fmt.Printf("  Phần trăm sử dụng: %.2f%%\n", diskInfo["usage_percent"])
        }
    }
}