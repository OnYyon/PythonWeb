CREATE TABLE IF NOT EXISTS user_cards (
    card_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    balance NUMERIC(12, 2) NOT NULL CHECK (balance >= 0)
);

CREATE INDEX IF NOT EXISTS idx_user_cards_user_id
    ON user_cards (user_id);

CREATE TABLE IF NOT EXISTS payments (
    payment_id UUID PRIMARY KEY,
    sub_id UUID NOT NULL,
    amount NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
    card_hash VARCHAR(64) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_payments_sub_id
    ON payments (sub_id);

CREATE INDEX IF NOT EXISTS idx_payments_card_hash
    ON payments (card_hash);
