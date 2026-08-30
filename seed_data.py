import json, random
from datetime import datetime, timedelta

# Generates 55 realistic records with built-in edge cases for AI diagnosis
bank_records = []
razorpay_records = []

base_date = datetime(2026, 8, 1)

for i in range(1, 56):
    tx_id = f"pay_RZP_{1000 + i}"
    ref_no = f"BANK_REF_{5000 + i}"
    amount = round(random.uniform(500.0, 15000.0), 2)
    fee = round(amount * 0.02, 2)
    tax = round(fee * 0.18, 2)
    net_payout = round(amount - (fee + tax), 2)
    
    date_str = (base_date + timedelta(days=i % 10)).strftime('%Y-%m-%d')

    # Edge Case 1: Record #15 has a fee mismatch (discrepancy)
    if i == 15:
        net_payout -= 150.0 
    
    # Edge Case 2: Record #30 missing from Bank Statements (unhandled exception)
    if i != 30:
        bank_records.append({
            "transaction_date": date_str,
            "reference_no": ref_no,
            "amount": net_payout,
            "description": f"Settlement payout for {tx_id}"
        })

    # Edge Case 3: Record #45 has delayed bank posting date
    if i == 45:
        date_str = (base_date + timedelta(days=15)).strftime('%Y-%m-%d')

    razorpay_records.append({
        "transaction_id": tx_id,
        "order_id": f"order_{8000 + i}",
        "gross_amount": amount,
        "fee": fee,
        "tax": tax,
        "net_payout": net_payout,
        "status": "processed"
    })

# Save to local synthetic JSON files for fast backend testing
with open('bank_statements.json', 'w') as f:
    json.dump(bank_records, f, indent=2)

with open('razorpay_settlements.json', 'w') as f:
    json.dump(razorpay_records, f, indent=2)

print("✅ Generated 55 synthetic records across bank_statements.json and razorpay_settlements.json!")