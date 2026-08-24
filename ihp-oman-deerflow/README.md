# IHP Oman Multi-Agent DeerFlow System

**Status:** Production Implementation
**Purpose:** Automate RFQ-to-cash workflow and recover VDP to 90%+
**Current VDP:** 68.96% (Target: 90%+)

## Overview

This system deploys 6 specialized AI agents using DeerFlow to automate IHP Oman's entire sales and delivery workflow:

1. **RFQ Handler** - Monitor portals, log RFQs, never miss a BCD
2. **Principal Coordinator** - Manage technical queries, compile quotations
3. **Compliance Manager** - Track VDRL, RFI, NCR documents
4. **VDP Tracker** - Monitor delivery performance (CRITICAL)
5. **Collections & SOA Handler** - Manage receivables and payables
6. **Orchestrator** - Coordinate agents, escalate issues

## Quick Start

### Prerequisites

- DeerFlow instance running locally or in Docker
- LLM API keys (Claude, GPT-4, or equivalent)
- Access to PDO Rabithah, Business Gateways portals
- F03 PO Tracker spreadsheet

### Installation (5-10 minutes)

```bash
# 1. Clone DeerFlow (if not already done)
cd /home/user/bytedance/deer-flow

# 2. Copy IHP Oman configuration
cp ihp-oman-deerflow/config/config.yaml ./config.yaml
cp ihp-oman-deerflow/config/extensions_config.json ./extensions_config.json

# 3. Install agent skills
cp -r ihp-oman-deerflow/skills/public/* ./skills/public/

# 4. Start DeerFlow
make dev
# or for production:
make up
```

### Access

- **Web UI:** http://localhost:2026
- **API:** http://localhost:8001/api
- **WebSocket:** ws://localhost:2026/api/websocket

## Architecture

```
Lead Orchestrator
     ↓
┌────┬─────┬─────────┬────────┬─────────────┐
↓    ↓     ↓         ↓        ↓             ↓
RFQ  Principal Compliance VDP    Collections Escalation
Handler Coordinator Manager Tracker Handler Agent
```

## File Structure

```
ihp-oman-deerflow/
├── README.md (this file)
├── DEPLOYMENT.md (step-by-step deployment guide)
├── config/
│   ├── config.yaml (DeerFlow configuration)
│   ├── extensions_config.json (Skills & integrations)
│   └── env.example (Environment variables template)
├── agents/
│   ├── orchestrator.py (Lead orchestrator agent)
│   ├── rfq_handler.py (RFQ portal monitor)
│   ├── principal_coordinator.py (TQ & quotation management)
│   ├── compliance_manager.py (VDRL & NCR tracking)
│   ├── vdp_tracker.py (CRITICAL: Delivery performance)
│   ├── collections_handler.py (Receivables/payables)
│   └── base_agent.py (Common agent functionality)
├── skills/
│   └── public/
│       ├── rfq-monitor/ (Portal monitoring)
│       ├── principal-coordination/ (TQ & offer management)
│       ├── compliance-tracking/ (Document management)
│       ├── vdp-analysis/ (Delivery performance)
│       └── collections-management/ (Payment tracking)
├── integrations/
│   ├── pdo_rabithah.py (PDO Rabithah integration)
│   ├── tatweer_portal.py (Tatweer/Business Gateways)
│   ├── f03_tracker.py (F03 PO Tracker sync)
│   └── email_routing.py (Outlook integration)
├── tests/
│   ├── test_rfq_handler.py
│   ├── test_vdp_tracking.py
│   └── test_agent_coordination.py
└── docs/
    ├── SYSTEM_PROMPTS.md (Agent system prompts)
    ├── WORKFLOW_EXAMPLES.md (Real examples)
    └── TROUBLESHOOTING.md (Common issues)
```

## Configuration

### Environment Variables (Create `.env` file)

```bash
# LLM Provider
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Web Search (for research agent if needed)
TAVILY_API_KEY=tvly-...

# Portal Access (Optional - for actual integration)
PDO_USERNAME=your-username
PDO_PASSWORD=your-password
TATWEER_EMAIL=your-email@ihp.com

# Email Integration (Optional)
OUTLOOK_EMAIL=Sr.Sales@ihpoman.com
OUTLOOK_PASSWORD=your-password

# Database
DATABASE_URL=sqlite:///.deer-flow/ihp_oman.db
```

### DeerFlow Configuration (config.yaml)

Primary settings already configured:
- ✅ Claude Opus 5 (orchestrator/complex decisions)
- ✅ Claude Sonnet 5 (specialist agents)
- ✅ Web search enabled (market research)
- ✅ Sandbox mode (safe execution)
- ✅ SQLite database (tracking)

## Deployment Phases

### Phase 1: Setup (Week 1)
- [ ] Deploy DeerFlow
- [ ] Configure LLM credentials
- [ ] Integrate with F03 PO Tracker
- [ ] Test agent initialization

### Phase 2: Testing (Week 2)
- [ ] Test RFQ Handler on sample RFxs
- [ ] Test Principal Coordinator workflow
- [ ] Test VDP Tracker calculations
- [ ] Validate compliance tracking

### Phase 3: Pilot (Week 3)
- [ ] Run live on 5-10 real RFQs
- [ ] Monitor agent accuracy
- [ ] Gather feedback from Deepak
- [ ] Adjust prompts/rules

### Phase 4: Rollout (Week 4+)
- [ ] Deploy to all accounts
- [ ] Monitor daily (first 2 weeks)
- [ ] Weekly VDP reviews
- [ ] Measure vs. baseline

## Daily Operations

### Deepak's Daily Workflow

```
Morning (9:00 AM):
  ✅ Review Orchestrator's daily brief email
  ✅ Check for red alerts (delivery slips, stalled RFQs)
  ✅ Review VDP tracker (if trending down, escalate)

During Day:
  ✅ System handles: RFQ logging, TQ coordination, document tracking
  ✅ You focus on: Principal relationships, customer interaction
  ✅ System alerts you on: Delays, escalations, critical issues

End of Day (5:00 PM):
  ✅ Review pending collections
  ✅ Confirm any outstanding SOA responses
  ✅ Check tomorrow's RFQ deadlines
```

### Weekly Operations

- **Monday:** Review VDP trend (target: improving toward 90%)
- **Wednesday:** Compliance check (any stalled NCRs?)
- **Friday:** Collections review (receivables status)

## Monitoring & Metrics

### Key Metrics to Track

```json
{
  "vdp_percentage": {
    "target": 90.0,
    "current": "68.96 (initial)",
    "deadline": "6 months"
  },
  "operational_metrics": {
    "rfq_response_rate": "100% (bid or regret by BCD)",
    "document_compliance": "Zero overdue VDRL items",
    "bot_report_accuracy": "100%",
    "soa_response_time": "Same day"
  },
  "time_savings": {
    "deepak_hours_freed_per_week": "10-15",
    "new_hire_ramp_reduction": "50%",
    "bot_report_automation": "2-3 hrs → 10 min/month"
  }
}
```

### Dashboard Access

After deployment, view live metrics at:
- **http://localhost:2026/dashboards/ihp-oman**

## Support & Troubleshooting

### Common Issues

**Agent not responding?**
```bash
# Check agent health
curl http://localhost:8001/api/agents/vdp-tracker/status

# Check logs
docker logs deerflow-gateway (if using Docker)
tail -f .deer-flow/logs/agent.log (if local)
```

**Portal integration failing?**
```bash
# Verify credentials in .env
# Test portal connectivity
python -c "from integrations.pdo_rabithah import test_connection; test_connection()"
```

**VDP calculation incorrect?**
```bash
# Reset and recalculate
python integrations/f03_tracker.py --recalculate-vdp
```

See `docs/TROUBLESHOOTING.md` for more.

## Next Steps

1. **Read `DEPLOYMENT.md`** - Step-by-step deployment instructions
2. **Review `docs/SYSTEM_PROMPTS.md`** - Agent behavior details
3. **Run Phase 1 setup** - Get system live
4. **Execute Phase 2 testing** - Validate accuracy
5. **Deploy Phase 3 pilot** - Real-world testing
6. **Rollout Phase 4** - Full production

## Success Criteria

✅ **VDP Recovery:** From 68.96% → 90%+ within 6 months
✅ **Zero Missed RFQs:** 100% of RFxs answered by BCD
✅ **Compliance:** Zero overdue VDRL items
✅ **Collections:** Same-day SOA responses
✅ **Time Savings:** Deepak freed for 10-15 hours/week

## Questions?

- **Technical:** See `docs/TROUBLESHOOTING.md`
- **Workflow:** See `docs/WORKFLOW_EXAMPLES.md`
- **Agents:** See `docs/SYSTEM_PROMPTS.md`
- **Business Logic:** See `agents/[agent-name].py`

---

**Prepared for:** International Horizon Projects L.L.C. (IHP Oman)
**Date:** August 24, 2026
**Status:** Ready for deployment
