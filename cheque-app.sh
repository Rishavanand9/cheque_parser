#!/bin/bash

# Set the path to your project directory
PROJECT_DIR="/path/to/your/project"

# Function to start the application
start_app() {
    echo "Starting the application..."
    cd $PROJECT_DIR && docker-compose up -d
}

# Function to stop the application
stop_app() {
    echo "Stopping the application..."
    cd $PROJECT_DIR && docker-compose down
}

# Function to restart the application
restart_app() {
    stop_app
    start_app
}

# Function to show the status of the application
status_app() {
    echo "Application status:"
    cd $PROJECT_DIR && docker-compose ps
}

# Main script logic
case "$1" in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    status)
        status_app
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0