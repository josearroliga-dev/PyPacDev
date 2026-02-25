# PyPacDev

A Python Pygame implementation of PacMan!

## Setup Instructions

To run this project, make sure you have Python installed. The project relies on external libraries which can loosely be thought of similarly to Node.js `package.json` dependencies. In Python, these are conventionally tracked in a `requirements.txt` file.

### 1. Install Dependencies
Run the following command in your terminal from the root folder of the project to install `pygame` and any other required packages:

```bash
pip install -r requirements.txt
```

### 2. Run the Game locally (Python)
Once your dependencies are installed, you can launch the game using:
```bash
python main.py
```

### 3. Run the Game in the Browser (Pygbag / WebAssembly)
This project is fully configured to compile natively to HTML5 WebAssembly so it can be played directly inside any web browser without needing Python installed!

To launch the local web server and play it in your browser:
```bash
python -m pygbag --disable-sound-format-error main.py
```
After running this command, open a web browser and navigate to `http://localhost:8000`.

### 4. Deploying to the Web (GitHub Pages)
This repository includes a fully-automated GitHub Actions workflow (`.github/workflows/main.yml`). 

Whenever you run a `git push` to the `main` or `master` branch, GitHub will automatically:
1. Compile your Pygame code into WebAssembly using `pygbag`.
2. Push the compiled website up to a special branch called `gh-pages`.

**To turn it on:**
Go to your GitHub Repository **Settings** -> **Pages**. Under "Source", select **Deploy from a branch**, and select the **`gh-pages`** branch. Save it. 

Your deployed game will be live permanently at your repository's GitHub Pages URL!
