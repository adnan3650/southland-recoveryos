import os
from uuid import uuid4

import jwt
from fastapi import HTTPException, Request, Response


def owner(request: Request, response: Response):
    if os.getenv("APP_MODE", "local") == "aws":
        issuer = os.environ["COGNITO_ISSUER"]
        header = request.headers.get("authorization", "")
        if not header.startswith("Bearer "):
            raise HTTPException(401, "Sign in required")
        token = header[7:]
        try:
            jwks = request.app.state.jwks
            key = jwks.get_signing_key_from_jwt(token)
            claims = jwt.decode(
                token, key.key, algorithms=["RS256"], audience=os.environ["COGNITO_CLIENT_ID"], issuer=issuer
            )
            if claims.get("token_use") != "id":
                raise ValueError("ID token required")
            return claims["sub"]
        except Exception:
            raise HTTPException(401, "Invalid sign-in token") from None
    session = request.cookies.get("recovery_owner")
    try:
        from uuid import UUID

        UUID(session or "")
    except (ValueError, TypeError):
        session = str(uuid4())
        response.set_cookie("recovery_owner", session, httponly=True, samesite="strict", max_age=2592000, path="/")
    return session
