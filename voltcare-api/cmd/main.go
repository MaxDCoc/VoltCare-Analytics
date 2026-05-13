package main

import (
	"fmt"
	"net/http"
	"voltcare-api/handlers"
)

func healthHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintln(w, "API funcionando")
}

func main() {
	http.HandleFunc("/health", healthHandler)
	http.HandleFunc("/analyze", handlers.AnalyzeHandler)
	http.HandleFunc("/generate", handlers.GenerateHandler)

	fmt.Println("Servidor corriendo en http://localhost:8080")
	http.ListenAndServe(":8080", nil)
}