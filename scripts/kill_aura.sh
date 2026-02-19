#!/bin/bash
# AURA 2.0 - EMERGENCY STOP & PROCESS MANAGEMENT
# Safely or forcefully terminates all AURA processes

echo "=========================================="
echo "🛑 AURA 2.0 - Process Manager"
echo "=========================================="
echo ""

# Function to check if process is running
check_process() {
    pgrep -f "$1" > /dev/null 2>&1
    return $?
}

# Function to count AURA processes
count_aura_processes() {
    echo "$(pgrep -f "main_v2.py" | wc -l)"
}

# Show current status
echo "Current Status:"
echo "---------------"
AURA_COUNT=$(count_aura_processes)
echo "AURA instances running: $AURA_COUNT"

if check_process "llama-server"; then
    echo "LLM Server: ✅ Running"
    LLAMA_PID=$(pgrep -f "llama-server" | head -1)
    echo "  PID: $LLAMA_PID"
else
    echo "LLM Server: ❌ Not running"
fi

if check_process "main_v2.py"; then
    echo "AURA Main: ✅ Running"
    AURA_PIDS=$(pgrep -f "main_v2.py" | tr '\n' ' ')
    echo "  PIDs: $AURA_PIDS"
else
    echo "AURA Main: ❌ Not running"
fi
echo ""

# Menu
echo "Options:"
echo "--------"
echo "1) Graceful stop (recommended)"
echo "2) Force kill (emergency)"
echo "3) Kill all and restart"
echo "4) Just check status"
echo "5) View logs"
echo ""

read -p "Select option (1-5): " choice

case $choice in
    1)
        echo ""
        echo "Attempting graceful shutdown..."
        
        # Send SIGTERM to main process
        if check_process "main_v2.py"; then
            echo "Sending stop signal to AURA..."
            pkill -TERM -f "main_v2.py"
            sleep 3
            
            # Check if still running
            if check_process "main_v2.py"; then
                echo "⚠️  Graceful shutdown failed, processes still running"
                read -p "Force kill? (y/n): " force
                if [ "$force" = "y" ]; then
                    pkill -9 -f "main_v2.py"
                    echo "✅ Force killed"
                fi
            else
                echo "✅ Graceful shutdown successful"
            fi
        fi
        
        # Stop LLM server
        if check_process "llama-server"; then
            echo "Stopping LLM server..."
            pkill -TERM -f "llama-server"
            sleep 2
            
            if check_process "llama-server"; then
                pkill -9 -f "llama-server"
            fi
            echo "✅ LLM server stopped"
        fi
        ;;
        
    2)
        echo ""
        echo "🚨 EMERGENCY FORCE KILL"
        echo "======================="
        
        read -p "Are you sure? This will terminate ALL AURA processes immediately! (yes/no): " confirm
        
        if [ "$confirm" = "yes" ]; then
            echo "Force killing all AURA processes..."
            
            # Kill Python AURA
            pkill -9 -f "main_v2.py"
            echo "✅ AURA main process killed"
            
            # Kill LLM server
            pkill -9 -f "llama-server"
            echo "✅ LLM server killed"
            
            # Kill any remaining Python processes related to AURA
            pkill -9 -f "python.*aura"
            echo "✅ All related processes killed"
            
            # Clean up any lock files
            rm -f data/*.lock 2>/dev/null
            echo "✅ Lock files cleaned"
            
            echo ""
            echo "🛑 All processes terminated"
        else
            echo "Cancelled"
        fi
        ;;
        
    3)
        echo ""
        echo "Kill all and restart..."
        
        # Kill everything
        pkill -9 -f "main_v2.py" 2>/dev/null
        pkill -9 -f "llama-server" 2>/dev/null
        sleep 2
        
        echo "✅ All processes killed"
        echo ""
        read -p "Start AURA now? (y/n): " start
        
        if [ "$start" = "y" ]; then
            bash scripts/run_aura_v2.sh
        fi
        ;;
        
    4)
        echo ""
        echo "Status Check Complete"
        
        if [ "$AURA_COUNT" -gt 1 ]; then
            echo ""
            echo "⚠️  WARNING: Multiple AURA instances detected!"
            echo "This can cause conflicts and unexpected behavior."
            echo ""
            read -p "Kill duplicates? (y/n): " kill_dup
            if [ "$kill_dup" = "y" ]; then
                # Keep only the first one
                PIDS=$(pgrep -f "main_v2.py" | tail -n +2)
                for pid in $PIDS; do
                    kill -9 $pid 2>/dev/null
                    echo "Killed duplicate PID: $pid"
                done
                echo "✅ Duplicates removed"
            fi
        fi
        ;;
        
    5)
        echo ""
        if [ -f "data/logs/aura.log" ]; then
            echo "Recent logs (last 50 lines):"
            echo "----------------------------"
            tail -50 data/logs/aura.log
        else
            echo "No log file found"
        fi
        ;;
        
    *)
        echo "Invalid option"
        ;;
esac

echo ""
echo "=========================================="

# Final status
echo ""
echo "Final Status:"
AURA_COUNT=$(count_aura_processes)
if [ "$AURA_COUNT" -eq 0 ]; then
    echo "✅ All AURA processes stopped"
else
    echo "⚠️  $AURA_COUNT AURA process(es) still running"
    pgrep -f "main_v2.py" | while read pid; do
        echo "  - PID: $pid"
    done
fi
