#!/bin/bash

# Add environment variables to Vercel
echo "Adding environment variables to Vercel..."

# DATABASE_URL
echo "postgresql://neondb_owner:npg_Asb4ahlrFHg5@ep-calm-union-ab7g1jas-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require" | vercel env add DATABASE_URL production

# SECRET_KEY
echo "your_secret_key_here_change_in_production" | vercel env add SECRET_KEY production

# CORS_ORIGINS
echo "https://equipment-office-dashboard.vercel.app,https://equipment-driver-app.vercel.app" | vercel env add CORS_ORIGINS production

# ANTHROPIC_API_KEY (if available)
if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "$ANTHROPIC_API_KEY" | vercel env add ANTHROPIC_API_KEY production
fi

echo "Environment variables added successfully!"
