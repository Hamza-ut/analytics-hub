# 1. Bring the Python Operating System into the room
FROM python:3.11-slim

# 2. Prevent Python from generating unnecessary cache clutter
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Create and step inside a clean development workbench
WORKDIR /app

# 4. Copy ONLY the ingredients list into our container workspace
COPY requirements.txt /app/

# 5. Install the Python packages directly into the container's global space
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy every file from our current backend folder into the container /app folder
# (Docker automatically respects your .dockerignore and skips the media/ folder!)
COPY . /app/

# Copy your entrypoint gatekeeper script out to the root file level and make it executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 7. Use the entrypoint script to handle assets/migrations/superusers on boot,
# then hand control over to the Gunicorn command
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]