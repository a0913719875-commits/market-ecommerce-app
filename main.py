from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import datetime
import requests

app = FastAPI()

# Data storage (to be replaced by actual database)
database = {
    "trading_rules": {
        "stop_loss_percentage": 7.0,
        "macd_buy_signal": False
    },
    "schedule_time": "09:10"
}

# Trading rules update request model
class TradingRulesUpdate(BaseModel):
    stop_loss_percentage: float
    macd_buy_signal: bool

# Schedule update request model
class ScheduleUpdate(BaseModel):
    schedule_time: str

# Push notification (dummy function)
def send_line_notification(user_id: str, message: str):
    # Dummy line notification sender
    print(f"Sending LINE notification to {user_id}: {message}")

# PATCH trading rules
@app.patch("/trading/rules")
async def update_trading_rules(update: TradingRulesUpdate):
    database["trading_rules"]["stop_loss_percentage"] = update.stop_loss_percentage
    database["trading_rules"]["macd_buy_signal"] = update.macd_buy_signal
    return {"success": True, "message": "交易邏輯已更新"}

# PATCH schedule
@app.patch("/schedule")
async def update_schedule(update: ScheduleUpdate):
    try:
        # Validate time format
        datetime.datetime.strptime(update.schedule_time, "%H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format")
    
    database["schedule_time"] = update.schedule_time
    return {"success": True, "message": "掃股時間已更新"}

# Example endpoint to demonstrate risk alert notification format improvement
@app.post("/alert/risk")
async def risk_alert():
    message = "RISK ALERT: 請注意，ETF 標的風險已超過設定閾值。"
    send_line_notification("U9f200ef6c095c25edd6aa44cd927fa1b", message)
    return {"success": True, "message": "風險警告已發送"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)