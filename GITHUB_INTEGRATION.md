# GitHub Integration for GitFlow Studio

GitFlow Studio now supports GitHub authentication and repository management directly from the terminal.

## Features

- **GitHub OAuth Authentication**: Secure login using GitHub OAuth
- **Repository Listing**: View all your GitHub repositories
- **Repository Cloning**: Clone repositories directly to your local machine
- **Repository Search**: Search GitHub repositories
- **Secure Token Storage**: Encrypted storage of access tokens

## Setup

### 1. Create GitHub OAuth App

1. Go to [GitHub Settings > Developer settings > OAuth Apps](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Fill in the following details:
   - **Application name**: `GitFlow Studio`
   - **Homepage URL**: `http://localhost:8080`
   - **Authorization callback URL**: `http://localhost:8080/callback`
4. Click "Register application"
5. Copy your **Client ID** and **Client Secret**

### 2. Configure Credentials

You have two options to configure your GitHub credentials:

#### Option A: Environment Variables (Recommended)

```bash
export GITHUB_CLIENT_ID="your_client_id_here"
export GITHUB_CLIENT_SECRET="your_client_secret_here"
```

#### Option B: Direct File Edit

Edit `studio/github/auth.py` and replace:
- `"your_github_oauth_app_client_id"` with your actual Client ID
- `"your_github_oauth_app_client_secret"` with your actual Client Secret

## Usage

### Interactive Mode

Start GitFlow Studio in interactive mode:

```bash
python -m studio --interactive
```

#### GitHub Commands in Interactive Mode

- `github login` - Login to your GitHub account
- `github logout` - Logout from GitHub
- `github repos` - List your GitHub repositories
- `github clone <repo_name>` - Clone a repository by name
- `github search <query>` - Search GitHub repositories

### Command Line Mode

#### Login/Logout

```bash
# Login to GitHub
python -m studio --github-login

# Logout from GitHub
python -m studio --github-logout
```

#### Repository Operations

```bash
# List repositories
python -m studio github repos

# Clone a repository
python -m studio github clone my-repo-name

# Clone to specific path
python -m studio github clone my-repo-name --path /path/to/clone

# Search repositories
python -m studio github search "python git workflow"

# Search with limit
python -m studio github search "python" --limit 10
```

## Security

- Access tokens are encrypted using Fernet encryption
- Tokens are stored securely using the system keyring
- OAuth flow includes CSRF protection with state parameters
- All sensitive data is encrypted before storage

## Dependencies

The GitHub integration requires these additional dependencies:

```
PyGithub>=1.59.0
cryptography>=41.0.0
keyring>=24.0.0
```

These are automatically included in the updated `requirements.txt`.

## Troubleshooting

### "GitHub OAuth credentials not configured"

This error occurs when the GitHub OAuth credentials are not set up. Follow the setup instructions above to configure your credentials.

### "Not authenticated. Please login first"

You need to login to GitHub before using repository features. Use `github login` command.

### Browser doesn't open automatically

If the browser doesn't open automatically during login, manually visit the URL shown in the terminal.

### Port 8080 already in use

The OAuth callback server uses port 8080. If this port is already in use, you may need to:
1. Stop the service using port 8080
2. Or modify the port in the auth.py file

## Example Workflow

```bash
# 1. Start interactive mode
python -m studio --interactive

# 2. Login to GitHub
gitflow-studio> github login

# 3. List your repositories
gitflow-studio> github repos

# 4. Clone a repository
gitflow-studio> github clone my-project

# 5. Set it as current repository
gitflow-studio> discover
gitflow-studio> 1

# 6. Now you can use all Git operations
gitflow-studio> status
gitflow-studio> log
gitflow-studio> branches
```

## API Permissions

The GitHub OAuth app requests the following permissions:
- `repo` - Full control of private repositories
- `user` - Read access to user profile

These permissions allow GitFlow Studio to:
- List your repositories
- Clone private repositories
- Access repository information
- Search repositories

## Development

To modify the GitHub integration:

1. **Authentication**: Edit `studio/github/auth.py`
2. **Repository Operations**: Edit `studio/github/repos.py`
3. **CLI Integration**: Edit `studio/cli.py`

The integration uses the GitHub REST API v3 and follows GitHub's best practices for OAuth applications. 