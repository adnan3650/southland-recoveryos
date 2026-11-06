"""Prepared Lambda entry point. Public deployment is not accepted until production gates pass."""

from mangum import Mangum

from backend.app.main import app

handler = Mangum(app, lifespan="off")
