from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_user
from ..invoice_utils import generate_invoice_pdf

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

@router.get("/plans", response_model=list[schemas.SubscriptionPlanOut])
def list_plans(db: Session = Depends(get_db)):
    return db.query(models.SubscriptionPlan).all()

@router.post("/subscribe", status_code=status.HTTP_200_OK)
def subscribe(
    req: schemas.SubscribeRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    plan = db.query(models.SubscriptionPlan).filter(models.SubscriptionPlan.name == req.plan_name).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
        
    current_user.plan_id = plan.id
    
    # Generate Billing History
    transaction_id = str(uuid.uuid4())
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30) # 1 month subscription
    
    invoice_path = generate_invoice_pdf(
        username=current_user.username,
        plan_name=plan.name,
        price=plan.price,
        start_date=start_date,
        end_date=end_date,
        transaction_id=transaction_id
    )
    
    billing = models.BillingHistory(
        user_id=current_user.id,
        plan_id=plan.id,
        price=plan.price,
        start_date=start_date,
        end_date=end_date,
        transaction_id=transaction_id,
        invoice_pdf_path=invoice_path
    )
    
    db.add(billing)
    db.commit()
    db.refresh(current_user)
    
    return {"message": "Subscribed successfully", "invoice_url": invoice_path}

@router.get("/billing", response_model=list[schemas.BillingHistoryOut])
def list_billing_history(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.BillingHistory).filter(models.BillingHistory.user_id == current_user.id).order_by(models.BillingHistory.start_date.desc()).all()
