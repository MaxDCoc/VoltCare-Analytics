package handlers

import (
	"encoding/json"
	"net/http"
	"voltcare-api/services"
)

type AnalyzeRequest struct {
	ContractType string  `json:"contract_type"`
	ServiceType  string  `json:"service_type"`
	Seniority    string  `json:"seniority"`
}

func AnalyzeHandler(w http.ResponseWriter, r *http.Request) {
	var req AnalyzeRequest
	err := json.NewDecoder(r.Body).Decode(&req); 
	
	if err != nil {
		http.Error(w, "JSON inválido", 400)
		return
	}

	result, err := services.RunPythonScript(
		"C:\\Users\\asus\\Desktop\\4to\\proyectos\\VoltCare-Analytics\\VoltCare-Analytics\\notebooks\\data_analysis.py",
		req.ContractType,
		req.ServiceType,
		req.Seniority,
	)

	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(result)
}