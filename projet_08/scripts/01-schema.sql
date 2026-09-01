-- ============================================================
-- SUPPORT CLIENT - DATABASE SCHEMA
-- PostgreSQL
-- ============================================================


-- ============================================================
-- 1. CUSTOMERS
-- ============================================================

CREATE TABLE customers (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name      TEXT NOT NULL,
    last_name       TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    phone           TEXT,
    address         TEXT,
    city            TEXT,
    postal_code     TEXT,
    country         TEXT NOT NULL DEFAULT 'Canada',
    status          TEXT NOT NULL DEFAULT 'active',

    created_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (status IN ('active', 'inactive', 'blocked'))
);


-- ============================================================
-- 2. PRODUCTS
-- ============================================================

CREATE TABLE products (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_name    TEXT NOT NULL,
    description     TEXT,
    unit_price      INTEGER NOT NULL,
    currency        TEXT NOT NULL DEFAULT 'CAD',
    status          TEXT NOT NULL DEFAULT 'active',

    created_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (unit_price >= 0),
    CHECK (status IN ('active', 'inactive'))
);


-- ============================================================
-- 3. ORDERS
-- ============================================================

CREATE TABLE orders (
    id                  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id         INTEGER NOT NULL,
    order_number        TEXT NOT NULL UNIQUE,

    status              TEXT NOT NULL DEFAULT 'pending',

    total_amount        INTEGER NOT NULL,
    currency            TEXT NOT NULL DEFAULT 'CAD',

    shipping_address    TEXT NOT NULL,

    ordered_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (customer_id)
        REFERENCES customers(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CHECK (
        status IN (
            'pending',
            'confirmed',
            'processing',
            'shipped',
            'delivered',
            'cancelled'
        )
    ),

    CHECK (total_amount >= 0)
);


-- ============================================================
-- 4. ORDER ITEMS
-- ============================================================

CREATE TABLE order_items (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    order_id        INTEGER NOT NULL,
    product_id      INTEGER NOT NULL,

    quantity        INTEGER NOT NULL,
    unit_price      INTEGER NOT NULL,

    FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CHECK (quantity > 0),
    CHECK (unit_price >= 0),

    UNIQUE (order_id, product_id)
);


-- ============================================================
-- 5. PAYMENTS
-- ============================================================

CREATE TABLE payments (
    id                      INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    order_id                INTEGER NOT NULL,

    amount                  INTEGER NOT NULL,
    currency                TEXT NOT NULL DEFAULT 'CAD',

    status                  TEXT NOT NULL,

    payment_method          TEXT NOT NULL,
    transaction_reference   TEXT UNIQUE,

    paid_at                 TEXT,
    created_at              TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CHECK (amount >= 0),

    CHECK (
        status IN (
            'pending',
            'authorized',
            'paid',
            'failed',
            'refunded',
            'partially_refunded'
        )
    ),

    CHECK (
        payment_method IN (
            'credit_card',
            'debit_card',
            'paypal',
            'bank_transfer'
        )
    )
);


-- ============================================================
-- 6. SHIPMENTS
-- ============================================================

CREATE TABLE shipments (
    id                  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    order_id            INTEGER NOT NULL,

    carrier             TEXT NOT NULL,
    tracking_number     TEXT NOT NULL,

    status              TEXT NOT NULL DEFAULT 'pending',

    estimated_delivery  TEXT,
    shipped_at          TEXT,
    delivered_at        TEXT,

    created_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CHECK (
        status IN (
            'pending',
            'in_transit',
            'out_for_delivery',
            'delivered',
            'delayed',
            'lost'
        )
    ),

    UNIQUE (tracking_number)
);


-- ============================================================
-- 7. RETURNS
-- ============================================================

CREATE TABLE returns (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    order_id        INTEGER NOT NULL,

    reason          TEXT NOT NULL,

    status          TEXT NOT NULL DEFAULT 'requested',

    requested_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    approved_at     TEXT,
    received_at     TEXT,
    refunded_at     TEXT,

    FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CHECK (
        status IN (
            'requested',
            'approved',
            'rejected',
            'received',
            'refunded',
            'cancelled'
        )
    )
);
-- ============================================================
-- 8. support_conversations
-- ============================================================
CREATE TABLE support_conversations (
    id                  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    customer_id         INTEGER,

    channel             TEXT NOT NULL DEFAULT 'chat',

    status              TEXT NOT NULL DEFAULT 'open',

    assigned_to         TEXT,

    created_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at           TEXT,

    FOREIGN KEY (customer_id)
        REFERENCES customers(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    CHECK (
        channel IN (
            'chat',
            'email',
            'phone'
        )
    ),

    CHECK (
        status IN (
            'open',
            'in_progress',
            'resolved',
            'escalated',
            'closed'
        )
    )
);

-- ============================================================
-- 9. support_messages
-- ============================================================
CREATE TABLE support_messages (
    id                  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    conversation_id     INTEGER NOT NULL,

    sender_type         TEXT NOT NULL,

    message             TEXT NOT NULL,

    ai_generated        INTEGER NOT NULL DEFAULT 0,

    knowledge_article_id TEXT,

    confidence_score    REAL,

    created_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (conversation_id)
        REFERENCES support_conversations(id)
        ON DELETE CASCADE,

    CHECK (
        sender_type IN (
            'customer',
            'agent',
            'ai'
        )
    ),

    CHECK (ai_generated IN (0, 1)),

    CHECK (
        confidence_score IS NULL
        OR (
            confidence_score >= 0
            AND confidence_score <= 1
        )
    )
);
-- ============================================================
-- 10. INDEXES
-- ============================================================

CREATE INDEX idx_customers_email
    ON customers(email);

-- Orders
CREATE INDEX idx_orders_customer_id
    ON orders(customer_id);

CREATE INDEX idx_orders_status
    ON orders(status);


-- Order items
CREATE INDEX idx_order_items_order_id
    ON order_items(order_id);

CREATE INDEX idx_order_items_product_id
    ON order_items(product_id);


-- Payments
CREATE INDEX idx_payments_order_id
    ON payments(order_id);

CREATE INDEX idx_payments_status
    ON payments(status);


-- Shipments
CREATE INDEX idx_shipments_order_id
    ON shipments(order_id);

CREATE INDEX idx_shipments_tracking_number
    ON shipments(tracking_number);


-- Returns
CREATE INDEX idx_returns_order_id
    ON returns(order_id);

CREATE INDEX idx_returns_status
    ON returns(status);


-- Support
CREATE INDEX idx_support_conversations_customer_id
    ON support_conversations(customer_id);

CREATE INDEX idx_support_messages_conversation_id
    ON support_messages(conversation_id);
