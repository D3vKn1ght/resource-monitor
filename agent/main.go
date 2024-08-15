package main

import (
    "fmt"
)



func main() {
    configFile := "config.json"
    
    config, err := ReadConfig(configFile)
    if err != nil {
        fmt.Printf("Lỗi khi đọc file config: %v\n", err)
        return
    }

    err = CheckAndCreateID(config, configFile)
    if err != nil {
        fmt.Printf("Lỗi khi tạo ID: %v\n", err)
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