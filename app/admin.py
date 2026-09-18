from sqladmin import Admin, ModelView
from . import models

class UserAdmin(ModelView, model=models.User):
    column_list = [models.User.id, models.User.username, models.User.email, models.User.plan_id]

class SubscriptionPlanAdmin(ModelView, model=models.SubscriptionPlan):
    column_list = [models.SubscriptionPlan.id, models.SubscriptionPlan.name, models.SubscriptionPlan.price, models.SubscriptionPlan.post_limit, models.SubscriptionPlan.image_limit]

class BillingHistoryAdmin(ModelView, model=models.BillingHistory):
    column_list = [models.BillingHistory.id, models.BillingHistory.user_id, models.BillingHistory.plan_id, models.BillingHistory.price, models.BillingHistory.start_date, models.BillingHistory.transaction_id]

def setup_admin(app, engine):
    admin = Admin(app, engine)
    admin.add_view(UserAdmin)
    admin.add_view(SubscriptionPlanAdmin)
    admin.add_view(BillingHistoryAdmin)
    return admin
