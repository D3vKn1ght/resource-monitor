package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"

	"github.com/google/uuid"
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

func SaveConfig(filename string, config map[string]interface{}) error {
	data, err := json.MarshalIndent(config, "", "  ")
	if err != nil {
		return err
	}

	err = ioutil.WriteFile(filename, data, 0644)
	if err != nil {
		return err
	}

	return nil
}

func CheckAndCreateID(config map[string]interface{}, filename string) error {
	id, exists := config["id"]
	if !exists || id == nil || len(id.(string)) == 0 {
		newID := uuid.New().String()
		config["id"] = newID
		fmt.Printf("Tạo ID mới: %s\n", newID)
		return SaveConfig(filename, config)
	}

	fmt.Printf("ID hiện tại: %s\n", id)
	return nil
}

func SendSystemInfo(domain string, systemInfo map[string]interface{}) error {
	jsonData, err := json.Marshal(systemInfo)
	if err != nil {
		return err
	}
	var url string = domain + "/send-system-info/"

	resp, err := http.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("Failed to send system info, status code: %d", resp.StatusCode)
	}

	fmt.Println("System info sent successfully")
	return nil
}

func sendSystemInfoAsync(domain string, systemInfo map[string]interface{}) {
	err := SendSystemInfo(domain, systemInfo)
	if err != nil {
		fmt.Printf("Error sending system info: %v\n", err)
	}
}
