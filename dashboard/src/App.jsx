import React, { useState, useEffect } from 'react';
import {
    Container,
    Grid,
    Card,
    CardContent,
    Typography,
    Box,
    Chip,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    TextField,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    Button,
    Alert,
    CircularProgress
} from '@mui/material';
import {
    Security,
    BugReport,
    Warning,
    CheckCircle,
    Error,
    Info,
    TrendingUp,
    FilterList,
    Download
} from '@mui/icons-material';
import {
    PieChart,
    Pie,
    Cell,
    BarChart,
    Bar,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer
} from 'recharts';
import './App.css';

// Sample data structure - in production, this would come from API
const sampleData = {
    report_id: "ai_analysis_20251215_083000",
    generated_at: "2025-12-15T08:30:00Z",
    policy: {
        name: "Enterprise Security Policy",
        version: "1.0"
    },
    summary: {
        total_vulnerabilities: 45,
        filtered_vulnerabilities: 18,
        false_positives: 27,
        false_positive_rate: 0.6,
        by_severity: {
            CRITICAL: 2,
            HIGH: 5,
            MEDIUM: 7,
            LOW: 3,
            INFO: 1
        },
        by_source: {
            SAST: 12,
            DAST: 6
        }
    },
    top_priorities: [
        {
            id: "vuln_001",
            title: "SQL Injection in login endpoint",
            severity: "CRITICAL",
            risk_score: 0.95,
            priority: 1,
            location: { file: "app.py", line_start: 75 },
            cwe: "CWE-89",
            owasp: "A03:2021-Injection",
            remediation: { sla_days: 3, effort: "MEDIUM" }
        },
        {
            id: "vuln_002",
            title: "Command Injection in ping utility",
            severity: "CRITICAL",
            risk_score: 0.92,
            priority: 1,
            location: { file: "app.py", line_start: 145 },
            cwe: "CWE-78",
            owasp: "A03:2021-Injection",
            remediation: { sla_days: 3, effort: "HIGH" }
        }
    ]
};

function App() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState({ severity: 'ALL', source: 'ALL', search: '' });
    const [filteredVulns, setFilteredVulns] = useState([]);

    useEffect(() => {
        // Load data from file or API
        loadData();
    }, []);

    useEffect(() => {
        if (data) {
            applyFilters();
        }
    }, [filter, data]);

    const loadData = async () => {
        try {
            // Try to load from public/data/ai_analysis.json
            const response = await fetch('./data/ai_analysis.json');
            if (response.ok) {
                const jsonData = await response.json();
                setData(jsonData);
            } else {
                // Use sample data if file not found
                setData(sampleData);
            }
        } catch (error) {
            console.log('Using sample data:', error);
            setData(sampleData);
        } finally {
            setLoading(false);
        }
    };

    const applyFilters = () => {
        // Use all_findings instead of top_priorities to show ALL vulnerabilities
        if (!data || !data.all_findings) return;

        let filtered = data.all_findings;

        if (filter.severity !== 'ALL') {
            filtered = filtered.filter(v => v.severity === filter.severity);
        }

        if (filter.source !== 'ALL') {
            filtered = filtered.filter(v => v.source === filter.source);
        }

        if (filter.search) {
            const searchLower = filter.search.toLowerCase();
            filtered = filtered.filter(v =>
                v.title.toLowerCase().includes(searchLower) ||
                v.cwe?.toLowerCase().includes(searchLower) ||
                v.location?.file?.toLowerCase().includes(searchLower)
            );
        }

        // Sort by priority (P1 first) then by risk score (highest first)
        filtered.sort((a, b) => {
            if (a.priority !== b.priority) {
                return a.priority - b.priority; // P1, P2, P3...
            }
            return b.risk_score - a.risk_score; // Higher risk score first
        });

        setFilteredVulns(filtered);
    };

    const getSeverityColor = (severity) => {
        const colors = {
            CRITICAL: '#ff0080',
            HIGH: '#ff8c42',
            MEDIUM: '#f59e0b',
            LOW: '#10b981',
            INFO: '#a78bfa'
        };
        return colors[severity] || '#00d9ff';
    };

    const getSeverityIcon = (severity) => {
        if (severity === 'CRITICAL' || severity === 'HIGH') return <Error />;
        if (severity === 'MEDIUM') return <Warning />;
        return <Info />;
    };

    const exportToCSV = () => {
        if (!data) return;

        const csv = [
            ['ID', 'Title', 'Severity', 'Source', 'Risk Score', 'CWE', 'OWASP', 'Location', 'SLA Days'].join(','),
            ...filteredVulns.map(v => [
                v.id,
                `"${v.title}"`,
                v.severity,
                v.source || '',
                v.risk_score,
                v.cwe || '',
                v.owasp || '',
                v.source === 'DAST'
                    ? `"${v.location?.method || 'GET'} ${v.location?.url || ''}"`
                    : `"${v.location?.file || ''}:${v.location?.line_start || ''}"`,
                v.remediation?.sla_days || ''
            ].join(','))
        ].join('\n');

        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'vulnerabilities.csv';
        a.click();
    };

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
                <CircularProgress size={60} />
            </Box>
        );
    }

    if (!data) {
        return (
            <Container maxWidth="xl" sx={{ color: '#ffffff' }}>
                <Alert severity="error">Failed to load vulnerability data</Alert>
            </Container>
        );
    }

    const summary = data.summary || {};
    const severityData = Object.entries(summary.by_severity || {})
        .filter(([name, value]) => name !== 'INFO' && value > 0)
        .map(([name, value]) => ({
            name,
            value,
            color: getSeverityColor(name)
        }));

    const sourceData = Object.entries(summary.by_source || {}).map(([name, value]) => ({
        name,
        value
    }));

    return (
        <div className="App">
            {/* Header */}
            <Box className="header" sx={{
                background: 'rgba(10, 10, 15, 0.8)',
                backdropFilter: 'blur(20px)',
                borderBottom: '1px solid rgba(0, 217, 255, 0.2)',
                py: 3,
                mb: 4
            }}>
                <Container maxWidth="xl">
                    <Box display="flex" alignItems="center" gap={2}>
                        <Security sx={{
                            fontSize: 40,
                            color: '#00d9ff',
                            filter: 'drop-shadow(0 0 10px rgba(0, 217, 255, 0.6))'
                        }} />
                        <Box flex={1}>
                            <Typography
                                variant="h4"
                                fontWeight="700"
                                sx={{
                                    color: '#ffffff',
                                    letterSpacing: '-0.5px',
                                    fontWeight: 700
                                }}
                            >
                                AI-Driven DevSecOps
                            </Typography>
                            <Typography variant="body2" sx={{
                                color: '#00d9ff',
                                fontWeight: 500,
                                opacity: 0.9
                            }}>
                                Security Vulnerability Analysis & Prioritization
                            </Typography>
                        </Box>
                    </Box>
                </Container>
            </Box>

            <Container maxWidth="xl">
                {/* Summary Cards */}
                <Grid container spacing={3} sx={{ mb: 4 }}>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card className="glass-card hover-lift animate-fade-in">
                            <CardContent>
                                <Box display="flex" justifyContent="space-between" alignItems="center">
                                    <Box>
                                        <Typography sx={{ color: '#ffffff', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }} variant="body2">
                                            Total Findings
                                        </Typography>
                                        <Typography variant="h4" fontWeight="700" sx={{ color: '#00d9ff', mt: 0.5 }}>
                                            {summary.total_vulnerabilities || 0}
                                        </Typography>
                                    </Box>
                                    <BugReport sx={{ fontSize: 40, color: '#00d9ff', opacity: 0.4 }} />
                                </Box>
                            </CardContent>
                        </Card>
                    </Grid>

                    <Grid item xs={12} sm={6} md={3}>
                        <Card className="glass-card hover-lift animate-fade-in" style={{ animationDelay: '0.1s' }}>
                            <CardContent>
                                <Box display="flex" justifyContent="space-between" alignItems="center">
                                    <Box>
                                        <Typography sx={{ color: '#ffffff', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }} variant="body2">
                                            After Filtering
                                        </Typography>
                                        <Typography variant="h4" fontWeight="700" sx={{ color: '#00d9ff', mt: 0.5 }}>
                                            {summary.filtered_vulnerabilities || 0}
                                        </Typography>
                                    </Box>
                                    <FilterList sx={{ fontSize: 40, color: '#00d9ff', opacity: 0.4 }} />
                                </Box>
                            </CardContent>
                        </Card>
                    </Grid>

                    <Grid item xs={12} sm={6} md={3}>
                        <Card className="glass-card hover-lift animate-fade-in" style={{ animationDelay: '0.2s' }}>
                            <CardContent>
                                <Box display="flex" justifyContent="space-between" alignItems="center">
                                    <Box>
                                        <Typography sx={{ color: '#ffffff', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }} variant="body2">
                                            False Positive Rate
                                        </Typography>
                                        <Typography variant="h4" fontWeight="700" sx={{ color: '#00d9ff', mt: 0.5 }}>
                                            {((summary.false_positive_rate || 0) * 100).toFixed(0)}%
                                        </Typography>
                                    </Box>
                                    <CheckCircle sx={{ fontSize: 40, color: '#a78bfa', opacity: 0.4 }} />
                                </Box>
                            </CardContent>
                        </Card>
                    </Grid>

                    <Grid item xs={12} sm={6} md={3}>
                        <Card className="glass-card hover-lift" style={{ animationDelay: '0.3s' }}>
                            <CardContent>
                                <Box display="flex" justifyContent="space-between" alignItems="center">
                                    <Box>
                                        <Typography sx={{ color: '#ffffff', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }} variant="body2">
                                            Critical + High
                                        </Typography>
                                        <Typography
                                            variant="h4"
                                            fontWeight="700"
                                            sx={{ color: '#ff0080', mt: 0.5 }}
                                        >
                                            {(summary.by_severity?.CRITICAL || 0) + (summary.by_severity?.HIGH || 0)}
                                        </Typography>
                                    </Box>
                                    <Error sx={{ fontSize: 40, color: '#ff0080', opacity: 0.4 }} />
                                </Box>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>

                {/* Charts */}
                <Grid container spacing={3} sx={{ mb: 4 }}>
                    <Grid item xs={12} md={6}>
                        <Card className="glass-card animate-fade-in">
                            <CardContent>
                                <Typography variant="h6" gutterBottom fontWeight="600">
                                    Vulnerabilities by Severity
                                </Typography>
                                <ResponsiveContainer width="100%" height={300}>
                                    <PieChart>
                                        <Pie
                                            data={severityData}
                                            cx="50%"
                                            cy="50%"
                                            outerRadius={100}
                                            dataKey="value"
                                        >
                                            {severityData.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={entry.color} />
                                            ))}
                                        </Pie>
                                        <Tooltip />
                                        <Legend />
                                    </PieChart>
                                </ResponsiveContainer>

                            </CardContent>
                        </Card>
                    </Grid>

                    <Grid item xs={12} md={6}>
                        <Card className="glass-card animate-fade-in">
                            <CardContent>
                                <Typography variant="h6" gutterBottom fontWeight="600">
                                    Findings by Source
                                </Typography>
                                <ResponsiveContainer width="100%" height={300}>
                                    <BarChart data={sourceData}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                                        <XAxis dataKey="name" stroke="#cbd5e1" />
                                        <YAxis stroke="#cbd5e1" />
                                        <Tooltip
                                            contentStyle={{
                                                backgroundColor: '#1e293b',
                                                border: '1px solid rgba(255,255,255,0.1)',
                                                borderRadius: '8px'
                                            }}
                                        />
                                        <Bar dataKey="value" fill="#6366f1" radius={[8, 8, 0, 0]} />
                                    </BarChart>
                                </ResponsiveContainer>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>

                {/* Filters */}
                <Card className="glass-card" sx={{ mb: 3 }}>
                    <CardContent>
                        <Grid container spacing={2} alignItems="center">
                            <Grid item xs={12} sm={4}>
                                <TextField
                                    fullWidth
                                    label="Search"
                                    variant="outlined"
                                    value={filter.search}
                                    onChange={(e) => setFilter({ ...filter, search: e.target.value })}
                                    size="small"
                                />
                            </Grid>
                            <Grid item xs={12} sm={3}>
                                <FormControl fullWidth size="small">
                                    <InputLabel>Severity</InputLabel>
                                    <Select
                                        value={filter.severity}
                                        label="Severity"
                                        onChange={(e) => setFilter({ ...filter, severity: e.target.value })}
                                    >
                                        <MenuItem value="ALL">All Severities</MenuItem>
                                        <MenuItem value="CRITICAL">Critical</MenuItem>
                                        <MenuItem value="HIGH">High</MenuItem>
                                        <MenuItem value="MEDIUM">Medium</MenuItem>
                                        <MenuItem value="LOW">Low</MenuItem>
                                        <MenuItem value="INFO">Info</MenuItem>
                                    </Select>
                                </FormControl>
                            </Grid>
                            <Grid item xs={12} sm={3}>
                                <FormControl fullWidth size="small">
                                    <InputLabel>Source</InputLabel>
                                    <Select
                                        value={filter.source}
                                        label="Source"
                                        onChange={(e) => setFilter({ ...filter, source: e.target.value })}
                                    >
                                        <MenuItem value="ALL">All Sources</MenuItem>
                                        <MenuItem value="SAST">SAST</MenuItem>
                                        <MenuItem value="DAST">DAST</MenuItem>
                                    </Select>
                                </FormControl>
                            </Grid>
                            <Grid item xs={12} sm={2}>
                                <Button
                                    fullWidth
                                    variant="contained"
                                    startIcon={<Download />}
                                    onClick={exportToCSV}
                                    sx={{
                                        background: 'linear-gradient(135deg, #6366f1 0%, #ec4899 100%)',
                                        '&:hover': {
                                            background: 'linear-gradient(135deg, #4f46e5 0%, #db2777 100%)',
                                        }
                                    }}
                                >
                                    Export
                                </Button>
                            </Grid>
                        </Grid>
                    </CardContent>
                </Card>

                {/* Vulnerability Table */}
                <Card className="glass-card">
                    <CardContent>
                        <Typography variant="h6" gutterBottom fontWeight="600" sx={{ mb: 2 }}>
                            All Vulnerabilities - Sorted by Priority ({filteredVulns.length})
                        </Typography>
                        <TableContainer>
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Priority</TableCell>
                                        <TableCell>Title</TableCell>
                                        <TableCell>Source</TableCell>
                                        <TableCell>Severity</TableCell>
                                        <TableCell>Risk Score</TableCell>
                                        <TableCell>CWE</TableCell>
                                        <TableCell>Location</TableCell>
                                        <TableCell>SLA</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {filteredVulns.map((vuln, index) => (
                                        <TableRow
                                            key={vuln.id}
                                            className="animate-slide-in"
                                            style={{ animationDelay: `${index * 0.05}s` }}
                                            sx={{
                                                '&:hover': {
                                                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                                                    cursor: 'pointer'
                                                }
                                            }}
                                        >
                                            <TableCell>
                                                <Chip
                                                    label={`P${vuln.priority}`}
                                                    size="small"
                                                    sx={{
                                                        fontWeight: 'bold',
                                                        background: vuln.priority === 1 ? '#dc2626' : '#f59e0b'
                                                    }}
                                                />
                                            </TableCell>
                                            <TableCell>
                                                <Box display="flex" alignItems="center" gap={1}>
                                                    {getSeverityIcon(vuln.severity)}
                                                    <Typography variant="body2">{vuln.title}</Typography>
                                                </Box>
                                            </TableCell>
                                            <TableCell>
                                                <Chip
                                                    label={vuln.source || 'SAST'}
                                                    size="small"
                                                    sx={{
                                                        backgroundColor: vuln.source === 'DAST' ? '#6366f1' : '#0ea5e9',
                                                        fontWeight: 'bold'
                                                    }}
                                                />
                                            </TableCell>
                                            <TableCell>
                                                <Chip
                                                    label={vuln.severity}
                                                    size="small"
                                                    sx={{
                                                        backgroundColor: getSeverityColor(vuln.severity),
                                                        fontWeight: 'bold'
                                                    }}
                                                />
                                            </TableCell>
                                            <TableCell>
                                                <Typography variant="body2" fontWeight="600">
                                                    {(vuln.risk_score * 100).toFixed(0)}%
                                                </Typography>
                                            </TableCell>
                                            <TableCell>
                                                <Chip
                                                    label={vuln.cwe || 'N/A'}
                                                    size="small"
                                                    variant="outlined"
                                                    sx={{
                                                        color: '#ffffff',
                                                        borderColor: 'rgba(255, 255, 255, 0.5)'
                                                    }}
                                                />
                                            </TableCell>
                                            <TableCell>
                                                <Typography variant="body2" sx={{ color: '#ffffff' }}>
                                                    {vuln.source === 'DAST'
                                                        ? `${vuln.location?.method || 'GET'} ${vuln.location?.url || ''}${vuln.location?.parameter ? ' [' + vuln.location.parameter + ']' : ''}`
                                                        : `${vuln.location?.file || ''}:${vuln.location?.line_start || ''}`
                                                    }
                                                </Typography>
                                            </TableCell>
                                            <TableCell>
                                                <Typography variant="body2">
                                                    {vuln.remediation?.sla_days} days
                                                </Typography>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </CardContent>
                </Card>

                {/* Footer */}
                <Box sx={{ mt: 4, mb: 2, textAlign: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                        Generated: {new Date(data.generated_at).toLocaleString()} |
                        Policy: {data.policy?.name} v{data.policy?.version}
                    </Typography>
                </Box>
            </Container>
        </div>
    );
}

export default App;
