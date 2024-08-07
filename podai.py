import asyncio
import docker
import json
import logging
from typing import Dict, Any, List
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from langchain_community.llms import Ollama
from datetime import datetime

# Set up logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app for API endpoints and Docker client for container operations
app = FastAPI(title="Autonomous AI Container Manager")
docker_client = docker.from_env()

class AutonomousAI:
    def __init__(self, model_name: str = "qwen2"):
        # Initialize the AI model using Ollama
        self.llm = Ollama(model=model_name)
        # Store recent decisions and actions
        self.memory: List[Dict[str, Any]] = []
        # Store AI's current goals
        self.goals: List[str] = []
        # Dispatch dictionary for mapping actions to methods
        self.action_dispatch = {
            "create_container": self.create_container,
            "delete_container": self.delete_container,
            "modify_container": self.modify_container,
            "set_goal": self.set_goal,
            "list_containers": self.list_containers,
            "get_container_logs": self.get_container_logs,
            "execute_in_container": self.execute_in_container
        }

    async def think(self) -> Dict[str, Any]:
        # Get current system state
        system_state = await self.get_system_state()
        # Prepare recent memory and goals for the AI prompt
        memory_str = json.dumps(self.memory[-10:]) if self.memory else "No previous actions"
        goals_str = "\n".join(self.goals) if self.goals else "No specific goals set"

        # Construct the prompt for the AI
        prompt = f"""
        You are an autonomous AI responsible for managing a Docker container environment.
        Your goal is to optimize the system, create interesting projects, and maintain a well-organized container ecosystem.

        Current system state:
        {json.dumps(system_state, indent=2)}

        Recent memory:
        {memory_str}

        Current goals:
        {goals_str}

        Based on the current state, your memory, and goals, decide on the next action to take.
        You can create, modify, or delete containers, set new goals, or perform any Docker-related operation.
        Be creative, but also maintain system stability and efficiency.

        Respond with a JSON object containing:
        1. "thought_process": Your reasoning for the decision
        2. "action": The action to perform (e.g., "create_container", "set_goal", "modify_container", etc.)
        3. "parameters": Any parameters needed for the action
        4. "explanation": A user-friendly explanation of your decision

        Remember, you have full control over the container environment. Be innovative!
        """

        # Invoke the AI model to make a decision
        response = await self.llm.ainvoke(prompt)
        try:
            decision = json.loads(response)
            # Store the decision in memory
            self.memory.append({"timestamp": datetime.now().isoformat(), "decision": decision})
            return decision
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON response from AI: {response}")
            return {"thought_process": "Error in decision making", "action": "none", "parameters": {}, "explanation": "There was an error in processing the AI's response."}

    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        # Use the dispatch dictionary to call the appropriate method
        action_function = self.action_dispatch.get(action)
        if action_function:
            return await action_function(**parameters)
        else:
            return {"error": f"Unknown action: {action}"}

    async def get_system_state(self) -> Dict[str, Any]:
        # Retrieve current state of Docker environment
        containers = docker_client.containers.list(all=True)
        return {
            "containers": [{"id": c.id[:12], "name": c.name, "status": c.status, "image": c.image.tags} for c in containers],
            "images": [img.tags for img in docker_client.images.list()],
            "networks": [net.name for net in docker_client.networks.list()],
            "volumes": [vol.name for vol in docker_client.volumes.list()]
        }

    async def create_container(self, name: str, image: str, **kwargs) -> Dict[str, Any]:
        # Create a new Docker container
        container = docker_client.containers.run(image, name=name, detach=True, **kwargs)
        return {"message": f"Container created: {container.name} ({container.id[:12]})"}

    async def delete_container(self, name: str) -> Dict[str, Any]:
        # Delete a Docker container
        container = docker_client.containers.get(name)
        container.remove(force=True)
        return {"message": f"Container deleted: {name}"}

    async def modify_container(self, name: str, **kwargs) -> Dict[str, Any]:
        # Modify a Docker container's properties
        container = docker_client.containers.get(name)
        container.update(**kwargs)
        return {"message": f"Container modified: {name}"}

    def set_goal(self, goal: str) -> Dict[str, Any]:
        # Set a new goal for the AI
        self.goals.append(goal)
        return {"message": f"New goal set: {goal}"}

    async def list_containers(self) -> Dict[str, Any]:
        # List all Docker containers
        containers = docker_client.containers.list(all=True)
        return {"containers": [{"id": c.id[:12], "name": c.name, "status": c.status} for c in containers]}

    async def get_container_logs(self, name: str, lines: int = 50) -> Dict[str, Any]:
        # Retrieve logs from a specific container
        container = docker_client.containers.get(name)
        logs = container.logs(tail=lines).decode('utf-8')
        return {"logs": logs}

    async def execute_in_container(self, name: str, command: str) -> Dict[str, Any]:
        # Execute a command inside a specific container
        container = docker_client.containers.get(name)
        result = container.exec_run(command)
        return {"exit_code": result.exit_code, "output": result.output.decode('utf-8')}

# Create an instance of the AutonomousAI
ai_manager = AutonomousAI()

async def ai_loop():
    # Main loop for autonomous AI operations
    while True:
        try:
            # AI makes a decision
            decision = await ai_manager.think()
            logger.info(f"AI Decision: {json.dumps(decision, indent=2)}")
            if decision['action'] != 'none':
                # Execute the decided action
                result = await ai_manager.execute_action(decision['action'], decision['parameters'])
                logger.info(f"Action Result: {json.dumps(result, indent=2)}")
            # Wait for 1 minute before next decision
            await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"Error in AI loop: {str(e)}")
            # Wait before retrying in case of error
            await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
    # Start the AI loop when the application starts
    asyncio.create_task(ai_loop())

class UserInput(BaseModel):
    # Pydantic model for user input validation
    message: str

@app.post("/interact")
async def interact_with_ai(user_input: UserInput):
    # Endpoint for user interaction with the AI
    decision = await ai_manager.think()
    result = await ai_manager.execute_action(decision['action'], decision['parameters'])
    return {
        "ai_thought_process": decision['thought_process'],
        "ai_action": decision['action'],
        "ai_explanation": decision['explanation'],
        "action_result": result
    }

@app.get("/system_state")
async def get_system_state():
    # Endpoint to retrieve current system state
    return await ai_manager.get_system_state()

@app.get("/ai_goals")
async def get_ai_goals():
    # Endpoint to retrieve AI's current goals
    return {"goals": ai_manager.goals}

@app.get("/ai_memory")
async def get_ai_memory():
    # Endpoint to retrieve AI's recent memory
    return {"memory": ai_manager.memory}

if __name__ == "__main__":
    # Run the FastAPI application
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
