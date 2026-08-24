-- IHP Oman DeerFlow Database Schema
-- SQLite database for tracking RFQ-to-cash workflow

-- ============================================================================
-- RFQ TRACKING TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS rfq_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rfx_number TEXT NOT NULL UNIQUE,
    ihp_rfq_number TEXT UNIQUE,
    operator_name TEXT NOT NULL,
    operator_code TEXT,
    description TEXT,
    bcd_date DATETIME NOT NULL,
    received_date DATETIME NOT NULL,
    logged_date DATETIME,
    forwarded_to_principal TEXT,
    forwarded_date DATETIME,
    status TEXT DEFAULT 'received',  -- received, forwarded, bid_submitted, regret_sent, closed
    assigned_agent_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- QUOTATION TRACKING TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS quotation_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quotation_number TEXT NOT NULL UNIQUE,
    ihp_rfq_number TEXT NOT NULL,
    rfx_number TEXT,
    principal_name TEXT NOT NULL,
    principal_offer_price REAL,
    ihp_margin_percent REAL,
    ihp_selling_price REAL,
    technical_query_count INTEGER DEFAULT 0,
    last_tq_response_date DATETIME,
    submission_date DATETIME,
    bcd_date DATETIME,
    days_until_bcd INTEGER,
    status TEXT DEFAULT 'draft',  -- draft, tq_pending, ready, submitted, awarded, lost
    assigned_agent_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- PURCHASE ORDER TRACKING TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS po_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    po_number TEXT NOT NULL UNIQUE,
    ihp_po_reference TEXT UNIQUE,
    operator_name TEXT NOT NULL,
    operator_code TEXT,
    principal_name TEXT NOT NULL,
    quotation_number TEXT,
    po_value REAL,
    order_date DATETIME,
    promised_delivery_date DATETIME,
    actual_delivery_date DATETIME,
    delivery_status TEXT DEFAULT 'open',  -- on_time, late, at_risk, delivered
    delivery_slip_alert_days INTEGER,
    days_overdue INTEGER,
    vdp_included BOOLEAN DEFAULT 1,
    operator_priority TEXT,  -- critical, high, medium, low
    assigned_agent_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- VDP TRACKING TABLE (Vendor Delivery Performance)
-- ============================================================================
CREATE TABLE IF NOT EXISTS vdp_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operator_name TEXT NOT NULL UNIQUE,
    operator_code TEXT,
    total_deliveries_12m INTEGER DEFAULT 0,
    on_time_deliveries_12m INTEGER DEFAULT 0,
    late_deliveries_12m INTEGER DEFAULT 0,
    vdp_percentage REAL DEFAULT 0.0,
    vdp_threshold REAL DEFAULT 90.0,
    vdp_status TEXT DEFAULT 'normal',  -- normal, alert, critical
    last_calculated DATETIME,
    alert_sent_date DATETIME,
    bot_report_due_date DATETIME,
    bot_report_submitted_date DATETIME,
    assigned_agent_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- COMPLIANCE TRACKING TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS compliance_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    po_number TEXT NOT NULL,
    document_type TEXT NOT NULL,  -- vdrl, rfi, ncr, tpi, wps
    reference_number TEXT UNIQUE,
    description TEXT,
    required_by_date DATETIME,
    submitted_date DATETIME,
    status TEXT DEFAULT 'pending',  -- pending, submitted, approved, rejected, closed
    days_overdue INTEGER DEFAULT 0,
    severity TEXT DEFAULT 'normal',  -- normal, high, critical
    assigned_agent_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- COLLECTIONS TRACKING TABLE (Receivables)
-- ============================================================================
CREATE TABLE IF NOT EXISTS collections_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number TEXT NOT NULL UNIQUE,
    po_number TEXT,
    customer_name TEXT NOT NULL,
    invoice_amount REAL NOT NULL,
    invoice_date DATETIME NOT NULL,
    due_date DATETIME NOT NULL,
    payment_received_date DATETIME,
    payment_status TEXT DEFAULT 'outstanding',  -- outstanding, partial, paid
    days_overdue INTEGER DEFAULT 0,
    reminder_count INTEGER DEFAULT 0,
    escalation_level TEXT DEFAULT 'normal',  -- normal, warning, escalated, critical
    assigned_agent_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- PAYABLES TRACKING TABLE (Principal SOA - Statement of Account)
-- ============================================================================
CREATE TABLE IF NOT EXISTS payables_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    soa_reference TEXT NOT NULL UNIQUE,
    principal_name TEXT NOT NULL,
    principal_code TEXT,
    soa_amount REAL NOT NULL,
    soa_date DATETIME NOT NULL,
    due_date DATETIME NOT NULL,
    payment_due_date DATETIME,
    ihp_response_date DATETIME,
    payment_commitment TEXT,
    response_status TEXT DEFAULT 'pending',  -- pending, acknowledged, committed, paid
    days_since_soa INTEGER,
    assigned_agent_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- AGENT LOGS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS agent_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,
    agent_type TEXT,  -- orchestrator, rfq_handler, principal_coordinator, compliance_manager, vdp_tracker, collections_handler
    action_type TEXT NOT NULL,
    object_type TEXT,  -- rfq, quotation, po, compliance, collection, payable
    object_id TEXT,
    status TEXT,
    message TEXT,
    error_message TEXT,
    execution_time_ms INTEGER,
    assigned_to TEXT,  -- deepak, hamed
    escalated BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- ALERTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_type TEXT NOT NULL,  -- delivery_slip, rfq_miss, tq_delay, ncr_stalled, payment_overdue, soa_unanswered, vdp_critical
    severity TEXT NOT NULL,  -- yellow, red, critical
    object_id TEXT,
    object_type TEXT,
    message TEXT,
    assigned_to TEXT,  -- deepak, hamed
    alert_sent_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_date DATETIME,
    resolved BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES for performance
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_rfq_bcd_date ON rfq_tracking(bcd_date);
CREATE INDEX IF NOT EXISTS idx_rfq_status ON rfq_tracking(status);
CREATE INDEX IF NOT EXISTS idx_po_promised_delivery ON po_tracking(promised_delivery_date);
CREATE INDEX IF NOT EXISTS idx_po_delivery_status ON po_tracking(delivery_status);
CREATE INDEX IF NOT EXISTS idx_vdp_operator ON vdp_tracking(operator_name);
CREATE INDEX IF NOT EXISTS idx_compliance_po ON compliance_tracking(po_number);
CREATE INDEX IF NOT EXISTS idx_compliance_status ON compliance_tracking(status);
CREATE INDEX IF NOT EXISTS idx_collections_status ON collections_tracking(payment_status);
CREATE INDEX IF NOT EXISTS idx_collections_overdue ON collections_tracking(days_overdue);
CREATE INDEX IF NOT EXISTS idx_payables_status ON payables_tracking(response_status);
CREATE INDEX IF NOT EXISTS idx_alerts_resolved ON alerts(resolved);
CREATE INDEX IF NOT EXISTS idx_agent_logs_agent ON agent_logs(agent_name);
