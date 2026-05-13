package handlers

import (
	"encoding/json"
	"net/http"
	"voltcare-api/services"
	"voltcare-api/config"
)

func GenerateHandler(w http.ResponseWriter, r *http.Request) {

	result, err := services.RunPythonScript(
		config.AppConfig.GenerateScript,
	)

	if err != nil {
		WriteJSONError(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(result)
}