"""
GitHub OAuth Configuration Template

To use GitHub authentication, you need to:

1. Create a GitHub OAuth App:
   - Go to GitHub Settings > Developer settings > OAuth Apps
   - Click "New OAuth App"
   - Set Application name: "GitFlow Studio"
   - Set Homepage URL: "http://localhost:8080"
   - Set Authorization callback URL: "http://localhost:8080/callback"
   - Click "Register application"

2. Copy your Client ID and Client Secret

3. Update the auth.py file with your credentials:
   - Replace 'your_github_oauth_app_client_id' with your actual Client ID
   - Replace 'your_github_oauth_app_client_secret' with your actual Client Secret

4. For production use, consider using environment variables:
   - Set GITHUB_CLIENT_ID environment variable
   - Set GITHUB_CLIENT_SECRET environment variable
   - Update auth.py to read from environment variables

Example environment variables:
export GITHUB_CLIENT_ID="your_client_id_here"
export GITHUB_CLIENT_SECRET="your_client_secret_here"
"""

# Example configuration (replace with your actual values)
GITHUB_CLIENT_ID = "your_github_oauth_app_client_id"
GITHUB_CLIENT_SECRET = "your_github_oauth_app_client_secret" 