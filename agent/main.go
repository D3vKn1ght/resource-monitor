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
	domain, _ := config["domain"]

	systemInfo, err := GetSystemInfo(config)
	if err != nil {
		fmt.Printf("Lỗi khi lấy thông tin hệ thống: %v\n", err)
		return
	}
	systemInfo["id"], _ = config["id"]

	fmt.Println(systemInfo)

	err = SendSystemInfo(domain.(string), systemInfo)
	if err != nil {
		fmt.Printf("Error sending system info: %v\n", err)
	}
}
