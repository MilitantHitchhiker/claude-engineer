# 🤖 Prometheus

Prometheus is an advanced implementation of a multi-model AI assistant with enhanced capabilities and modular architecture. It provides an interactive command-line interface (CLI) that leverages various AI models from providers like Anthropic, OpenAI, and Groq to assist with software development tasks and more.

## ✨ Features

- 💬 Interactive chat interface with multiple AI models (Claude, GPT-4, Mixtral, etc.)
- 🖥️ Code Interpreter: Execute Python code within conversations
- 🖼️ Image Support: Upload and process images during interactions
- 🚀 Automode: Autonomous task completion with iterative goal-setting
- 🧩 Modular Architecture: Improved code organization and maintainability
- 📁 File system operations (create folders, files, read/write files)
- 🔍 Web search capabilities using Tavily API
- 🌈 Syntax highlighting for code snippets
- 🏗️ Project structure creation and management
- 🧐 Code analysis and improvement suggestions
- 🔢 Token tracking: Monitor and display token usage statistics
- 🗃️ Vector database integration with Qdrant for context retrieval
- 🔄 Flexible AI provider selection (Anthropic, OpenAI, Groq)
- ⚙️ Flexible Configuration: Use of .env file and JSON for easy configuration management

## 🛠️ Installation

1. Clone this repository:
   ```
   git clone https://github.com/MilitantHitchhiker/claude-engineer.git
   cd claude-engineer
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your .env file:
   Create a .env file in the root directory and add your API keys:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   GROQ_API_KEY=your_groq_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

4. Install and run Qdrant:
   Follow the installation instructions for Qdrant at https://qdrant.tech/documentation/install/

## 🚀 Usage

Run the main script to start the Claude Engineer interface:

```
python main.py
```

Once started, you can interact with Claude Engineer by typing your queries or commands. Some example interactions:

- "Create a new Python project structure for a web application"
- "Explain the code in file.py and suggest improvements"
- "Search for the latest best practices in React development"
- "Help me debug this error: [paste your error message]"
- "Analyze this image and describe what you see"

### Special commands:
- Type 'exit' to end the conversation and close the application.
- Type 'image' to include an image in your message.
- Type 'automode [number]' to enter Autonomous mode with a specific number of iterations.
- Type 'token' to see the token usage summary.
- Type 'model' to change the current AI model.
- Press Ctrl+C at any time to exit the automode to return to regular chat.

### 🤖 Automode

Automode allows Claude Engineer to work autonomously on complex tasks. When in automode:

1. The AI sets clear, achievable goals based on your request.
2. It works through these goals one by one, using available tools as needed.
3. The AI provides regular updates on its progress.
4. Automode continues until goals are completed, the maximum number of iterations is reached, or the maximum token limit is reached.

To use automode:
1. Type 'automode [number]' when prompted for input.
2. Provide your request when prompted.
3. The AI will work autonomously, providing updates after each iteration.
4. Automode exits when the task is completed, after reaching the maximum number of iterations, or after reaching the maximum token limit.

## ⚙️ Configuration

Adjust the `models.json` file to customize the behavior of the AI assistant:

- Model configurations for different providers (Anthropic, OpenAI, Groq)
- Text models, vision models, and audio models specifications
- Capabilities, context windows, and other model-specific parameters

You can also modify the `.env` file to set environment variables:

- `MAX_CONTINUATION_ITERATIONS`: Maximum iterations for automode (default: 10)
- `MAX_CONTINUATION_TOKENS`: Maximum total tokens for automode (default: 50000)
- `CONTINUATION_EXIT_PHRASE`: Phrase to exit automode (default: "AUTOMODE_COMPLETE")
- Color configurations for different output types

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.