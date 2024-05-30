# Use an official Python runtime as a parent image
FROM python:3

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script and any other necessary files
COPY . .

# Copy the toloka2MediaServer directory
COPY toloka2MediaServer /app/toloka2MediaServer

# Add the config folder as a volume
VOLUME /app/toloka2MediaServer/data

# Define the default cron schedule
ENV CRON_SCHEDULE="0 8 * * *"

# Add the cron job to run toloka2transmission
ADD crontab /etc/cron.d/cron-job
RUN chmod 0644 /etc/cron.d/cron-job
RUN touch /var/log/cron.log

# Start cron service
CMD cron && tail -f /var/log/cron.log

# Make port available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV PORT 8000

# Run app.py when the container launches
CMD ["python", "-m", "toloka2MediaServerWeb"]