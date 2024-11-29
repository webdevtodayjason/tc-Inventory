#!/bin/bash

# Apply database migrations
railway run flask db upgrade

# Create initial data
railway run flask create-category
railway run flask create-cpus
railway run flask create-tags

# Create admin user using environment variables
railway run flask create-admin 