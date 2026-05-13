package handlers

import (
	"encoding/json"
	"net/http"
	"voltcare-api/services"
	"voltcare-api/config"
)

var validContractTypes = map[string]bool{
	"Suscripcion": true,
	"Pay-per-use": true,
}

var validServiceTypes = map[string]bool{
	"Correctivo Software": true,
	"Correctivo Mecanico": true,
	"Preventivo": true,
}

var validSeniorities = map[string]bool{
	"Junior": true,
	"Semi-Senior": true,
	"Senior": true,
}


type AnalyzeRequest struct {
	ContractType string  `json:"contract_type"`
	ServiceType  string  `json:"service_type"`
	Seniority    string  `json:"seniority"`
}

func AnalyzeHandler(w http.ResponseWriter, r *http.Request) {
	var req AnalyzeRequest
	err := json.NewDecoder(r.Body).Decode(&req); 
	
	if err != nil {
		WriteJSONError(w, "JSON inválido", http.StatusBadRequest)
		return
	}

	if req.ContractType != "" && !validContractTypes[req.ContractType] {
		WriteJSONError(w, "Tipo de contrato no válido", http.StatusBadRequest)
		return
	}

	if req.ServiceType != "" && !validServiceTypes[req.ServiceType] {
		WriteJSONError(w, "Tipo de servicio no válido", http.StatusBadRequest)
		return
	}

	if req.Seniority != "" && !validSeniorities[req.Seniority] {
		WriteJSONError(w, "Nivel de seniority no válido", http.StatusBadRequest)
		return
	}

	result, err := services.RunPythonScript(
		config.AppConfig.AnalyzeScript,
		req.ContractType,
		req.ServiceType,
		req.Seniority,
	)

	if err != nil {
		WriteJSONError(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(result)
}