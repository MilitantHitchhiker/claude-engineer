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
- 🖼️ Vision capabilities support via terminal drag and drop of images

## 🛠️ Installation

1. Clone this repository:
   ```
   git clone https://github.com/Doriandarko/claude-engineer.git
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

4. Set up your API keys:
   - Add your Anthropic and Tavily API keys in the `config.json` file:
     ```json
     {
       "anthropic_api_key": "YOUR_ANTHROPIC_API_KEY",
       "tavily_api_key": "YOUR_TAVILY_API_KEY"
     }
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

Special commands:
- Type 'exit' to end the conversation and close the application.
- Type 'image' to include an image in your message.
- Type 'CODE' to execute Python code.
- Type 'automode' plus the max amount of iterations to enter Autonomous mode.
- Press Ctrl+C at any time to exit the automode to return to regular chat.

### 🤖 Automode

Automode allows Claude to work autonomously on complex tasks. When in automode:

1. Claude sets clear, achievable goals based on your request.
2. It works through these goals one by one, using available tools as needed.
3. Claude provides regular updates on its progress.
4. Automode continues until goals are completed or the maximum number of iterations is reached.

To use automode:
1. Type 'automode' when prompted for input.
2. Provide your request when prompted.
3. Claude will work autonomously, providing updates after each iteration.
4. Automode exits when the task is completed or after reaching the maximum number of iterations.

Note: Claude will only have access to the files in the root folders of the script or any folder path you provide it.

## ⚙️ Configuration

Adjust the `config.json` file to customize the behavior of the AI assistant:

- `anthropic_api_key`: Your Anthropic API key
- `tavily_api_key`: Your Tavily API key
- `model`: The GPT model to use (e.g., "claude-3.5-sonnet")
- `use_code_interpreter`: Set to `true` to enable the code interpreter feature

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Doriandarko/claude-engineer&type=Date)](https://star-history.com/#Doriandarko/claude-engineer&Date)