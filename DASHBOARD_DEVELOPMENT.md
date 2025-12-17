# Dashboard Frontend Development Guide

## 📁 **Files to Edit**

Your friend needs to work with these files in the `dashboard/` directory:

### **Core Files (Main Editing)**

```
dashboard/
├── src/
│   ├── App.jsx          ⭐ MAIN FILE - All dashboard logic & UI
│   ├── App.css          🎨 Dashboard-specific styles
│   ├── index.css        🎨 Global styles, theme, animations
│   └── main.jsx         ⚙️  Entry point (rarely needs editing)
├── index.html           📄 HTML template (edit title, meta tags)
├── package.json         📦 Dependencies (add new libraries here)
└── vite.config.js       ⚙️  Build config (rarely needs editing)
```

---

## 🎯 **What Each File Does**

### **1. `src/App.jsx`** ⭐ **MOST IMPORTANT**
**Purpose**: Main dashboard component with all UI and logic

**What's inside**:
- Data loading from `ai_analysis.json`
- Summary cards (total vulnerabilities, false positives, etc.)
- Interactive charts (pie chart, bar chart)
- Vulnerability table with sorting
- Search and filter functionality
- Export to CSV feature

**Edit this to**:
- Change layout and structure
- Add/remove components
- Modify data display
- Add new features
- Change interactions

**Key sections**:
```jsx
// Line ~50-100: Data loading and state management
const [data, setData] = useState(null);

// Line ~150-200: Summary cards
<Card>Total Vulnerabilities: {summary.total_vulnerabilities}</Card>

// Line ~250-300: Charts
<PieChart data={chartData} />

// Line ~350-450: Vulnerability table
<TableContainer>...</TableContainer>
```

---

### **2. `src/index.css`** 🎨 **GLOBAL STYLES**
**Purpose**: Global styling, theme colors, animations

**What's inside**:
- CSS variables for colors
- Dark theme definitions
- Glassmorphism effects
- Animations (fade-in, slide-up)
- Responsive breakpoints

**Edit this to**:
- Change color scheme
- Modify dark theme
- Add new animations
- Adjust spacing/sizing
- Change fonts

**Key sections**:
```css
/* Line 1-30: CSS Variables */
:root {
  --primary-color: #6366f1;
  --background: #0a0a0a;
}

/* Line 50-80: Glassmorphism */
.glass {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
}

/* Line 100-150: Animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

---

### **3. `src/App.css`** 🎨 **COMPONENT STYLES**
**Purpose**: Styles specific to App.jsx components

**What's inside**:
- Dashboard-specific classes
- Card styles
- Chart container styles
- Table styles

**Edit this to**:
- Fine-tune component appearance
- Add component-specific styles
- Override Material-UI defaults

---

### **4. `index.html`** 📄 **HTML TEMPLATE**
**Purpose**: Base HTML, meta tags, title

**Edit this to**:
- Change page title
- Add meta descriptions
- Include external fonts
- Add favicon

```html
<head>
  <title>AI-Driven DevSecOps Dashboard</title>
  <meta name="description" content="Security vulnerability analysis dashboard">
</head>
```

---

### **5. `package.json`** 📦 **DEPENDENCIES**
**Purpose**: Project dependencies and scripts

**Edit this to**:
- Add new npm packages
- Update existing packages
- Modify build scripts

**Current dependencies**:
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "@mui/material": "^5.14.0",
    "recharts": "^2.8.0"
  }
}
```

---

## 🚀 **Development Workflow**

### **Setup (First Time)**

```bash
# Navigate to dashboard
cd dashboard

# Install dependencies
npm install

# Start development server
npm run dev

# Dashboard opens at: http://localhost:5173
```

### **Making Changes**

1. **Edit files** in `src/` directory
2. **Save** - Changes auto-reload in browser
3. **Test** - Check in browser
4. **Commit** when satisfied

### **Building for Production**

```bash
# Build optimized version
npm run build

# Output goes to: dashboard/dist/
```

---

## 🎨 **Common Customizations**

### **Change Colors**

**File**: `src/index.css`

```css
:root {
  --primary-color: #6366f1;     /* Change to your color */
  --secondary-color: #8b5cf6;   /* Change to your color */
  --background: #0a0a0a;        /* Change background */
}
```

### **Modify Summary Cards**

**File**: `src/App.jsx` (around line 150-200)

```jsx
<Card>
  <CardContent>
    <Typography variant="h6">
      Total Vulnerabilities  {/* Edit text */}
    </Typography>
    <Typography variant="h3">
      {summary.total_vulnerabilities}  {/* Edit data */}
    </Typography>
  </CardContent>
</Card>
```

### **Add New Chart**

**File**: `src/App.jsx`

```jsx
import { LineChart, Line } from 'recharts';

// Add in render section
<LineChart data={yourData}>
  <Line dataKey="value" stroke="#8884d8" />
</LineChart>
```

### **Change Table Columns**

**File**: `src/App.jsx` (around line 350-400)

```jsx
<TableHead>
  <TableRow>
    <TableCell>ID</TableCell>
    <TableCell>Title</TableCell>
    {/* Add new column */}
    <TableCell>Your New Column</TableCell>
  </TableRow>
</TableHead>
```

---

## 📚 **Technologies Used**

### **React** (UI Framework)
- Component-based architecture
- Hooks for state management
- Learn: https://react.dev

### **Material-UI** (Component Library)
- Pre-built components (Cards, Tables, etc.)
- Theming system
- Learn: https://mui.com

### **Recharts** (Charts Library)
- Pie charts, bar charts, line charts
- Responsive and customizable
- Learn: https://recharts.org

### **Vite** (Build Tool)
- Fast development server
- Hot module replacement
- Learn: https://vitejs.dev

---

## 🔧 **File Structure Explained**

```
dashboard/
├── public/              # Static files
│   └── data/           # JSON data files
│       └── ai_analysis.json  # Vulnerability data
│
├── src/                # Source code
│   ├── App.jsx         # Main component ⭐
│   ├── App.css         # Component styles
│   ├── index.css       # Global styles
│   └── main.jsx        # Entry point
│
├── dist/               # Built files (after npm run build)
│   ├── index.html
│   └── assets/
│
├── index.html          # HTML template
├── package.json        # Dependencies
├── vite.config.js      # Build config
└── README.md          # Documentation
```

---

## 💡 **Tips for Your Friend**

### **Start Small**
1. Change colors in `index.css`
2. Modify text in `App.jsx`
3. Adjust card layout
4. Then tackle bigger changes

### **Use Browser DevTools**
- Right-click → Inspect
- See live CSS changes
- Debug React components

### **Hot Reload**
- Changes appear instantly
- No need to refresh browser
- Saves time during development

### **Component Structure**
```jsx
// App.jsx is organized like this:
function App() {
  // 1. State and data loading
  // 2. Helper functions
  // 3. Render UI
  return (
    <div>
      {/* Summary Cards */}
      {/* Charts */}
      {/* Table */}
    </div>
  );
}
```

---

## 🎯 **Quick Reference**

### **Want to change...**

| What | File | Line Range |
|------|------|------------|
| **Colors** | `index.css` | 1-30 |
| **Summary cards** | `App.jsx` | 150-200 |
| **Charts** | `App.jsx` | 250-300 |
| **Table** | `App.jsx` | 350-450 |
| **Animations** | `index.css` | 100-150 |
| **Page title** | `index.html` | 5-10 |
| **Fonts** | `index.css` | 40-50 |

---

## 🐛 **Troubleshooting**

### **Changes not showing?**
- Hard refresh: `Ctrl + F5`
- Clear cache
- Restart dev server

### **Build errors?**
```bash
# Delete node_modules and reinstall
rm -rf node_modules
npm install
```

### **Port already in use?**
```bash
# Kill existing process
Get-Process -Name node | Stop-Process -Force

# Or use different port
npm run dev -- --port 3000
```

---

## 📖 **Learning Resources**

### **React Basics**
- Official Tutorial: https://react.dev/learn
- React Hooks: https://react.dev/reference/react

### **Material-UI**
- Components: https://mui.com/material-ui/getting-started/
- Customization: https://mui.com/material-ui/customization/theming/

### **CSS**
- Flexbox: https://css-tricks.com/snippets/css/a-guide-to-flexbox/
- Grid: https://css-tricks.com/snippets/css/complete-guide-grid/

---

## ✅ **Checklist for Your Friend**

Before starting:
- [ ] Node.js installed (v18+)
- [ ] Code editor ready (VS Code recommended)
- [ ] Git installed
- [ ] Repository cloned

First steps:
- [ ] Run `npm install` in dashboard folder
- [ ] Run `npm run dev`
- [ ] Open http://localhost:5173
- [ ] Make a small change to test

---

## 🚀 **After Editing**

### **Test Locally**
```bash
npm run dev
# Check at http://localhost:5173
```

### **Build for Production**
```bash
npm run build
# Creates optimized files in dist/
```

### **Deploy**
```bash
git add .
git commit -m "feat: Update dashboard design"
git push origin main
# Vercel auto-deploys!
```

---

**Your friend has everything needed to customize the dashboard!** 🎨

**Main file to focus on**: `src/App.jsx` - This is where 90% of changes happen!
