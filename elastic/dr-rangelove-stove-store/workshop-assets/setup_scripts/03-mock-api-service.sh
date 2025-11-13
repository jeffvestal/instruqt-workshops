#!/bin/bash
set -e

echo "[Mock API] Creating remediation API service..."

MOCK_API_DIR="/opt/mock-remediation-api"
mkdir -p "$MOCK_API_DIR"
cd "$MOCK_API_DIR"

# Write package.json
cat > package.json <<'EOF'
{
  "name": "mock-remediation-api",
  "version": "1.0.0",
  "dependencies": {"express": "^4.18.2"}
}
EOF

# Write server.js
cat > server.js <<'EOF'
const express = require('express');
const app = express();
app.use(express.json());

app.post('/remediate_service', (req, res) => {
  const serviceName = req.body.service_name || 'unknown';
  const timestamp = new Date().toISOString();
  const remediationId = `rem-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;

  console.log(`[${timestamp}] [REMEDIATION] Triggered for service: ${serviceName} (ID: ${remediationId})`);

  res.json({
    success: true,
    status: 'remediation_triggered',
    remediation_id: remediationId,
    service: serviceName,
    action: 'restart_service',
    timestamp,
    message: `✅ Remediation initiated for ${serviceName}`,
    details: {
      steps: ['Draining connections', 'Restarting service', 'Health check'],
      estimated_duration: '30s'
    }
  });
});

app.get('/health', (req, res) => {
  res.json({status: 'healthy', uptime: process.uptime()});
});

const PORT = 3000;
app.listen(PORT, () => console.log(`Mock Remediation API listening on port ${PORT}`));
EOF

echo "[Mock API] Installing dependencies..."
npm install --production --silent

echo "[Mock API] Starting with pm2..."
pm2 delete mock-api 2>/dev/null || true
pm2 start server.js --name mock-api
pm2 save --force

echo "[Mock API] Service started on port 3000"
echo "[Mock API] Endpoints:"
echo "  - POST http://localhost:3000/remediate_service"
echo "  - GET  http://localhost:3000/health"

