# Environment Configuration

This document describes the environment variables required for the VortexBerserker Hybrid Swarm trading engine.

## Required Environment Variables

### MEXC Exchange Credentials

The trading engine requires MEXC exchange API credentials to function. Without these, the engine will start but trading functionality will be disabled.

#### MEXC_API_KEY
- **Description**: Your MEXC API key
- **Required**: Yes (for trading functionality)
- **Example**: `mx0vglxxxxxxxxxxxxxxxx`
- **How to obtain**: 
  1. Log in to [MEXC Exchange](https://www.mexc.com/)
  2. Go to API Management
  3. Create a new API key
  4. Save the API key securely

#### MEXC_SECRET_KEY
- **Description**: Your MEXC API secret key
- **Required**: Yes (for trading functionality)
- **Example**: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **Security**: Keep this secret and never commit it to version control

## Setting Environment Variables

### On Render.com

1. Navigate to your service dashboard
2. Go to "Environment" tab
3. Click "Add Environment Variable"
4. Add both `MEXC_API_KEY` and `MEXC_SECRET_KEY`
5. Redeploy your service

### Locally (Development)

Create a `.env` file in the project root:

```bash
MEXC_API_KEY=your_api_key_here
MEXC_SECRET_KEY=your_secret_key_here
```

**Important**: The `.env` file is already in `.gitignore` - never commit it!

### In Docker

```bash
docker run -e MEXC_API_KEY=your_api_key \
           -e MEXC_SECRET_KEY=your_secret_key \
           your-image-name
```

## Behavior Without Credentials

If API credentials are not configured:

1. **Startup**: Engine will start normally
2. **Warnings**: You'll see warnings in the logs:
   ```
   ⚠️  MEXC API credentials not configured
   Trading functionality will be disabled
   Set MEXC_API_KEY and MEXC_SECRET_KEY environment variables to enable trading
   ```
3. **Trading**: No trades will be executed
4. **API Endpoints**: All API endpoints will still work
5. **Telemetry**: Will show idle slots

## Verifying Configuration

After setting credentials and redeploying, check the logs for:

```
✅ MEXC API credentials found
✅ MEXC Exchange initialized successfully
```

If you see errors like:

```
❌ Exchange initialization failed: AuthenticationError
   Check your MEXC_API_KEY and MEXC_SECRET_KEY credentials
```

This means:
- Credentials are set but invalid
- API key permissions are insufficient
- API key has been revoked

## Required API Permissions

Your MEXC API key must have the following permissions:
- **Spot Trading**: Read and Trade
- **Account Information**: Read
- **Market Data**: Read (usually enabled by default)

## Security Best Practices

1. **Use Read-Only Keys When Possible**: For testing, create read-only API keys
2. **Enable IP Whitelisting**: Restrict API key usage to specific IP addresses
3. **Rotate Keys Regularly**: Change your API keys periodically
4. **Use Separate Keys for Production/Development**: Never use production keys in development
5. **Monitor API Usage**: Check your MEXC account regularly for unexpected activity

## Troubleshooting

### "SCAN ERROR" in Logs

If you see errors like:
```
⚠️ SCAN ERROR SOL/USDT: mexc GET https://api.mexc.com/api/v3/...
```

This could mean:
1. **Invalid Credentials**: API key or secret is incorrect
2. **Insufficient Permissions**: API key doesn't have required permissions
3. **Rate Limiting**: Too many requests (Auto-Healer will handle this)
4. **IP Restriction**: Your IP is not whitelisted on MEXC

**Solution**: 
- Verify credentials are correct
- Check API key permissions in MEXC dashboard
- Enable IP whitelisting if required
- Wait for rate limit recovery (Auto-Healer handles this automatically)

### Missing Credentials Warning

If you see:
```
⚠️  MEXC API credentials not configured!
Set MEXC_API_KEY and MEXC_SECRET_KEY environment variables
```

**Solution**: Set the environment variables as described above and redeploy.

## Additional Configuration (Optional)

Future versions may support additional configuration options. Currently, these are the only required environment variables.

## Support

For issues with:
- **MEXC API Keys**: Contact MEXC support
- **Render.com Deployment**: Check Render documentation
- **Application Issues**: Check the [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
