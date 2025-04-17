# runZero MCP Server with Claude Desktop

This guide walks you through setting up and running the runZero MCP server (`run.py`) using Claude Desktop (or any MCP-supported client) as the front-end.

---

## 📋 Prerequisites

- Python 3.8+ installed on your system
- `python3`, `pip`, and virtualenv (optional but recommended)
- `git` for cloning the repository
- [Claude Desktop](https://claude.ai/desktop) or another MCP client
- A runZero Export API token and Organization ID

---

## 🚀 Setup Steps

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-folder>
   ```

2. **Prepare the `.env` file**
   - Copy the example:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your credentials:
     ```dotenv
     RUNZERO_EXPORT_TOKEN=<your_export_token>
     RUNZERO_ORG_TOKEN=<your_org_token>
     RUNZERO_ORG_ID=<your_organization_id>
     ```

3. **Install Python dependencies**
   ```bash
   python3 -m venv .venv        # create a virtual environment (optional)
   source .venv/bin/activate    # activate it
   pip install -r requirements.txt
   ```

4. **Verify your Python paths**
   ```bash
   which python3        # e.g. /usr/local/bin/python3
   which pip            # should match your python3 venv
   ```

5. **Locate your `run.py` script**
   ```bash
   pwd                   # full path to this folder
   ls -l run.py           # confirm file exists
   ```

6. **Configure Claude Desktop**

   Create or update `claude_desktop_config.json` with an entry for your MCP server. For example:
   ```json
   {
     "mcpServers": {
       "runZero MCP": {
         "command": "/Users/tyler/.local/share/virtualenvs/runZero-scripts-VoSeJ_A1/bin/python3",
         "args": ["/Users/tyler/git/runZero-scripts/mcp/run.py"],
         "enabled": true
       }
     }
   }
   ```

   - **`command`**: full path to the `python3` executable.
   - **`args`**: array containing the path to `run.py`.
   - **`enabled`**: set to `true` to activate this server in Claude Desktop.

7. **Start the MCP server in Claude Desktop**
   - Launch Claude Desktop, select the **runZero MCP** server, and click **Connect**.
   - In the logs pane, you should see:
     ```text
     Initializing server…
     Server started and connected successfully
     ```

8. **Run searches via the client**
   - In the Claude prompt, call your tools:
     ```txt
     searchAssets("os:linux AND alive:t")
     searchServices("protocol:ssh AND alive:t")
     ```
   - Results will return raw CSV under a `csv` field:
     ```json
     {
       "csv": "id,organization,site,...\n1,AcmeCorp,SiteA,...\n..."
     }
     ```

---

## 🔧 Customization

- **`queries.csv`**: contains your curated query library. Place it in the same folder or adjust the path in `run.py`.
- **Logging**: All server messages print to `stderr` for easy debugging in Claude Desktop.
- **Override invalid keys**: use `ignore_invalid=True` in `searchAssets` / `searchServices` to bypass field validation.

---

## 📝 Troubleshooting

- **Missing tokens**: ensure `.env` is in the working directory and loaded by `python-dotenv`.
- **Permission errors**: check file permissions on `run.py` (`chmod +x run.py`).
- **Client fails to connect**: verify `command` and `args` paths in `claude_desktop_config.json`.

---

*Last updated: April 17, 2025*

