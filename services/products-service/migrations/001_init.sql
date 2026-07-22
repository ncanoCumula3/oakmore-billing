-- Products service schema (billing) — runs into each tenant DB.
CREATE SCHEMA IF NOT EXISTS billing;

CREATE TABLE IF NOT EXISTS billing.products (
  id                 serial PRIMARY KEY,
  code               varchar NOT NULL UNIQUE,
  name               varchar NOT NULL,
  description        varchar,
  category           varchar NOT NULL DEFAULT 'CUSTOM',
  pricing_model      varchar NOT NULL DEFAULT 'FLAT',
  payer              varchar NOT NULL DEFAULT 'EMPLOYER',
  taxable            boolean NOT NULL DEFAULT false,
  gl_account         varchar,
  billing_frequency  varchar NOT NULL DEFAULT 'MONTHLY',
  prorate            boolean NOT NULL DEFAULT false,
  employer_split     numeric(6,4) NOT NULL DEFAULT 0,
  sort_order         integer NOT NULL DEFAULT 100,
  active             boolean NOT NULL DEFAULT true,
  created_at         timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS billing.product_prices (
  id             serial PRIMARY KEY,
  product_id     integer NOT NULL REFERENCES billing.products(id),
  amount         numeric(10,2) NOT NULL,
  percentage     numeric(6,4),
  employer_split numeric(6,4) NOT NULL DEFAULT 0,
  effective_date date NOT NULL,
  is_invalid     boolean NOT NULL DEFAULT false
);
CREATE INDEX IF NOT EXISTS ix_product_prices_product ON billing.product_prices(product_id, is_invalid, effective_date DESC);

CREATE TABLE IF NOT EXISTS billing.client_products (
  id             serial PRIMARY KEY,
  client_id      integer NOT NULL,
  product_id     integer NOT NULL REFERENCES billing.products(id),
  scope          varchar NOT NULL DEFAULT 'ALL_MEMBERS',   -- ALL_MEMBERS | CLIENT_FLAT
  quantity       numeric(10,2) NOT NULL DEFAULT 1,
  price_override numeric(10,2),
  payer_override varchar,
  effective_date date NOT NULL,
  end_date       date,
  is_invalid     boolean NOT NULL DEFAULT false
);
CREATE INDEX IF NOT EXISTS ix_client_products ON billing.client_products(client_id, is_invalid);

CREATE TABLE IF NOT EXISTS billing.member_products (
  id             serial PRIMARY KEY,
  member_id      integer NOT NULL,
  product_id     integer NOT NULL REFERENCES billing.products(id),
  quantity       numeric(10,2) NOT NULL DEFAULT 1,
  price_override numeric(10,2),
  payer_override varchar,
  effective_date date NOT NULL,
  end_date       date,
  is_invalid     boolean NOT NULL DEFAULT false,
  modified_by    varchar,
  modified_date  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_member_products ON billing.member_products(member_id, is_invalid);

CREATE TABLE IF NOT EXISTS billing.invoice_line_items (
  id                serial PRIMARY KEY,
  client_invoice_id integer NOT NULL,
  invoices_final_id integer,
  member_id         integer,                 -- NULL = CLIENT_FLAT line
  product_id        integer NOT NULL,
  product_code      varchar NOT NULL,
  description       varchar,
  line_type         varchar NOT NULL DEFAULT 'CURRENT',  -- CURRENT | BACKBILLED | CREDIT | ADJUSTMENT
  quantity          numeric(10,2) NOT NULL DEFAULT 1,
  unit_price        numeric(10,2) NOT NULL,
  proration_factor  numeric(9,6) NOT NULL DEFAULT 1,
  amount            numeric(10,2) NOT NULL,
  payer             varchar NOT NULL,
  employer_amount   numeric(10,2) NOT NULL DEFAULT 0,
  employee_amount   numeric(10,2) NOT NULL DEFAULT 0,
  taxable           boolean NOT NULL DEFAULT false,
  tax_amount        numeric(10,2) NOT NULL DEFAULT 0,
  gl_account        varchar,
  service_month     date NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_line_items_invoice ON billing.invoice_line_items(client_invoice_id);
CREATE INDEX IF NOT EXISTS ix_line_items_member  ON billing.invoice_line_items(member_id);
-- idempotency guard for generation
CREATE UNIQUE INDEX IF NOT EXISTS uq_line_items_run
  ON billing.invoice_line_items(client_invoice_id, coalesce(member_id,0), product_code, line_type);
