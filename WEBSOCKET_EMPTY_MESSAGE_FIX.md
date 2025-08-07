# WebSocket Empty Message Issue - Analysis and Fix

## Problem Description

The WebSocket connection in Odoo 17 is experiencing issues where empty messages are being received, causing the following log messages:

```
8/7/2025, 12:10:40 PM - [onClose] 1001 <empty string> websocket_worker_bundle:63:59
8/7/2025, 12:10:43 PM - [onOpen] websocket_worker_bundle:74:45
8/7/2025, 12:10:43 PM - [onMessage] 
```

## Root Cause Analysis

### 1. Empty Message Reception
- The WebSocket worker is receiving empty messages from the server
- These empty messages are being logged but not properly handled
- The connection is closing with code 1001 (GOING_AWAY) and reopening

### 2. Message Processing Issues
- Empty messages are being passed through the WebSocket frame processing
- The JSON parsing fails on empty messages but the error isn't properly handled
- The server-side message validation is insufficient

### 3. Potential Causes
- Network issues causing frame corruption
- Server-side WebSocket implementation sending empty frames
- Proxy or load balancer interference
- Browser WebSocket implementation issues

## Implemented Fixes

### 1. Client-Side Improvements (websocket_worker.js)

**Enhanced Message Validation:**
```javascript
_onWebsocketMessage(messageEv) {
    // Check for empty or null messages
    if (!messageEv.data || messageEv.data === '') {
        if (this.isDebug) {
            console.warn(
                `%c${new Date().toLocaleString()} - [onMessage] Empty message received`,
                "color: #f90; font-weight: bold;"
            );
        }
        return; // Skip processing empty messages
    }

    let notifications;
    try {
        notifications = JSON.parse(messageEv.data);
    } catch (error) {
        if (this.isDebug) {
            console.error(
                `%c${new Date().toLocaleString()} - [onMessage] JSON parse error:`,
                "color: #f00; font-weight: bold;",
                error,
                "Raw data:",
                messageEv.data
            );
        }
        return; // Skip processing invalid JSON
    }

    // Validate notifications structure
    if (!Array.isArray(notifications) || notifications.length === 0) {
        if (this.isDebug) {
            console.warn(
                `%c${new Date().toLocaleString()} - [onMessage] Invalid notifications format:`,
                "color: #f90; font-weight: bold;",
                notifications
            );
        }
        return;
    }

    this.lastNotificationId = notifications[notifications.length - 1].id;
    this.broadcast("notification", notifications);
}
```

### 2. Server-Side Improvements (websocket.py)

**Enhanced Message Validation:**
```python
def serve_websocket_message(self, message):
    # Validate message is not empty or None
    if not message or message.strip() == '':
        _logger.warning("Received empty WebSocket message, skipping processing")
        return
        
    try:
        jsonrequest = json.loads(message)
        event_name = jsonrequest['event_name']  # mandatory
    except KeyError as exc:
        _logger.error(f"Missing key {exc.args[0]!r} in WebSocket request: {message}")
        raise InvalidWebsocketRequest(
            f'Key {exc.args[0]!r} is missing from request'
        ) from exc
    except ValueError as exc:
        _logger.error(f"Invalid JSON in WebSocket message: {message}, error: {exc}")
        raise InvalidWebsocketRequest(
            f'Invalid JSON data, {exc.args[0]}'
        ) from exc
```

**Enhanced Frame Processing:**
```python
def get_messages(self):
    while self.state is not ConnectionState.CLOSED:
        try:
            # ... existing code ...
            if self.__socket in readables:
                message = self._process_next_message()
                if message is not None:
                    # Additional validation for empty messages
                    if isinstance(message, str) and message.strip() == '':
                        _logger.warning("Received empty message from WebSocket, skipping")
                        continue
                    yield message
        except Exception as exc:
            self._handle_transport_error(exc)
```

## Debug Tools

### WebSocket Debug Script
A Python script (`websocket_debug.py`) has been created to help debug WebSocket connections:

**Features:**
- Connects to Odoo WebSocket endpoint
- Monitors all incoming messages
- Detects empty or malformed messages
- Provides detailed logging
- Helps identify the root cause of issues

**Usage:**
```bash
python3 websocket_debug.py
```

## Testing the Fixes

### 1. Enable Debug Mode
To see the enhanced logging, enable debug mode in your browser console or Odoo configuration.

### 2. Monitor Logs
Watch for the following new log messages:
- `Empty message received` - When empty messages are detected
- `JSON parse error` - When invalid JSON is received
- `Invalid notifications format` - When message structure is invalid

### 3. Check Server Logs
Monitor the Odoo server logs for:
- `Received empty WebSocket message, skipping processing`
- `Received empty message from WebSocket, skipping`

## Expected Behavior After Fix

1. **Empty messages** will be logged but not processed
2. **Invalid JSON** will be logged with detailed error information
3. **Connection stability** should improve
4. **Better error reporting** for debugging

## Additional Recommendations

### 1. Network Configuration
- Check for proxy or load balancer issues
- Verify WebSocket upgrade headers are properly handled
- Ensure no network equipment is interfering with WebSocket frames

### 2. Server Configuration
- Monitor WebSocket connection limits
- Check for memory issues affecting WebSocket handling
- Verify database connection pool health

### 3. Browser Compatibility
- Test with different browsers
- Check for browser-specific WebSocket implementation issues
- Verify SharedWorker vs Worker fallback behavior

## Monitoring

After implementing these fixes, monitor:

1. **Connection stability** - Fewer disconnections
2. **Message processing** - No more empty message errors
3. **Performance** - Improved WebSocket responsiveness
4. **Error logs** - Reduced WebSocket-related errors

## Files Modified

1. `odoo17/addons/bus/static/src/workers/websocket_worker.js`
   - Enhanced message validation
   - Better error handling
   - Improved debug logging

2. `odoo17/addons/bus/websocket.py`
   - Added empty message validation
   - Enhanced error logging
   - Improved frame processing

3. `websocket_debug.py` (new file)
   - Debug script for WebSocket testing

4. `WEBSOCKET_EMPTY_MESSAGE_FIX.md` (new file)
   - This documentation

## Next Steps

1. **Deploy the fixes** to your Odoo instance
2. **Monitor the logs** for the new debug messages
3. **Run the debug script** to verify WebSocket behavior
4. **Test with different browsers** and network conditions
5. **Monitor connection stability** over time

The fixes should resolve the empty message issue and provide better visibility into WebSocket problems for future debugging.