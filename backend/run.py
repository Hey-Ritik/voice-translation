
import uvicorn
import logging

# Configure logging to show timestamps
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Initializing application and loading models...")
    # Import here to avoid early config loading if needed, but it's fine
    from app.main import app
    from app.services.model_loader import ModelLoader

    # Pre-load models in the main thread
    try:
        ModelLoader.get_instance().load_models()
    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        exit(1)

    logger.info("Models loaded. Starting server...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
