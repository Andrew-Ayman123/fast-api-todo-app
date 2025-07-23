
#!/bin/bash

# Load environment variables from .env file
if [ -f ".env" ]; then
    export $(grep -v '^#' pytest.env | grep -v '^$' | sed 's/#.*$//')

fi

source ./.venv/bin/activate

# Start PostgreSQL Docker container
echo "Starting PostgreSQL Docker container..."

# Stop and remove existing container if it exists
if docker ps -a --format 'table {{.Names}}' | grep -q postgres-todo-test; then
    echo "Stopping and removing existing postgres-todo-test container..."
    docker stop postgres-todo-test
    docker rm postgres-todo-test
fi

docker run -d \
    --name postgres-todo-test \
    -e POSTGRES_DB=$DATABASE_NAME \
    -e POSTGRES_USER=$DATABASE_USER \
    -e POSTGRES_PASSWORD=$DATABASE_PASSWORD \
    -p $DATABASE_PORT:5432 \
    postgres:15

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
sleep 2

# Check if PostgreSQL is ready
until docker exec postgres-todo-test pg_isready -U $DATABASE_USER -d $DATABASE_NAME; do
    echo "Waiting for PostgreSQL to start..."
    sleep 2
done

echo "PostgreSQL is ready!"

# Run Alembic migrations
echo "Running Alembic migrations..."


# Run pending migrations
echo "Applying database migrations..."
alembic -x url=$DATABASE_URL_ALEMBIC upgrade head

echo "Database migrations completed successfully!"

echo "Setup completed successfully!"


