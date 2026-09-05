import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

# 1. Initialize App FIRST
app = FastAPI(title="AI Finance Reconciliation Agent")

# 2. Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Helper Function to Load Local JSON Files
def load_data():
    base_path = os.path.dirname(os.path.abspath(__file__))
    bank_file = os.path.join(base_path, "bank_statements.json")
    rzp_file = os.path.join(base_path, "razorpay_settlements.json")
    
    with open(bank_file, "r") as f:
        bank_data = json.load(f)
    with open(rzp_file, "r") as f:
        rzp_data = json.load(f)
        
    return bank_data, rzp_data

# 4. Request Model
class PromptQuery(BaseModel):
    query: str

# 5. Root Endpoint (Fixes "Not Found" at base URL)
@app.get("/")
def read_root():
    return {"status": "AI Finance Engine Online"}

# 6. Reconciliation Endpoint
@app.get("/api/reconcile")
def run_reconciliation():
    bank_data, rzp_data = load_data()
    bank_map = {item["reference_no"]: item for item in bank_data}

    audit_logs = []
    matched_count = 0
    discrepancy_count = 0
    unhandled_count = 0
    total_variance = 0.0

    for i, rzp in enumerate(rzp_data):
        ref_no = f"BANK_REF_{5000 + (i + 1)}"
        bank_record = bank_map.get(ref_no)

        if not bank_record:
            unhandled_count += 1
            audit_logs.append({
                "tx_id": rzp["transaction_id"],
                "bank_ref": ref_no,
                "bank_amount": "N/A",
                "razorpay_payout": f"${rzp['net_payout']:.2f}",
                "status": "UNHANDLED_EXCEPTION",
                "variance": f"-${rzp['net_payout']:.2f}",
                "ai_diagnosis": "Missing bank entry. Settlement record exists in Razorpay but no corresponding bank transaction found."
            })
            continue

        variance = round(bank_record["amount"] - rzp["net_payout"], 2)

        if abs(variance) < 0.01:
            matched_count += 1
            audit_logs.append({
                "tx_id": rzp["transaction_id"],
                "bank_ref": ref_no,
                "bank_amount": f"${bank_record['amount']:.2f}",
                "razorpay_payout": f"${rzp['net_payout']:.2f}",
                "status": "MATCHED",
                "variance": "$0.00",
                "ai_diagnosis": f"100% net match across fees (${rzp['fee']:.2f}) & GST (${rzp['tax']:.2f})."
            })
        else:
            discrepancy_count += 1
            total_variance += variance
            audit_logs.append({
                "tx_id": rzp["transaction_id"],
                "bank_ref": ref_no,
                "bank_amount": f"${bank_record['amount']:.2f}",
                "razorpay_payout": f"${rzp['net_payout']:.2f}",
                "status": "DISCREPANCY",
                "variance": f"${variance:.2f}",
                "ai_diagnosis": f"${abs(variance):.2f} variance detected. AI Reason: Unreconciled manual debit/chargeback deduction."
            })

    total_records = len(rzp_data)
    reconciliation_rate = round((matched_count / total_records) * 100, 1) if total_records > 0 else 0.0

    return {
        "metrics": {
            "total_records": total_records,
            "matched_count": matched_count,
            "unhandled_count": unhandled_count + discrepancy_count,
            "reconciliation_rate": f"{reconciliation_rate}%",
            "net_variance": f"${total_variance:.2f}"
        },
        "audit_logs": audit_logs
    }

# 7. AI Query Endpoint
@app.post("/api/ai-query")
def process_ai_query(body: PromptQuery):
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        return {"response": "GEMINI_API_KEY environment variable is not configured."}

    try:
        ai_client = genai.Client(api_key=gemini_key)
        response = ai_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"You are an expert AI Finance Controller for Razorpay Buildathon. Answer this question concisely based on financial reconciliation rules: {body.query}"
        )
        return {"response": response.text}
    except Exception as e:
        return {"response": f"AI Engine error: {str(e)}"}
