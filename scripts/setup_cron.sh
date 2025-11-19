#!/bin/bash
#
# Setup cron jobs for ROOK's daily reading schedule
# Run this script to install the cron jobs
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
READER_SCRIPT="$SCRIPT_DIR/daily_reader.py"

echo "Setting up ROOK's daily reading schedule..."

# Create cron jobs
# Note: Times are in UTC. Adjust for your timezone.
# 6am UTC = 6am GMT
# 12pm UTC = 12pm GMT  
# 6pm UTC = 6pm GMT

CRON_JOBS="
# ROOK Daily Reading Schedule
0 6 * * * cd $SCRIPT_DIR/.. && python3 scripts/daily_reader.py morning >> /tmp/rook_reading.log 2>&1
0 12 * * * cd $SCRIPT_DIR/.. && python3 scripts/daily_reader.py midday >> /tmp/rook_reading.log 2>&1
0 18 * * * cd $SCRIPT_DIR/.. && python3 scripts/daily_reader.py evening >> /tmp/rook_reading.log 2>&1
"

# Add to crontab
(crontab -l 2>/dev/null; echo "$CRON_JOBS") | crontab -

echo "✅ Cron jobs installed!"
echo ""
echo "Schedule:"
echo "  - 6am:  Morning reading (overnight news)"
echo "  - 12pm: Midday reading (breaking news, social media)"
echo "  - 6pm:  Evening reading (analysis, academic)"
echo ""
echo "Logs: /tmp/rook_reading.log"
echo ""
echo "To view current crontab:"
echo "  crontab -l"
echo ""
echo "To remove cron jobs:"
echo "  crontab -e  # then delete the ROOK lines"
