package services

import (
	"encoding/json"
	"os/exec"
	"errors"
)

func RunPythonScript(scriptPath string, args ...string) (map[string]interface{}, error) {

	commandArgs := append([]string{scriptPath}, args...)

	cmd := exec.Command("python", commandArgs...)
	
	output, err := cmd.CombinedOutput()

	if err != nil {
		return nil, errors.New(string(output))
	}

	var result map[string]interface{}

	err = json.Unmarshal(output, &result)
	if err != nil {
		return nil, err
	}

	return result, nil
}