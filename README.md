# PodAI: Autonomous Container Management

## Description
PodAI is an innovative project that combines AI decision-making with Docker container management. This system uses an AI model to autonomously manage, create, and optimize Docker containers, providing a unique approach to container orchestration and system administration.

## Features
- AI-driven decision making for container management
- Autonomous creation, modification, and deletion of Docker containers
- Self-set goals and memory of past actions
- RESTful API for interaction and monitoring
- Real-time logging of AI decisions and actions

## Prerequisites
- Python 3.7 or higher
- Docker
- Ollama (for running the AI model locally)

## Installation
1. Clone this repository:
   ```
   git clone https://github.com/yourusername/podai.git
   cd podai
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install fastapi uvicorn docker langchain_community ollama
   ```

4. Ensure Docker is running on your system.

5. Install Ollama and download the "qwen2" model:
   ```
   ollama pull qwen2
   ```

## Usage
1. Run the application:
   ```
   python podai.py
   ```

2. The AI will start making autonomous decisions about container management.

3. Interact with the system using the following API endpoints:
   - POST `/interact`: Trigger an immediate AI decision and action
   - GET `/system_state`: Get the current state of the Docker environment
   - GET `/ai_goals`: View the AI's current goals
   - GET `/ai_memory`: See the AI's recent memory of decisions and actions

## API Examples
1. Interact with the AI:
   ```
   curl -X POST http://localhost:8000/interact -H "Content-Type: application/json" -d '{"message": "What is the current state of the system?"}'
   ```

2. Get the current system state:
   ```
   curl http://localhost:8000/system_state
   ```

3. View AI's goals:
   ```
   curl http://localhost:8000/ai_goals
   ```

4. View AI's memory:
   ```
   curl http://localhost:8000/ai_memory
   ```

## Warning
This system gives significant autonomy to an AI in managing Docker containers. It's designed for experimental and educational purposes. Exercise caution when running it, especially in production environments.

## Contributing
Contributions to PodAI are welcome! Please feel free to submit pull requests, create issues or spread the word.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
