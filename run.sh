#!/bin/bash
until curl -s http://ollama:11434/v1/models | grep -q "mistral"; do
    echo "Waiting for Ollama model to be ready..."
    sleep 5
done
echo "Ollama is ready with the model loaded!"

python  web_ui.py
