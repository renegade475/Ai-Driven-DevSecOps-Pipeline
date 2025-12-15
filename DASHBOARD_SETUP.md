# Dashboard Setup - Manual Steps

## Issue
Node.js is installed but not in your PowerShell PATH. Here's how to fix it:

## Solution: Add Node.js to PATH

### Option 1: Restart PowerShell (Easiest)
1. Close your current PowerShell window
2. Open a **new** PowerShell window
3. Navigate back to the dashboard directory:
   ```powershell
   cd C:\Users\notan\Documents\GitHub\Ai-Driven-DevSecOps-Pipeline\dashboard
   ```
4. Run:
   ```powershell
   npm install
   npm run dev
   ```

### Option 2: Add to PATH Manually
1. Press `Win + X` and select "System"
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "User variables", select "Path" and click "Edit"
5. Click "New" and add: `C:\Program Files\nodejs`
6. Click OK on all windows
7. Restart PowerShell and try again

### Option 3: Use Full Path (Quick Test)
```powershell
& "C:\Program Files\nodejs\npm.cmd" install
& "C:\Program Files\nodejs\npm.cmd" run dev
```

## After npm install succeeds

You'll see the dashboard at: **http://localhost:5173**

The dashboard will show:
- 📊 **5 Total Vulnerabilities**
- 🔴 **2 Critical Priority**
- 🟠 **2 High Priority**  
- 📈 **Charts and visualizations**
- 🔍 **Filtering and search**
- 📥 **CSV export**

## Alternative: View JSON Results

If you prefer not to set up the dashboard right now, you can:

1. **Open the JSON file**:
   ```powershell
   code C:\Users\notan\Documents\GitHub\Ai-Driven-DevSecOps-Pipeline\results\ai_analysis.json
   ```

2. **Key sections to review**:
   - `summary`: Overall statistics
   - `top_priorities`: Most critical vulnerabilities
   - `filtered_vulnerabilities`: All real vulnerabilities with details
   - Each vulnerability includes:
     - Risk score
     - Priority level
     - Remediation guidance
     - Code examples
     - SLA days

## For Your Presentation

You can use:
1. ✅ The JSON report (already generated)
2. ✅ Screenshots of the workflow runs from GitHub
3. ✅ The AI engine console output showing the analysis
4. ✅ The dashboard (once npm install works)

**The core AI-Driven DevSecOps Pipeline is fully functional!** 🎉
