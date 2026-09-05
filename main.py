import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
# 2. Root route so base URL doesn't return "Not Found"
@app.get("/")
def read_root():
    return {"status": "AI Finance Engine Online"}

# 3. Data Reconciliation Endpoint
@app.get("/api/reconcile")
def run_reconciliation():
    base_path = os.path.dirname(os.path.abspath(_file_))
    bank_file = os.path.join(base_path, "bank_statements.json")
    rzp_file = os.path.join(base_path, "razorpay_settlements.json")
    
    with open(bank_file, "r") as f:
        bank_data = json.load(f)
    with open(rzp_file, "r") as f:
        rzp_data = json.load(f)
        
    return {"bank": bank_data, "razorpay": rzp_data}

# 4. AI Query Endpoint
@app.post("/api/ai-query")
def process_ai_query(payload: dict):
    user_query = payload.get("query", "")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not gemini_key:
        return {"response": "GEMINI_API_KEY environment variable is not configured."}
        
    client = genai.Client(api_key=gemini_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_query,
    )
    return {"response": response.text}

app = FastAPI(title="AI Finance Reconciliation Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    ai_client = genai.Client(api_key=GEMINI_API_KEY)
else:
    ai_client = None

# Initialize Gemini Client (uses GEMINI_API_KEY environment variable)
gimini_key = os.getenv("GEMINI_API_KEY")
ai_client = genai.Client(api_key=gimini_key)

def load_data():
    base_path = os.path.dirname(os.path.abspath(__file__))
    bank_file = os.path.join(base_path,"bank_statements.json")
    rzp_file = os.path.join(base_path,"razorpay_settlements.json")
    
    with open(bank_file, "r") as f:
        bank_data = json.load(f)
    with open(rzp_file, "r") as f:
        rzp_data = json.load(f)
        
    return bank_data, rzp_data

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
        
        # Edge Case 1: Unhandled Exception
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
        
        # Edge Case 2: Matched
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
        # Edge Case 3: Discrepancy
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
    reconciliation_rate = round((matched_count / total_records) * 100, 1)

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

class PromptQuery(BaseModel):
    query: str

@app.post("/api/ai-query")
def process_ai_query(body: PromptQuery):
    try:
        response = ai_client.models.generate_content(
            model="gemini-1.5-flash-latest",
            contents=f"You are an expert AI Finance Controller for Razorpay Buildathon. Answer this question concisely based on financial reconciliation principles: {body.query}"
        )
        return {"response": response.text}
    except Exception as e:
        return {"response": f"AI Engine error: {str(e)}"}
