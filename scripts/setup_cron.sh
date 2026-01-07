set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================================"
echo "Daily Report Cron Job Setup"
echo "================================================"

# Get the absolute path to the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo -e "${GREEN}Project directory: ${PROJECT_DIR}${NC}"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed or not in PATH${NC}"
    exit 1
fi

PYTHON_PATH=$(which python3)
echo -e "${GREEN}Python path: ${PYTHON_PATH}${NC}"

# Create logs directory if it doesn't exist
LOG_DIR="${PROJECT_DIR}/logs"
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
    echo -e "${GREEN}Created logs directory: ${LOG_DIR}${NC}"
fi

# Create reports directory if it doesn't exist
REPORT_DIR="${PROJECT_DIR}/reports"
if [ ! -d "$REPORT_DIR" ]; then
    mkdir -p "$REPORT_DIR"
    echo -e "${GREEN}Created reports directory: ${REPORT_DIR}${NC}"
fi

# Test the report script
echo ""
echo "Testing report generation script..."
if ${PYTHON_PATH} "${PROJECT_DIR}/scripts/generate_daily_report.py"; then
    echo -e "${GREEN}✓ Report script test successful${NC}"
else
    echo -e "${RED}✗ Report script test failed${NC}"
    echo "Please check that all dependencies are installed (pip install -r requirements.txt)"
    exit 1
fi

# Create the cron job entry
CRON_ENTRY="0 20 * * * cd ${PROJECT_DIR} && ${PYTHON_PATH} ${PROJECT_DIR}/scripts/generate_daily_report.py >> ${LOG_DIR}/cron_daily_report.log 2>&1"

echo ""
echo "================================================"
echo "Cron Job Configuration"
echo "================================================"
echo "The following cron job will be added:"
echo ""
echo -e "${YELLOW}${CRON_ENTRY}${NC}"
echo ""
echo "This will run daily at 8:00 PM (20:00)"
echo ""

# Ask for confirmation
read -p "Do you want to add this cron job? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

# Backup existing crontab
echo ""
echo "Backing up existing crontab..."
crontab -l > "${PROJECT_DIR}/cron/crontab_backup_$(date +%Y%m%d_%H%M%S).txt" 2>/dev/null || true
echo -e "${GREEN}✓ Backup saved${NC}"

# Check if the cron job already exists
if crontab -l 2>/dev/null | grep -q "generate_daily_report.py"; then
    echo ""
    echo -e "${YELLOW}Warning: A similar cron job already exists${NC}"
    read -p "Do you want to replace it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove existing entry and add new one
        (crontab -l 2>/dev/null | grep -v "generate_daily_report.py"; echo "$CRON_ENTRY") | crontab -
        echo -e "${GREEN}✓ Cron job updated${NC}"
    else
        echo "Installation cancelled. Existing cron job unchanged."
        exit 0
    fi
else
    # Add the cron job
    (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
    echo -e "${GREEN}✓ Cron job added successfully${NC}"
fi

# Verify installation
echo ""
echo "================================================"
echo "Verification"
echo "================================================"
echo "Current crontab entries:"
crontab -l | grep "generate_daily_report.py" || echo "No entries found"

echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo "The daily report will be generated at 8:00 PM every day."
echo ""
echo "Useful commands:"
echo "  - View cron jobs:     crontab -l"
echo "  - Edit cron jobs:     crontab -e"
echo "  - Remove cron job:    crontab -e (then delete the line)"
echo "  - View logs:          tail -f ${LOG_DIR}/cron_daily_report.log"
echo "  - View reports:       ls -lh ${REPORT_DIR}"
echo "  - Test script:        ${PYTHON_PATH} ${PROJECT_DIR}/scripts/generate_daily_report.py"
echo ""
