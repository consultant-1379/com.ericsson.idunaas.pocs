# Use the official Python image as the base image
FROM python:3.9

# Install PostgreSQL client and Nginx
RUN apt-get update && \
    apt-get install -y postgresql-client nginx

# Install Gunicorn
RUN pip install gunicorn


# Set the working directory
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project to the working directory
COPY . .

# Set the environment variables for PostgreSQL
ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD postgres
ENV POSTGRES_DB mydb


# Collect static files
RUN python manage.py collectstatic --noinput 

# Copy the Nginx configuration file
COPY nginx/nginx.conf /etc/nginx/nginx.conf


# Add the following lines at the end of your Dockerfile
CMD ["sh", "-c", "python manage.py makemigrations --noinput && python manage.py migrate && gunicorn inventorytool.wsgi:application --bind 0.0.0.0:8000"]
