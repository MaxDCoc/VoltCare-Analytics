package handlers

import (
	"encoding/json"
	"net/http"
	"voltcare-api/services"
)

func GenerateHandler(w http.ResponseWriter, r *http.Request) {

	result, err := services.RunPythonScript(
		"C:\\Users\\asus\\Desktop\\4to\\proyectos\\VoltCare-Analytics\\VoltCare-Analytics\\notebooks\\data_generator.py",
	)

	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(result)
}