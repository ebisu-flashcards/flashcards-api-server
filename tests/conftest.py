from fastapi.testclient import TestClient

from flashcards_server.main import app  # oauth2_scheme


client = TestClient(app)


# class MockOAuth(OAuth2):
#     def __init__(
#         self,
#         tokenUrl: str,
#         scheme_name: Optional[str] = None,
#         scopes: Optional[Dict[str, str]] = None,
#         description: Optional[str] = None,
#         auto_error: bool = True,
#     ):
#         if not scopes:
#             scopes = {}
#         flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
#         super().__init__(
#             flows=flows,
#             scheme_name=scheme_name,
#             description=description,
#             auto_error=auto_error,
#         )

#     async def __call__(self, request: Request) -> Optional[str]:
#         authorization: str = request.headers.get("Authorization")
#         scheme, param = get_authorization_scheme_param(authorization)
#         if not authorization or scheme.lower() != "bearer":
#             if self.auto_error:
#                 raise HTTPException(
#                     status_code=HTTP_401_UNAUTHORIZED,
#                     detail="Not authenticated",
#                     headers={"WWW-Authenticate": "Bearer"},
#                 )
#             else:
#                 return None
#         return param


# async def mock_auth(tokenUrl: Optional[str] = "token"):
#     return MockOAuth()


# app.dependency_overrides[oauth2_scheme] = override_dependency
