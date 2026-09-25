from fastapi import APIRouter
from app.api.v1.routes import health, auth, profile, datasets, preprocessing, training, analytics, predictions, monitoring, deployments

api_router = APIRouter()

# Group all version 1 route modules here
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(preprocessing.router, prefix="/preprocessing", tags=["preprocessing"])
api_router.include_router(training.router, prefix="/training", tags=["training"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(deployments.router, prefix="/deployments", tags=["deployments"])

