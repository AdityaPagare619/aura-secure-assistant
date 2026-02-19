#!/bin/bash
# Device Diagnosis Script
# Shows detailed information about the Android device

echo "=========================================="
echo "🔍 AURA Device Diagnostic"
echo "=========================================="
echo ""

# Check if running in Termux
if [ -z "$TERMUX_VERSION" ] && [ ! -d "/data/data/com.termux" ]; then
    echo "⚠️  Warning: Not running in Termux environment"
    echo "This script is designed for Termux on Android"
    echo ""
fi

echo "📱 Device Information:"
echo "----------------------"
echo "Manufacturer: $(getprop ro.product.manufacturer 2>/dev/null || echo 'Unknown')"
echo "Model: $(getprop ro.product.model 2>/dev/null || echo 'Unknown')"
echo "Device: $(getprop ro.product.device 2>/dev/null || echo 'Unknown')"
echo ""

echo "⚙️  Android Version:"
echo "-------------------"
echo "Version: $(getprop ro.build.version.release 2>/dev/null || echo 'Unknown')"
echo "API Level: $(getprop ro.build.version.sdk 2>/dev/null || echo 'Unknown')"
echo "Security Patch: $(getprop ro.build.version.security_patch 2>/dev/null || echo 'Unknown')"
echo ""

echo "📺 Display:"
echo "-----------"
wm size 2>/dev/null || echo "Size: Unknown"
wm density 2>/dev/null || echo "Density: Unknown"
echo ""

echo "🔧 Hardware:"
echo "------------"
echo "CPU: $(getprop ro.hardware 2>/dev/null || echo 'Unknown')"
echo "Total RAM: $(free -h 2>/dev/null | grep Mem | awk '{print $2}' || echo 'Unknown')"
echo ""

echo "🔒 Security:"
echo "------------"
if su -c "id" &>/dev/null; then
    echo "Root: ✅ Yes"
else
    echo "Root: ❌ No"
fi
echo "SELinux: $(getenforce 2>/dev/null || echo 'Unknown')"
echo ""

echo "📦 Termux Environment:"
echo "---------------------"
echo "Termux Version: $TERMUX_VERSION"
echo "Prefix: $PREFIX"
echo "Home: $HOME"
echo ""

echo "🔌 Termux API Status:"
echo "--------------------"
check_termux_api() {
    if command -v $1 &> /dev/null; then
        echo "✅ $1"
        return 0
    else
        echo "❌ $1"
        return 1
    fi
}

check_termux_api "termux-telephony-call"
check_termux_api "termux-sms-send"
check_termux_api "termux-notification"
check_termux_api "termux-camera-photo"
check_termux_api "termux-tts-speak"
check_termux_api "termux-dialog"
check_termux_api "termux-battery-status"
echo ""

echo "🎯 System Capabilities:"
echo "----------------------"
# Check input command (for screen control)
if command -v input &> /dev/null; then
    echo "✅ Screen control (input command)"
else
    echo "❌ Screen control not available"
fi

# Check if we can get app list
if pm list packages &>/dev/null; then
    echo "✅ Package manager access"
else
    echo "❌ Package manager restricted"
fi

# Check dumpsys
if dumpsys activity &>/dev/null; then
    echo "✅ System dump access"
else
    echo "❌ System dump restricted"
fi
echo ""

echo "⚠️  Potential Issues:"
echo "--------------------"

# Check for manufacturer-specific issues
MANUFACTURER=$(getprop ro.product.manufacturer 2>/dev/null | tr '[:upper:]' '[:lower:]')

case $MANUFACTURER in
    *xiaomi*|*redmi*)
        echo "⚠️  Xiaomi/Redmi detected:"
        echo "   - MIUI may restrict background apps"
        echo "   - Auto-start may be disabled"
        echo "   - Check: Settings > Apps > Autostart"
        ;;
    *samsung*)
        echo "⚠️  Samsung detected:"
        echo "   - Aggressive battery optimization"
        echo "   - Check: Settings > Battery > App power management"
        ;;
    *huawei*|*honor*)
        echo "⚠️  Huawei/Honor detected:"
        echo "   - Power Genie may kill background apps"
        echo "   - Check: Settings > Battery > App launch"
        ;;
    *oneplus*)
        echo "⚠️  OnePlus detected:"
        echo "   - Battery optimization may be aggressive"
        echo "   - Check: Settings > Battery > Battery optimization"
        ;;
    *oppo*|*vivo*|*realme*)
        echo "⚠️  OPPO/vivo/realme detected:"
        echo "   - ColorOS restrictions may apply"
        echo "   - Check: Settings > Battery settings"
        ;;
esac

# Check Android version
API_LEVEL=$(getprop ro.build.version.sdk 2>/dev/null)
if [ "$API_LEVEL" -lt 23 ] 2>/dev/null; then
    echo "⚠️  Android version < 6.0 (API 23)"
    echo "   - Some features may not work"
    echo "   - Limited background execution"
fi

if [ "$API_LEVEL" -lt 26 ] 2>/dev/null; then
    echo "⚠️  Android version < 8.0 (API 26)"
    echo "   - Limited background activity"
fi

# Check if Termux API is installed
if ! command -v termux-api-start &> /dev/null; then
    echo "❌ Termux:API not installed"
    echo "   Install: pkg install termux-api"
    echo "   And install Termux:API app from F-Droid"
fi

echo ""
echo "=========================================="
echo "📋 Recommendations:"
echo "=========================================="
echo ""

if [ "$API_LEVEL" -lt 23 ] 2>/dev/null; then
    echo "1. ⚠️  Consider upgrading Android for better compatibility"
fi

echo "2. 🔋 Disable battery optimization for Termux:"
echo "   Settings > Apps > Termux > Battery > No restrictions"

echo "3. 🚀 Enable Termux wake lock:"
echo "   Run: termux-wake-lock"

echo "4. 🔄 Allow Termux to start at boot:"
echo "   Settings > Apps > Termux > Autostart"

echo "5. 📱 Keep Termux running in background:"
echo "   Don't swipe away from recents"

echo ""
echo "=========================================="
echo "✅ Diagnosis complete!"
echo "=========================================="
