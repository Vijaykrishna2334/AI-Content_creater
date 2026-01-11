# Run the cleanup script for users.json
python "$(Split-Path -Parent $MyInvocation.MyCommand.Definition)\cleanup_users_uploaded_newsletters.py"
