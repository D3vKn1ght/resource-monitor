package main

import (
	"fmt"
	"time"
)

func main() {
	configFile := "config.json"
	for {
		fmt.Println("Đọc file config")
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
		domain, _ := config["domain"]

		fmt.Println("Lấy thông tin hệ thống")
		systemInfo, err := GetSystemInfo(config)
		if err != nil {
			fmt.Printf("Lỗi khi lấy thông tin hệ thống: %v\n", err)
			return
		}

		systemInfo["id"], _ = config["id"]

		fmt.Println(systemInfo)

		fmt.Println("Gửi thông tin hệ thống")
		go sendSystemInfoAsync(domain.(string), systemInfo)

		fmt.Println("Chờ 1 phút")
		time.Sleep(1 * time.Minute)
	}
}

