# Use the official MySQL image as the base image
FROM mysql:8.0-debian
RUN apt-get update && apt-get install -y --no-install-recommends \
vim \
nano \
net-tools \
mysql-client

# Set environment variables for MySQL configuration
ENV MYSQL_ROOT_PASSWORD=root_password
ENV MYSQL_DATABASE=flask_crud
ENV MYSQL_USER=sql
ENV MYSQL_PASSWORD=sql1245

# Expose the MySQL port
EXPOSE 3306

# Add any custom initialization SQL scripts (optional)
# Copy .sql files into the Docker image to be executed during initialization
COPY ./users_db.sql /docker-entrypoint-initdb.d/

# The MySQL server will automatically initialize and run
