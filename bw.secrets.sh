1. Login (non-interactive)
export BW_CLIENTID="organization.xxx"
export BW_CLIENTSECRET="yyy"

SESSION=$(bw login --apikey --raw)
2. Unlock vault (non-interactive)
export BW_PASSWORD="master-password"

SESSION_KEY=$(bw unlock --passwordenv BW_PASSWORD --raw)
3. Use vault
bw list items --session $SESSION_KEY

or:

bw sync --session $SESSION_KEY
