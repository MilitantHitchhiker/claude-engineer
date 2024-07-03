# 🤖 Claude Engineer

Claude Engineer is an advanced implementation of a Claude-based AI assistant with enhanced capabilities and modular architecture. It provides an interactive command-line interface (CLI) that leverages the power of Anthropic's Claude-3.5-Sonnet model to assist with software development tasks.

## ✨ Features

- 💬 Interactive chat interface with Claude-3.5-Sonnet
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
- ⚙️ Flexible Configuration: Use of .env file for easy configuration management

## 🛠️ Installation

1. Clone this repository:
   ```
   git clone https://github.com/MilitantHitchhiker/claude-engineer.git
   cd claude-engineer
   ```

2. Switch to the Prometheus branch:
   ```
   git checkout Prometheus
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your .env file:
   Create a .env file in the root directory and add your API keys:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

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

### Special commands:
- Type 'exit' to end the conversation and close the application.
- Type 'image' to include an image in your message.
- Type 'CODE' to execute Python code.
- Type 'automode [number]' to enter Autonomous mode with a specific number of iterations.
- Type 'token' to see the token usage summary.
- Press Ctrl+C at any time to exit the automode to return to regular chat.

### 🤖 Automode

Automode allows Claude to work autonomously on complex tasks. When in automode:

1. Claude sets clear, achievable goals based on your request.
2. It works through these goals one by one, using available tools as needed.
3. Claude provides regular updates on its progress.
4. Automode continues until goals are completed, the maximum number of iterations is reached, or the maximum token limit is reached.

To use automode:
1. Type 'automode [number]' when prompted for input.
2. Provide your request when prompted.
3. Claude will work autonomously, providing updates after each iteration.
4. Automode exits when the task is completed, after reaching the maximum number of iterations, or after reaching the maximum token limit.

Note: Claude will only have access to the files in the root folders of the script or any folder path you provide it.

## ⚙️ Configuration

Adjust the `.env` file to customize the behavior of the AI assistant:

- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `TAVILY_API_KEY`: Your Tavily API key
- `MODEL_NAME`: The Claude model to use (default: "claude-3.5-sonnet-20240620")
- `MAX_TOKENS`: Maximum number of tokens per response (default: 4000)
- `MAX_CONTINUATION_ITERATIONS`: Maximum iterations for automode (default: 10)
- `MAX_CONTINUATION_TOKENS`: Maximum total tokens for automode (default: 40000)
- `CONTINUATION_EXIT_PHRASE`: Phrase to exit automode (default: "AUTOMODE_COMPLETE")

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Doriandarko/claude-engineer&type=Date)](https://star-history.com/#Doriandarko/claude-engineer&Date)