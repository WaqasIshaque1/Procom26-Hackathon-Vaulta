-- Add transaction categories and hardcoded test customer

-- Update transactions with random categories
UPDATE transactions
SET category = CASE 
    WHEN transaction_type ILIKE '%withdrawal%' OR transaction_type ILIKE '%debit%' THEN
        (ARRAY['Food & Dining', 'Transportation', 'Shopping', 'Utilities'])[floor(random() * 4 + 1)]
    WHEN transaction_type ILIKE '%deposit%' OR transaction_type ILIKE '%credit%' THEN 'Income'
    WHEN transaction_type ILIKE '%transfer%' THEN 'Transfer'
    ELSE 'Other'
END
WHERE category IS NULL OR category = '';

-- Update transaction descriptions to be more descriptive
UPDATE transactions
SET description = CASE 
    WHEN category = 'Food & Dining' THEN 
        (ARRAY['Grocery Store', 'Restaurant', 'Coffee Shop', 'Fast Food'])[floor(random() * 4 + 1)]
    WHEN category = 'Transportation' THEN 
        (ARRAY['Gas Station', 'Uber', 'Parking', 'Public Transit'])[floor(random() * 4 + 1)]
    WHEN category = 'Shopping' THEN 
        (ARRAY['Amazon Purchase', 'Online Shopping', 'Clothing Store', 'Electronics'])[floor(random() * 4 + 1)]
    WHEN category = 'Utilities' THEN 
        (ARRAY['Electric Bill', 'Internet Bill', 'Phone Bill', 'Water Bill'])[floor(random() * 4 + 1)]
    WHEN category = 'Income' THEN 'Salary Deposit'
    ELSE transaction_type
END
WHERE description IS NULL OR description = transaction_type;

-- Add hardcoded test customer for quick demo (Customer ID: 9999, PIN: 1111)
INSERT INTO customers (
    customer_id, first_name, last_name, age, gender, address, city,
    contact_number, email, account_type, account_balance,
    date_of_account_opening, last_transaction_date, branch_id, pi, anomaly
) VALUES (
    '9999', 'Demo', 'User', 30, 'Male',
    '123 Demo Street', 'Demo City',
    '+1-555-DEMO', 'demo@vaulta.com', 'Checking', 5000.00,
    '2020-01-01', CURRENT_DATE, 'BR001', '1111', false
)
ON CONFLICT (customer_id) DO UPDATE SET
    account_balance = 5000.00,
    last_transaction_date = CURRENT_DATE;

-- Add demo user's cards
INSERT INTO cards (
    card_id, customer_id, card_type, card_status, last_four_digits, expiry_date,
    credit_limit, credit_card_balance
) VALUES
    ('DEMO_DEBIT', '9999', 'Debit', 'active', '9999', '12/2028', NULL, NULL),
    ('DEMO_CREDIT', '9999', 'Credit', 'active', '8888', '06/2027', 10000.00, 2500.00)
ON CONFLICT (card_id) DO NOTHING;

-- Add demo user's recent transactions
INSERT INTO transactions (
    transaction_id, customer_id, transaction_date, transaction_type,
    transaction_amount, account_balance_after_transaction, description, category, status
) VALUES
    ('DEMO_TXN_1', '9999', CURRENT_TIMESTAMP - INTERVAL '1 day', 'Withdrawal', -50.00, 5000.00, 'Grocery Store', 'Food & Dining', 'completed'),
    ('DEMO_TXN_2', '9999', CURRENT_TIMESTAMP - INTERVAL '3 days', 'Withdrawal', -80.00, 5050.00, 'Gas Station', 'Transportation', 'completed'),
    ('DEMO_TXN_3', '9999', CURRENT_TIMESTAMP - INTERVAL '1 week', 'Deposit', 3000.00, 5130.00, 'Salary Deposit', 'Income', 'completed'),
    ('DEMO_TXN_4', '9999', CURRENT_TIMESTAMP - INTERVAL '10 days', 'Withdrawal', -120.00, 2130.00, 'Amazon Purchase', 'Shopping', 'completed'),
    ('DEMO_TXN_5', '9999', CURRENT_TIMESTAMP - INTERVAL '2 weeks', 'Withdrawal', -30.00, 2250.00, 'Coffee Shop', 'Food & Dining', 'completed')
ON CONFLICT (transaction_id) DO NOTHING;

-- Show summary
SELECT 
    'Customers' as table_name, 
    COUNT(*) as row_count 
FROM customers
UNION ALL
SELECT 'Cards', COUNT(*) FROM cards
UNION ALL
SELECT 'Transactions', COUNT(*) FROM transactions
UNION ALL
SELECT 'Loans', COUNT(*) FROM loans
UNION ALL
SELECT 'Feedback', COUNT(*) FROM feedback;

-- Show demo user details
SELECT 
    c.customer_id,
    c.first_name || ' ' || c.last_name as name,
    c.email,
    c.account_balance,
    COUNT(DISTINCT ca.card_id) as cards_count,
    COUNT(DISTINCT t.transaction_id) as transactions_count
FROM customers c
LEFT JOIN cards ca ON c.customer_id = ca.customer_id
LEFT JOIN transactions t ON c.customer_id = t.customer_id
WHERE c.customer_id = '9999'
GROUP BY c.customer_id, c.first_name, c.last_name, c.email, c.account_balance;
