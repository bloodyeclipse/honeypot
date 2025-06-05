# honeypot
honeypot ~a cybersecurity tool designed to lure hackers into a controlled environment, mimicking a legitimate system to attract attacks

## Setup Instructions
 Before You Begin (All OSes)

1. **Edit the Configuration**:
   - Update the `CONFIG` dictionary in the script with your email details and preferred ports.
   - Change the fake responses if you want to simulate different services.

2. **Python Requirements**:
   - Ensure Python 3.6+ is installed
   - No additional packages needed (uses standard library)

### Fedora 42 Setup

1. **Install Python** (if not already installed):
   ```bash
   sudo dnf install python3
   ```

2. **Run the Honeypot**:
   ```bash
   python3 honeypot.py
   ```

3. **Run as a Service** (optional):
   - Create a service file `/etc/systemd/system/honeypot.service`:
     ```
     [Unit]
     Description=Python Honeypot Service
     After=network.target

     [Service]
     User=root
     ExecStart=/usr/bin/python3 /path/to/honeypot.py
     Restart=always

     [Install]
     WantedBy=multi-user.target
     ```
   - Enable and start the service:
     ```bash
     sudo systemctl daemon-reload
     sudo systemctl enable honeypot
     sudo systemctl start honeypot
     ```

4. **Firewall Configuration**:
   ```bash
   sudo firewall-cmd --add-port={22,80,443,3389,5900}/tcp --permanent
   sudo firewall-cmd --reload
   ```

### Windows 11 Setup

1. **Install Python**:
   - Download from [python.org](https://www.python.org/downloads/windows/)
   - Check "Add Python to PATH" during installation

2. **Run the Honeypot**:
   - Open Command Prompt as Administrator
   ```cmd
   python honeypot.py
   ```

3. **Run as a Service** (optional):
   - Use NSSM (Non-Sucking Service Manager):
     ```cmd
     choco install nssm
     nssm install Honeypot python.exe "C:\path\to\honeypot.py"
     nssm start Honeypot
     ```

4. **Firewall Configuration**:
   - Open Windows Defender Firewall with Advanced Security
   - Add new inbound rules for TCP ports 22, 80, 443, 3389, 5900

### macOS Setup

1. **Install Python**:
   ```bash
   brew install python
   ```

2. **Run the Honeypot**:
   ```bash
   python3 honeypot.py
   ```

3. **Run as a Service** (optional):
   - Create a launchd plist file `~/Library/LaunchAgents/local.honeypot.plist`:
     ```xml
     <?xml version="1.0" encoding="UTF-8"?>
     <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
     <plist version="1.0">
     <dict>
         <key>Label</key>
         <string>local.honeypot</string>
         <key>ProgramArguments</key>
         <array>
             <string>/usr/local/bin/python3</string>
             <string>/path/to/honeypot.py</string>
         </array>
         <key>RunAtLoad</key>
         <true/>
         <key>KeepAlive</key>
         <true/>
     </dict>
     </plist>
     ```
   - Load the service:
     ```bash
     launchctl load ~/Library/LaunchAgents/local.honeypot.plist
     ```

4. **Firewall Configuration**:
   - Go to System Preferences > Security & Privacy > Firewall > Firewall Options
   - Add the Python application and ensure it's set to allow incoming connections

## Security Considerations

1. **Run with minimal privileges** - Don't run as root unless necessary
2. **Isolate the honeypot** - Run on a separate machine or VM
3. **Monitor resource usage** - The honeypot could be used in DDoS attacks
4. **Regularly check logs** - For any unexpected activity
5. **Use dedicated email** - Don't use your primary email account

## Customization Options

1. **Add more ports** - Edit the `listen_ports` list
2. **Change fake responses** - Update the `fake_responses` dictionary
3. **Modify reporting frequency** - Change the `time.sleep(3600)` value
4. **Add more logging** - Extend the `handle_connection` method
5. **Implement geolocation** - Add a library like `geoip2` to track attacker locations
