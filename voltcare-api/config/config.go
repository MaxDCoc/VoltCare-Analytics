package config

import (
	"os"
	"log"
	"github.com/joho/godotenv"
)

type Config struct {
	Port string
	AnalyzeScript string
	GenerateScript string
	VenvPython string
}

var AppConfig Config

func LoadConfig() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file")
	}

	AppConfig = Config{
		Port:           os.Getenv("PORT"),
		AnalyzeScript: "/app/notebooks/data_analysis.py",
		GenerateScript: "/app/notebooks/data_generator.py",
		VenvPython:    "python3",
	}
}