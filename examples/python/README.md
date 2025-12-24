# OpenAlgo Python Examples Configuration

This directory contains Python example scripts for the OpenAlgo trading platform. All scripts have been updated to use centralized configuration parameters.

## Configuration Setup

### 1. Create Configuration File

First, copy the sample configuration file:
```bash
cd examples/python
cp config.py.sample config.py
```

### 2. Update Configuration File

Edit the `config.py` file with your actual OpenAlgo credentials:

```python
# OpenAlgo API Configuration
API_KEY = "your-actual-api-key"        # Replace with your API key from OpenAlgo portal
HOST = "http://127.0.0.1:5000"         # Replace with your OpenAlgo server host
WS_URL = "ws://127.0.0.1:8765"         # Replace with your WebSocket server URL
```

### 3. Configuration Examples

**Local Development:**
```python
API_KEY = "7653f710c940cdf1d757b5a7d808a60f43bc7e9c0239065435861da2869ec0fc"
HOST = "http://127.0.0.1:5000"
WS_URL = "ws://127.0.0.1:8765"
```

**Cloud Deployment (AWS EC2):**
```python
API_KEY = "7653f710c940cdf1d757b5a7d808a60f43bc7e9c0239065435861da2869ec0fc"
HOST = "http://ec2-xx-xxx-xxx-xxx.region.compute.amazonaws.com:5000"
WS_URL = "ws://ec2-xx-xxx-xxx-xxx.region.compute.amazonaws.com:8765"
```

**Custom Server:**
```python
API_KEY = "7653f710c940cdf1d757b5a7d808a60f43bc7e9c0239065435861da2869ec0fc"
HOST = "http://your-server-ip:5000"
WS_URL = "ws://your-server-ip:8765"
```

## Updated Scripts

All the following scripts now use the centralized configuration:

### WebSocket Feed Scripts
- `depth_20_example.py` - 20-level market depth feed
- `depth_50_example.py` - 50-level market depth feed
- `depth_example.py` - Standard depth feed
- `ltp_example.py` - Last Traded Price feed
- `quote_example.py` - Quote feed
- `multiquotes_example.py` - Multiple quotes feed

### Trading Strategy Scripts
- `ema_crossover.py` - EMA crossover strategy
- `supertrend.py` - Supertrend indicator strategy
- `stoploss_example.py` - Stop loss implementation
- `straddle_with_stops.py` - Straddle with stop losses
- `straddle_scheduler.py` - Scheduled straddle strategy

### Option Chain & Analysis Scripts
- `optionchain_example.py` - Option chain data
- `flask_optionchain.py` - Flask web app for option chain
- `expiry_dates.py` - Expiry date extraction
- `heatmap.py` - Market heatmap visualization
- `placing ATM order.py` - ATM order placement

## Usage

1. **Create Configuration File**: Copy `config.py.sample` to `config.py`
2. **Update Configuration**: Edit `config.py` with your actual credentials
3. **Run Any Script**: All scripts will automatically use your configuration
4. **No Code Changes Needed**: Scripts will pick up API_KEY, HOST, and WS_URL from config.py

## Security Notes

- **The `config.py` file is gitignored** to prevent accidental commits of API keys
- **Use the `config.py.sample`** as a template for new setups
- **Never commit your actual API keys** to version control
- Consider using environment variables for production deployments
- Keep your `config.py` file secure and don't share it publicly

## Setup Instructions

```bash
# 1. Navigate to the python examples directory
cd examples/python

# 2. Copy the sample config file
cp config.py.sample config.py

# 3. Edit config.py with your actual credentials
# (Use any text editor to update API_KEY, HOST, and WS_URL)

# 4. Run any script
python ltp_example.py
```

## Example Usage

```bash
# After updating config.py with your credentials
python ltp_example.py
python ema_crossover.py
python optionchain_example.py
```

## Migration from Old Format

If you have existing scripts with hardcoded credentials, they've been automatically updated to use:

```python
from config import API_KEY, HOST, WS_URL

client = api(
    api_key=API_KEY,
    host=HOST,
    ws_url=WS_URL  # Only for WebSocket-enabled scripts
)
```

## Troubleshooting

1. **Import Error**: Make sure `config.py` is in the same directory as the script
2. **Connection Error**: Verify your HOST and WS_URL are correct and accessible
3. **Authentication Error**: Check that your API_KEY is valid and active