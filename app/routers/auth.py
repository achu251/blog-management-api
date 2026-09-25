import os
import secrets

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..security import hash_password, verify_password, create_access_token

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Auth"])

# ---------------------------------------------------------
# Auth0 configuration
# ---------------------------------------------------------

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL")

oauth = OAuth()

oauth.register(
    name="auth0",
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    server_metadata_url=f"https://{AUTH0_DOMAIN}/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid profile email",
    },
)


# ---------------------------------------------------------
# Normal username/password registration
# ---------------------------------------------------------

@router.post(
    "/register",
    response_model=schemas.UserOut,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(models.User)
        .filter(
            (models.User.username == user_in.username)
            | (models.User.email == user_in.email)
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    basic_plan = (
        db.query(models.SubscriptionPlan)
        .filter(models.SubscriptionPlan.name == "Basic")
        .first()
    )

    new_user = models.User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        plan_id=basic_plan.id if basic_plan else None,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ---------------------------------------------------------
# Normal username/password login
# ---------------------------------------------------------

@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(models.User)
        .filter(models.User.username == form_data.username)
        .first()
    )

    if not user or not verify_password(
        form_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    return schemas.Token(access_token=access_token)


# ---------------------------------------------------------
# Google login
# ---------------------------------------------------------

@router.get("/google")
async def google_login(request: Request):
    if not AUTH0_CLIENT_ID or not AUTH0_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Auth0 configuration is missing",
        )

    return await oauth.auth0.authorize_redirect(
        request,
        AUTH0_CALLBACK_URL,
        connection="google-oauth2",
    )


# ---------------------------------------------------------
# Facebook login
# ---------------------------------------------------------

@router.get("/facebook")
async def facebook_login(request: Request):
    if not AUTH0_CLIENT_ID or not AUTH0_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Auth0 configuration is missing",
        )

    return await oauth.auth0.authorize_redirect(
        request,
        AUTH0_CALLBACK_URL,
        connection="facebook",
    )


# ---------------------------------------------------------
# Auth0 callback
# ---------------------------------------------------------

@router.get("/callback")
async def auth0_callback(
    request: Request,
    db: Session = Depends(get_db),
):
    try:
        token = await oauth.auth0.authorize_access_token(request)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Auth0 login failed: {str(exc)}",
        )

    userinfo = token.get("userinfo")

    if not userinfo:
        try:
            response = await oauth.auth0.get(
                "userinfo",
                token=token,
            )
            userinfo = response.json()
        except Exception as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to retrieve Auth0 user information: {str(exc)}",
            )

    auth0_id = userinfo.get("sub")
    email = userinfo.get("email")

    if not auth0_id:
        raise HTTPException(
            status_code=400,
            detail="Auth0 user ID was not provided",
        )

    if not email:
        raise HTTPException(
            status_code=400,
            detail="Email was not provided by Google/Facebook",
        )

    # -----------------------------------------------------
    # Find user by Auth0 ID
    # -----------------------------------------------------

    user = (
        db.query(models.User)
        .filter(models.User.auth0_id == auth0_id)
        .first()
    )

    # -----------------------------------------------------
    # If not found, try existing account by email
    # -----------------------------------------------------

    if not user:
        user = (
            db.query(models.User)
            .filter(models.User.email == email)
            .first()
        )

    # -----------------------------------------------------
    # Create new local user
    # -----------------------------------------------------

    if not user:
        username = (
            userinfo.get("nickname")
            or userinfo.get("name")
            or email.split("@")[0]
        )

        # Make username safe for your existing unique constraint
        username = username.replace(" ", "_")

        base_username = username
        counter = 1

        while (
            db.query(models.User)
            .filter(models.User.username == username)
            .first()
        ):
            username = f"{base_username}_{counter}"
            counter += 1

        basic_plan = (
            db.query(models.SubscriptionPlan)
            .filter(models.SubscriptionPlan.name == "Basic")
            .first()
        )

        user = models.User(
            username=username,
            email=email,
            hashed_password=hash_password(
                secrets.token_urlsafe(32)
            ),
            auth0_id=auth0_id,
            auth_provider="auth0",
            plan_id=basic_plan.id if basic_plan else None,
        )

        db.add(user)

    else:
        # Existing local account: connect it to Auth0
        user.auth0_id = auth0_id
        user.auth_provider = "auth0"

    db.commit()
    db.refresh(user)

    # -----------------------------------------------------
    # Create your existing application JWT
    # -----------------------------------------------------

    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    
    request.session["access_token"] = access_token
    request.session["user_id"] = user.id

    return RedirectResponse(
    url="/static/dashboard.html"
)