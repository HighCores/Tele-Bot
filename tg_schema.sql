-- ============================================
-- Run this in Supabase SQL Editor for Telegram Bot
-- ============================================

CREATE TABLE IF NOT EXISTS tg_tickets (
    id BIGSERIAL PRIMARY KEY,
    ticket_id TEXT UNIQUE NOT NULL,
    user_id BIGINT NOT NULL,
    user_name TEXT,
    status TEXT DEFAULT 'open',
    topic_id BIGINT,
    subject TEXT,
    type TEXT,
    claimed_by TEXT,
    claimed_at TIMESTAMPTZ,
    closed_by TEXT,
    closed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tg_ticket_messages (
    id BIGSERIAL PRIMARY KEY,
    ticket_id TEXT REFERENCES tg_tickets(ticket_id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL,
    user_name TEXT,
    content TEXT NOT NULL,
    message_id BIGINT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tg_orders (
    id BIGSERIAL PRIMARY KEY,
    order_num TEXT UNIQUE NOT NULL,
    user_id BIGINT NOT NULL,
    user_name TEXT,
    project TEXT,
    contact TEXT,
    eta TEXT,
    total_price NUMERIC,
    status TEXT DEFAULT 'pending',
    topic_id BIGINT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tg_order_items (
    id BIGSERIAL PRIMARY KEY,
    order_num TEXT REFERENCES tg_orders(order_num) ON DELETE CASCADE,
    item_id TEXT NOT NULL,
    item_name TEXT NOT NULL,
    price NUMERIC NOT NULL
);

CREATE TABLE IF NOT EXISTS tg_vouchers (
    id BIGSERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    percentage INT NOT NULL,
    type TEXT,
    is_used BOOLEAN DEFAULT FALSE,
    user_id BIGINT,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tg_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
