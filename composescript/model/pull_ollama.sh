#!/bin/bash

ollama serve &
# Record Process ID.
pid=$!

# Pause for Ollama to start.
sleep 5

echo "🔴 Retrieving model..."
ollama pull llama3.2

ollama pull deepseek-r1:1.5b

#ollama pull all-minilm
echo "🟢 Done!"

# Wait for Ollama process to finish.
wait $pid