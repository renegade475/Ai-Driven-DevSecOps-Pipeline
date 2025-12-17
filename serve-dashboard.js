const http = require('http');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const PORT = 3000;
const DASHBOARD_DIR = path.join(__dirname, 'dashboard', 'dist');
const AI_ANALYSIS_PATH = path.join(__dirname, 'results', 'ai_analysis.json');

// MIME types
const mimeTypes = {
    '.html': 'text/html',
    '.js': 'text/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpg',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon'
};

const server = http.createServer((req, res) => {
    console.log(`${req.method} ${req.url}`);

    // Serve ai_analysis.json from results directory
    if (req.url === '/data/ai_analysis.json') {
        if (fs.existsSync(AI_ANALYSIS_PATH)) {
            const content = fs.readFileSync(AI_ANALYSIS_PATH);
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(content);
        } else {
            res.writeHead(404);
            res.end('AI analysis file not found');
        }
        return;
    }

    // Serve static files from dist directory
    let filePath = path.join(DASHBOARD_DIR, req.url === '/' ? 'index.html' : req.url);

    const extname = String(path.extname(filePath)).toLowerCase();
    const contentType = mimeTypes[extname] || 'application/octet-stream';

    fs.readFile(filePath, (error, content) => {
        if (error) {
            if (error.code === 'ENOENT') {
                // File not found, serve index.html for SPA routing
                fs.readFile(path.join(DASHBOARD_DIR, 'index.html'), (err, content) => {
                    if (err) {
                        res.writeHead(500);
                        res.end('Error loading dashboard');
                    } else {
                        res.writeHead(200, { 'Content-Type': 'text/html' });
                        res.end(content, 'utf-8');
                    }
                });
            } else {
                res.writeHead(500);
                res.end('Server Error: ' + error.code);
            }
        } else {
            res.writeHead(200, { 'Content-Type': contentType });
            res.end(content, 'utf-8');
        }
    });
});

server.listen(PORT, () => {
    const url = `http://localhost:${PORT}`;
    console.log('\n========================================');
    console.log('🚀 AI-Driven DevSecOps Dashboard');
    console.log('========================================');
    console.log(`✅ Server running at: ${url}`);
    console.log('✅ Dashboard ready!');
    console.log('\nPress Ctrl+C to stop the server');
    console.log('========================================\n');

    // Automatically open browser
    const start = process.platform === 'darwin' ? 'open' :
        process.platform === 'win32' ? 'start' : 'xdg-open';
    exec(`${start} ${url}`);
});
