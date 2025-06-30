# Stage 1: Builder
# Use a lightweight Python base image for building
FROM python:3.12-slim AS builder

# Set the working directory inside the container
WORKDIR /app

# Install Poetry, the dependency manager
RUN pip install poetry

# Configure Poetry to create the virtual environment inside the project directory
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

# Copy only the dependency configuration files to leverage Docker cache
COPY pyproject.toml poetry.lock ./

# Install production dependencies only, without development dependencies or the project itself
RUN poetry install --only main --no-root

# Stage 2: Final
# Start a new, clean image from the same lightweight Python base
FROM python:3.12-slim AS final

# Set the working directory inside the container
WORKDIR /app

# Copy the installed virtual environment from the builder stage
# This ensures all production dependencies are available
COPY --from=builder /app/.venv /app/.venv

# Add the virtual environment's bin directory to the PATH
# This allows direct execution of installed packages like uvicorn
ENV PATH="/app/.venv/bin:$PATH"

# Copy the application source code into the final image
# Only the 'src/aurora_platform' directory is needed for the application to run
COPY src/aurora_platform ./aurora_platform

# Expose the port on which the FastAPI application will listen
# Cloud Run typically expects applications to listen on port 8080
EXPOSE 8080

# Define the command to run the application using uvicorn
# It listens on all interfaces (0.0.0.0) on port 8080
CMD ["python", "-m", "uvicorn", "aurora_platform.main:app", "--host", "0.0.0.0", "--port", "8080"]