package main

import (
	"fmt"
	"net/http"
	"voltcare-api/handlers"
	"voltcare-api/config"
)

func healthHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintln(w, "API funcionando")
}

func main() {
	config.LoadConfig()
	http.HandleFunc("/health", healthHandler)
	http.HandleFunc("/analyze", handlers.AnalyzeHandler)
	http.HandleFunc("/generate", handlers.GenerateHandler)

	fmt.Println("Servidor corriendo en http://localhost:" +config.AppConfig.Port)
	http.ListenAndServe(":" +config.AppConfig.Port, nil,)
}