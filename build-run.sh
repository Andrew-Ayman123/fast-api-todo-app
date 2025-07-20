
#!/bin/bash

# Load environment variables from .env file
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | grep -v '^$' | sed 's/#.*$//')

fi

# Start PostgreSQL Docker container
echo "Starting PostgreSQL Docker container..."

# Stop and remove existing container if it exists
if docker ps -a --format 'table {{.Names}}' | grep -q postgres-todo; then
    echo "Stopping and removing existing postgres-todo container..."
    docker stop postgres-todo
    docker rm postgres-todo
fi

docker run -d \
    --name postgres-todo \
    -e POSTGRES_DB=$DATABASE_NAME \
    -e POSTGRES_USER=$DATABASE_USER \
    -e POSTGRES_PASSWORD=$DATABASE_PASSWORD \
    -p $DATABASE_PORT:5432 \
    postgres:15

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
sleep 2

# Check if PostgreSQL is ready
until docker exec postgres-todo pg_isready -U $DATABASE_USER -d $DATABASE_NAME; do
    echo "Waiting for PostgreSQL to start..."
    sleep 2
done

echo "PostgreSQL is ready!"


echo "Setup completed successfully!"


