package main

import (
    "encoding/json"
    "fmt"
    "io/ioutil"
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