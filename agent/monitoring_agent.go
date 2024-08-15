package main

import (
    "time"

    "github.com/shirou/gopsutil/cpu"
    "github.com/shirou/gopsutil/mem"
    "github.com/shirou/gopsutil/disk"
    "github.com/shirou/gopsutil/host"
)


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