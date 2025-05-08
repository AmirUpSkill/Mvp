import logging 
from  fastapi import HTTPException , status , Security 
from fastapi.security import OAuth2PasswordBearer
from jose import jwt , JWTError , ExpiredSignatureError 
from pydantic import ValidationError

from app.core.config import settings 

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/gw/token")

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials or token expired",
    headers={"WWW-Authenticate": "Bearer"},
)

INVALID_TOKEN_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid token format or signature",
    headers={"WWW-Authenticate": "Bearer"},
)

def decode_and_validate_token(token: str) -> dict:
    """ 
    Decodes and validates the JWT token passed by the API Gateway 

    Args:
        token : The raw JWT string  from the Authorization header.

    Returns:
        dict:  The dictionary of claims (payload) if the token is valid.

    Raises:
        HTTPException (401) : If the token is invalid , expired, or has an invalid signature.


    """

    try:
        logger.debug(f"Attempting to decode and validate token: {token}")
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
        )
        logger.debug("JWT validation successful.")
        return payload
    except ExpiredSignatureError:
        logger.error("Token has expired.")
        raise CREDENTIALS_EXCEPTION
    except JWTError as e:
        logger.warning(f"JWT validation failed: Invalid token. Error: {e}")
        raise INVALID_TOKEN_EXCEPTION
    except Exception as e:
        logger.error(f"Unexpected error during JWT decoding: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error during token processing: {e}"
        )

async def get_current_user_claims(token: str = Security(oauth2_scheme)) -> dict:
    claims = decode_and_validate_token(token)
    return claims
