#!/bin/bash

# Script to extract Heroku config variables to a .env file
# Usage: ./heroku-to-dotenv.sh your-app-name

if [ -z "$1" ]; then
  echo "Please provide your Heroku app name as an argument"
  echo "Usage: $0 your-app-name"
  exit 1
fi

APP_NAME=$1
ENV_FILE=".env"

echo "Retrieving environment variables from Heroku app: $APP_NAME"
echo "Writing to $ENV_FILE..."

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
  echo "Error: Heroku CLI is not installed. Please install it first."
  exit 1
fi

# Check if logged in to Heroku
if ! heroku auth:whoami &> /dev/null; then
  echo "Please log in to Heroku first:"
  heroku login
fi

# Check if app exists
if ! heroku apps:info --app $APP_NAME &> /dev/null; then
  echo "Error: App '$APP_NAME' not found or you don't have access to it."
  exit 1
fi

# Backup existing .env file if it exists
if [ -f "$ENV_FILE" ]; then
  BACKUP_FILE="$ENV_FILE.backup.$(date +%Y%m%d%H%M%S)"
  echo "Backing up existing $ENV_FILE to $BACKUP_FILE"
  cp "$ENV_FILE" "$BACKUP_FILE"
fi

# Get config vars and format them as KEY=VALUE in .env file
echo "# Environment variables from Heroku app: $APP_NAME" > $ENV_FILE
echo "# Generated on $(date)" >> $ENV_FILE
echo "" >> $ENV_FILE

# Extract config vars
heroku config --app $APP_NAME | tail -n +2 | while read line; do
  # Skip empty lines
  if [ -z "$line" ]; then
    continue
  fi
  
  # Extract key and value
  KEY=$(echo $line | awk '{print $1}')
  VALUE=$(echo $line | cut -d':' -f2- | sed 's/^ //')
  
  # Handle values with spaces or special characters
  if [[ "$VALUE" == *" "* || "$VALUE" == *"&"* || "$VALUE" == *";"* || "$VALUE" == *"#"* ]]; then
    echo "$KEY=\"$VALUE\"" >> $ENV_FILE
  else
    echo "$KEY=$VALUE" >> $ENV_FILE
  fi
done

echo "Done! Environment variables have been saved to $ENV_FILE"
echo "You may need to manually check the file for any complex values that weren't parsed correctly."
