# Agent Development Kit Demo

This project demonstrates the use of Google's Agent Development Kit (ADK) to create specialized AI agents for different tasks. The project includes multiple agents, each with specific capabilities and tools, organized in a modular structure.

## Project Structure

```
POC/
├── src/
│   ├── agent_team/             # Main agent team implementation
│   │   ├── core_utils/         # Shared utilities for the agent team
│   │   │   └── util.py         # Utility functions including logging setup
│   │   ├── tools_util/         # Tools and utilities for agents
│   │   │   └── __init__.py     # Tool implementations (weather, greetings, etc.)
│   │   └── agent.py            # Main agent definitions and configurations
│   │
│   ├── stock_advisor_workflow/  # Stock advisor agent implementation
│   │   ├── core_utils/         # Shared utilities for stock advisor
│   │   │   └── util.py         # Utility functions
│   │   ├── subagents/          # Subagents for the stock advisor
│   │   └── agent.py            # Stock advisor agent definition
│   │
│   └── weather_time_tool_agent/ # Weather and time agent
│       ├── core_utils/         # Shared utilities for weather agent
│       │   └── util.py         # Utility functions
│       └── agent.py            # Weather and time agent definition
│
├── pyproject.toml             # Project configuration and dependencies
└── README.md                  # This file
```

## Features

### 1. Agent Team
- **Weather Agent**: Provides weather information for specific cities
- **Greeting Agent**: Handles simple greetings and introductions
- **Farewell Agent**: Manages conversation conclusions and goodbyes

### 2. Stock Advisor Workflow
- Specialized agent for stock market information and advice
- Uses parallel processing for efficient information retrieval
- Includes subagents for different analysis tasks

### 3. Weather & Time Tool Agent
- Provides current weather information for any city
- Displays current time in different timezones
- Uses DuckDuckGo search for real-time data

## Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) package manager

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ankitdubey987/Google-ADK-Learning.git
   cd "Google-ADK-Learning/Agent Development Kit Demo/POC"
   ```

2. Install dependencies using `uv`:
   ```bash
   uv sync  # Creates a virtual environment and installs all dependencies
   ```

## Running the Agents

### Using uv run (recommended)

```bash
# Run Agent Team
uv run agent_team

# Run Stock Advisor
uv run stock_agent

# Run Weather & Time Agent
uv run weather_agent
```

## Configuration

- The project uses environment variables for configuration. Create a `.env` file in the root directory with any necessary API keys and configurations.
- Logging is configured in each agent's respective `core_utils/util.py` file.

## Project Commands

- `uv sync` - Install/update dependencies
- `uv run agent_team` - Start the Agent Team
- `uv run stock_agent` - Start the Stock Advisor
- `uv run weather_agent` - Start the Weather & Time Agent

## Recent Changes

- Reorganized project structure to use `src` directory
- Added support for `uv` package manager
- Created console entry points for easier execution
- Moved `core_utils` package to individual agent script folders for better modularity
- Updated logging to use lazy % formatting for better performance
- Standardized model configurations across agents
- Added proper error handling and logging

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.