# IHP Oman DeerFlow System - Deployment Guide

**Duration:** 4-6 weeks (phased approach)
**Effort:** 40-60 engineer hours
**Team:** 1 DevOps/Engineer + Deepak (part-time)

---

## Phase 1: Setup & Infrastructure (Week 1)

### 1.1 Prepare Development Environment

```bash
# Navigate to DeerFlow directory
cd /home/user/bytedance/deer-flow

# Verify DeerFlow is ready
make doctor

# Expected output:
# ✓ Python 3.12+
# ✓ Node.js 22+
# ✓ pnpm installed
# ✓ Docker available (if using Docker mode)
```

### 1.2 Configure Environment Variables

```bash
# Create .env file in DeerFlow root
cat > /home/user/bytedance/deer-flow/.env << 'EOF'
# LLM Provider
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx (optional)

# Web Search (optional, for market research)
TAVILY_API_KEY=tvly-xxxxx

# Database
DATABASE_URL=sqlite:///.deer-flow/ihp_oman.db
DATABASE_BACKEND=sqlite

# System Settings
DEER_FLOW_PROJECT_ROOT=/home/user/bytedance/deer-flow
DEER_FLOW_HOME=.deer-flow
DEER_FLOW_SKILLS_PATH=skills

# Logging
LOG_LEVEL=INFO
EOF

# Add your API keys
nano .env
```

### 1.3 Copy IHP Oman Configuration

```bash
# Copy configuration files
cp /home/user/markitdown/ihp-oman-deerflow/config/config.yaml \
   /home/user/bytedance/deer-flow/config.yaml

cp /home/user/markitdown/ihp-oman-deerflow/config/extensions_config.json \
   /home/user/bytedance/deer-flow/extensions_config.json

# Verify files copied
ls -la /home/user/bytedance/deer-flow/config*.yaml
ls -la /home/user/bytedance/deer-flow/extensions_config.json
```

### 1.4 Install DeerFlow Dependencies

```bash
cd /home/user/bytedance/deer-flow

# Install all dependencies
make install

# Expected output:
# ✓ Python environment ready
# ✓ Frontend dependencies installed
# ✓ Pre-commit hooks configured

# Verify installation
make check
```

### 1.5 Test Local Development Setup

```bash
# Start DeerFlow in development mode
make dev

# Expected output:
# Starting Nginx on http://localhost:2026
# Starting Gateway API on http://localhost:8001
# Starting Frontend on http://localhost:3000

# Test connectivity (in another terminal)
curl http://localhost:8001/health
# Should return: {"status": "healthy"}
```

### 1.6 Create Database & Initial Setup

```bash
# Initialize database
python -c "
from backend.app.database import init_db
init_db()
print('Database initialized successfully')
"

# Create initial tracking tables (if needed)
sqlite3 .deer-flow/ihp_oman.db << 'EOF'
CREATE TABLE IF NOT EXISTS rfq_tracking (
  rfx_number TEXT PRIMARY KEY,
  ihp_rfq_number TEXT,
  operator TEXT,
  bcd DATE,
  status TEXT,
  created_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vdp_tracking (
  po_number TEXT,
  line_item INTEGER,
  operator TEXT,
  original_eta DATE,
  current_eta DATE,
  delivery_date DATE,
  status TEXT,
  created_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS collections_tracking (
  invoice_number TEXT PRIMARY KEY,
  operator TEXT,
  amount DECIMAL,
  invoice_date DATE,
  payment_date DATE,
  status TEXT
);

.tables
EOF
```

### 1.7 Stop Development Server

```bash
make stop

# Expected output:
# All services stopped successfully
```

**Phase 1 Completion Checklist:**
- [ ] DeerFlow installed and verified
- [ ] Environment variables configured
- [ ] IHP Oman config files copied
- [ ] Database initialized
- [ ] Local dev environment working
- [ ] Documented any issues

---

## Phase 2: Agent Deployment (Week 2)

### 2.1 Deploy Agent Skills

```bash
cd /home/user/bytedance/deer-flow

# Copy IHP Oman skills
cp -r /home/user/markitdown/ihp-oman-deerflow/skills/public/* \
      ./skills/public/

# Verify skills copied
ls -la skills/public/ | grep -E "rfq|principal|compliance|vdp|collections"
```

### 2.2 Deploy Agent Code

```bash
# Copy agent implementations
cp -r /home/user/markitdown/ihp-oman-deerflow/agents/* \
      ./backend/app/agents/

# Verify agents copied
ls -la backend/app/agents/ | grep -E "orchestrator|rfq|principal|compliance|vdp|collections"
```

### 2.3 Configure Agent System Prompts

```bash
# Create system prompts directory
mkdir -p .deer-flow/agent_prompts

# Copy system prompts from documentation
cp /home/user/markitdown/ihp-oman-deerflow/docs/SYSTEM_PROMPTS.md \
   .deer-flow/agent_prompts/

# Each agent will load its prompt from extensions_config.json
```

### 2.4 Test Agent Initialization

```bash
make dev

# Wait for services to start (2-3 minutes)

# Test agent health in another terminal
curl http://localhost:8001/api/agents/orchestrator/status
curl http://localhost:8001/api/agents/rfq-handler/status
curl http://localhost:8001/api/agents/vdp-tracker/status

# Expected output (for each):
# {"status": "healthy", "active_threads": 0, "model": "claude-sonnet-5"}

# Stop if any agent fails to initialize
make stop
```

### 2.5 Run Agent Integration Tests

```bash
# Run test suite
cd backend
make test -k test_agents

# Expected output:
# ✓ test_orchestrator_initialization
# ✓ test_rfq_handler_logging
# ✓ test_principal_coordinator_tq_tracking
# ✓ test_vdp_tracker_calculation
# ✓ test_collections_handler_soa_response
# ✓ test_escalation_routing
#
# 6 passed in 2.3s
```

**Phase 2 Completion Checklist:**
- [ ] All skills deployed
- [ ] Agent code installed
- [ ] System prompts configured
- [ ] Agents initialize without errors
- [ ] Integration tests passing
- [ ] No warnings or errors in logs

---

## Phase 3: Testing & Validation (Week 3)

### 3.1 Prepare Test Data

```bash
# Create test RFQ data
python << 'EOF'
import json
from datetime import datetime, timedelta

test_rfqs = [
  {
    "rfx_number": "RFX#TEST-001",
    "operator": "PDO",
    "item_description": "Flow Transmitter 0-100 bar",
    "bcd": (datetime.now() + timedelta(days=8)).isoformat(),
    "principal": "Autocontrol Process Instrumentation"
  },
  {
    "rfx_number": "RFX#TEST-002",
    "operator": "OQ8",
    "item_description": "Level Gauge",
    "bcd": (datetime.now() + timedelta(days=10)).isoformat(),
    "principal": "Autocontrol Process Instrumentation"
  },
  {
    "rfx_number": "RFX#TEST-003",
    "operator": "bp",
    "item_description": "Water Cut Meter (OWD)",
    "bcd": (datetime.now() + timedelta(days=12)).isoformat(),
    "principal": "KAM"
  }
]

with open('.deer-flow/test_rfqs.json', 'w') as f:
  json.dump(test_rfqs, f, indent=2)

print(f"Created {len(test_rfqs)} test RFQs in .deer-flow/test_rfqs.json")
EOF
```

### 3.2 Test RFQ Handler

```bash
# Start DeerFlow
make dev

# Submit test RFQ to RFQ Handler
curl -X POST http://localhost:8001/api/agents/rfq-handler/run \
  -H "Content-Type: application/json" \
  -d '{
    "rfx_number": "RFX#TEST-001",
    "operator": "PDO",
    "item_description": "Flow Transmitter 0-100 bar",
    "bcd": "2026-09-15",
    "principal": "Autocontrol Process Instrumentation"
  }'

# Expected output:
# {
#   "status": "success",
#   "ihp_rfq_number": "IHP2026001",
#   "rfq_logged": true,
#   "message": "RFQ logged and forwarded to principal"
# }

# Verify it was logged in database
sqlite3 .deer-flow/ihp_oman.db "SELECT * FROM rfq_tracking WHERE rfx_number='RFX#TEST-001';"
```

### 3.3 Test VDP Tracker

```bash
# Create test PO data
python << 'EOF'
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('.deer-flow/ihp_oman.db')
c = conn.cursor()

# Insert test PO lines
test_pos = [
  ('PDO', '4800000001', 1, '2026-09-20', '2026-09-20', None, 'on-time'),
  ('PDO', '4800000002', 1, '2026-09-25', '2026-10-05', None, 'at-risk'),
  ('OQ8', '4500000001', 1, '2026-09-30', '2026-10-15', None, 'on-time'),
]

for operator, po, line, eta, current_eta, delivery, status in test_pos:
  c.execute('''INSERT INTO vdp_tracking 
    (po_number, line_item, operator, original_eta, current_eta, status) 
    VALUES (?, ?, ?, ?, ?, ?)''',
    (po, line, operator, eta, current_eta, status))

conn.commit()
conn.close()
print("Test PO data inserted")
EOF

# Run VDP Tracker
curl -X POST http://localhost:8001/api/agents/vdp-tracker/run \
  -H "Content-Type: application/json" \
  -d '{}'

# Expected output includes:
# {
#   "vdp_current": 75.0,
#   "vdp_status": "IMPROVING",
#   "open_po_lines": [...],
#   "at_risk_items": ["OQ8 4500000001: 10 days late"]
# }
```

### 3.4 Test Collections Handler

```bash
# Test SOA response
curl -X POST http://localhost:8001/api/agents/collections-handler/run \
  -H "Content-Type: application/json" \
  -d '{
    "principal": "Autocontrol Process Instrumentation",
    "soa_amount": 40000,
    "soa_date": "2026-09-20"
  }'

# Expected output:
# {
#   "status": "responded",
#   "response_sent": true,
#   "payment_commitment": "2026-10-05",
#   "message": "SOA acknowledged, payment confirmed for 2026-10-05"
# }
```

### 3.5 Run End-to-End Test

```bash
# Full workflow: RFQ → TQ → Quotation → Award → Delivery

python /home/user/markitdown/ihp-oman-deerflow/tests/test_workflow_e2e.py

# Expected output:
# ✓ RFQ logged successfully
# ✓ Technical query tracked
# ✓ Quotation submitted
# ✓ PO awarded
# ✓ Document compliance tracked
# ✓ Delivery monitored
# ✓ Invoice sent
# ✓ Payment confirmed
#
# Workflow completed in 2.3 seconds
```

**Phase 3 Completion Checklist:**
- [ ] RFQ Handler processes test RFQs correctly
- [ ] VDP Tracker calculates accurately
- [ ] Collections Handler responds same-day
- [ ] Compliance Manager tracks documents
- [ ] End-to-end workflow completes successfully
- [ ] No errors in logs
- [ ] Deepak reviews and approves results

---

## Phase 4: Pilot Deployment (Week 4)

### 4.1 Select Pilot Accounts

```bash
# Start with 2-3 known, friendly accounts:
# - PDO (largest volume)
# - Autocontrol (most principal interaction)
# - KAM (water-cut meter specialist)

# These accounts should have:
# ✓ Recent RFQs (so we can test immediately)
# ✓ Known principals (less variability)
# ✓ Friendly contacts (understanding of pilot)
```

### 4.2 Configure Live Portal Integration

```bash
# If portal integration is needed (optional):
# This is Phase 4 enhancement, not critical for Phase 1

# Edit config to connect to real portals (if available)
nano extensions_config.json

# Add PDO Rabithah credentials if available
# Add Tatweer/Business Gateways credentials if available
# Otherwise, Deepak continues to forward RFxs manually

make stop
make dev

# Verify portal connections
curl http://localhost:8001/api/integrations/status
```

### 4.3 Deploy to Pilot

```bash
# Switch to production-like setup
make docker-start

# Access at http://localhost:2026
# Login with test account
# Navigate to Dashboards → IHP Oman → Pilot

# Monitor for first 24 hours
# Expected activity:
# - RFQs logged
# - TQs tracked
# - Quotations prepared
# - Escalations if needed
```

### 4.4 Daily Monitoring (First Week)

```bash
# Every morning, review:
1. Agent health status
   curl http://localhost:8001/api/agents/status
   
2. RFQ processing
   curl http://localhost:8001/api/rfqs?status=pending
   
3. VDP tracking
   curl http://localhost:8001/api/vdp/summary
   
4. Critical alerts
   curl http://localhost:8001/api/alerts?severity=critical

# Every evening, review logs
tail -f .deer-flow/logs/agent.log
```

### 4.5 Collect Feedback

```bash
# After first week, gather feedback from Deepak:
1. ✓ Agent behavior accurate?
2. ✓ Escalations at right level?
3. ✓ VDP calculations correct?
4. ✓ Any unexpected issues?
5. ✓ Document tracking complete?

# Adjust prompts/rules based on feedback
# Example: If collections handler is too aggressive, adjust tone
nano .deer-flow/agent_prompts/collections_handler.txt

# After adjustments, redeploy
docker-compose restart deerflow-gateway
```

**Phase 4 Completion Checklist:**
- [ ] Pilot accounts selected
- [ ] Portal integration configured (if needed)
- [ ] Agents deployed to Docker
- [ ] 5-7 day monitoring completed
- [ ] Feedback collected from Deepak
- [ ] Adjustments made based on feedback
- [ ] System performing at >90% accuracy
- [ ] Ready for full rollout

---

## Phase 5: Full Rollout (Week 5+)

### 5.1 Enable All Operators

```bash
# Expand from pilot accounts to all operators:
# - PDO (primary)
# - OQ8
# - bp Oman
# - Shell Oman
# - Marsa LNG
# - MEDCO
# - Tatweer

# Update configuration
nano config.yaml

# Add all operators to monitoring list
# Add all principals to coordination list

# Restart services
docker-compose restart deerflow-gateway
```

### 5.2 Full Monitoring Setup

```bash
# Create monitoring dashboard
# Email alerts for critical issues

# Configure daily brief email to Deepak
# Format: VDP status, critical alerts, today's RFQ BCDs, collections status

# Set up weekly VDP review meeting
# Email summary to Hamed every Friday
```

### 5.3 Team Training

```bash
# Brief training for Deepak (~30 minutes):
1. System overview & agents
2. How to read agent outputs
3. When/how to escalate
4. Dashboard navigation
5. Emergency procedures

# Brief training for Ajith (~20 minutes):
1. RFQ workflow automation
2. Technical query coordination
3. Quotation submission process

# Training for accounting (~15 minutes):
1. Invoice tracking
2. Collections automation
3. SOA response process
```

### 5.4 Documentation Handover

```bash
# Provide to IHP Oman team:
1. README.md (system overview)
2. DEPLOYMENT.md (this file)
3. docs/SYSTEM_PROMPTS.md (agent behaviors)
4. docs/WORKFLOW_EXAMPLES.md (real examples)
5. docs/TROUBLESHOOTING.md (common issues)

# Access at:
# /home/user/markitdown/ihp-oman-deerflow/docs/
```

### 5.5 Establish Operations Rhythm

```
DAILY (Deepak):
  9:00 AM - Review agent brief email
  Throughout day - Respond to critical alerts
  5:00 PM - Check tomorrow's RFQ deadlines

WEEKLY (Deepak + Hamed):
  Monday - VDP trend review
  Wednesday - Compliance status
  Friday - Collections summary + Weekly brief to MD

MONTHLY:
  First Monday - Board-level metrics review
  Third Thursday - Principal relationship review
```

**Phase 5 Completion Checklist:**
- [ ] All operators enabled
- [ ] Monitoring alerts configured
- [ ] Team trained
- [ ] Documentation in place
- [ ] Daily/weekly operations rhythm established
- [ ] VDP trending upward (target: 75%+ by week 4)
- [ ] System stable and self-healing

---

## Success Metrics

### By Week 2
- ✅ System deployed and healthy
- ✅ All agents initialize without error
- ✅ Integration tests passing

### By Week 3
- ✅ Test RFQs processed accurately
- ✅ VDP calculation verified
- ✅ End-to-end workflow working

### By Week 4
- ✅ Pilot accounts live
- ✅ Agent behavior validated
- ✅ >90% accuracy on core functions

### By Week 6 (First Month)
- ✅ All accounts live
- ✅ VDP trending upward (target: 75%+)
- ✅ Zero missed RFQ deadlines
- ✅ Deepak freed 10+ hours/week

### By Month 3
- ✅ VDP recovered to 80%+
- ✅ 100% RFQ response rate
- ✅ Zero stalled NCRs
- ✅ Same-day collections responses

### By Month 6
- ✅ VDP recovered to 90%+ (SUCCESS!)
- ✅ PDO account secure
- ✅ All operational metrics green
- ✅ System autonomous

---

## Troubleshooting During Deployment

### Agent not starting?
```bash
# Check logs
docker logs deerflow-gateway | grep "ERROR"

# Verify configuration
make doctor

# Check LLM API keys
echo $ANTHROPIC_API_KEY | cut -c 1-20
# Should show: sk-ant-...
```

### Database errors?
```bash
# Reset database
rm .deer-flow/ihp_oman.db
make install
```

### Portal integration failing?
```bash
# Test connection
python -c "from integrations.pdo_rabithah import test_connection; test_connection()"

# If fails: Check credentials in .env file
```

### High API costs?
```bash
# Reduce model usage
# Switch from Opus to Sonnet for some agents
# Increase model caching
nano config.yaml
```

---

## Support Contacts

- **Technical Issues:** Check `docs/TROUBLESHOOTING.md`
- **Workflow Questions:** Review `docs/WORKFLOW_EXAMPLES.md`
- **Agent Behavior:** See `docs/SYSTEM_PROMPTS.md`
- **Emergency:** Contact system deployment engineer

---

**Deployment Status:** Ready to start
**Next Step:** Execute Phase 1 setup
**Estimated Completion:** Week 4-5
**Target VDP Recovery:** 90%+ by Month 6
