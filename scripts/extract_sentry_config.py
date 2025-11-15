#!/usr/bin/env python3
"""
Extract Sentry configuration from project.godot INI file
Usage: python3 extract_sentry_config.py
"""

import os
import re
import configparser
from pathlib import Path

def parse_project_godot():
    """Parse project.godot file with custom parser"""

    # Find project.godot file (script is now in extras/sentry-godot/scripts/)
    project_root = Path(__file__).parent.parent.parent.parent
    project_godot_path = project_root / "project" / "project.godot"

    if not project_godot_path.exists():
        print(f"❌ project.godot not found at: {project_godot_path}")
        return None

    print(f"📖 Reading project.godot from: {project_godot_path}")

    # Read the file content
    with open(project_godot_path, 'r') as f:
        lines = f.readlines()

    sentry_config = {}
    current_section = None
    in_sentry_section = False

    for line_num, line in enumerate(lines, 1):
        line = line.strip()

        # Skip comments and empty lines
        if not line or line.startswith(';'):
            continue

        # Check for section headers
        if line.startswith('[') and line.endswith(']'):
            current_section = line[1:-1]
            if current_section == 'sentry':
                in_sentry_section = True
                print("✅ Found [sentry] section in project.godot")
            else:
                in_sentry_section = False
            continue

        # Parse key=value pairs in Sentry section
        if in_sentry_section and '=' in line:
            # Remove any trailing comments
            key_value = line.split(';')[0].strip()
            if '=' in key_value:
                key, value = key_value.split('=', 1)
                sentry_config[key.strip()] = value.strip()
                print(f"  {key.strip()}: {value.strip()}")

    if not sentry_config:
        print("❌ No Sentry configuration found in project.godot")
        return None

    return sentry_config

def generate_android_metadata(config):
    """Generate AndroidManifest.xml metadata content"""

    dsn = config.get('android/dsn', '')
    # Remove surrounding quotes if present
    dsn = dsn.strip('"')
    debug = config.get('android/debug', 'true').strip('"')
    send_pii = config.get('android/send_default_pii', 'true').strip('"')
    user_interaction = config.get('android/user_interaction_breadcrumbs', 'true').strip('"')
    screenshot = config.get('android/attach_screenshot', 'true').strip('"')
    view_hierarchy = config.get('android/attach_view_hierarchy', 'true').strip('"')
    traces_rate = config.get('android/traces_sample_rate', '1.0')
    profiling_rate = config.get('android/profiling_session_sample_rate', '1.0')
    profiling_lifecycle = config.get('android/profiling_lifecycle', 'trace').strip('"')
    profiling_start = config.get('android/profiling_start_on_app_start', 'true').strip('"')
    replay_error_rate = config.get('android/session_replay_error_sample_rate', '1.0')
    replay_session_rate = config.get('android/session_replay_session_sample_rate', '0.1')

    metadata_lines = [
        '      <!-- Required: set your sentry.io project identifier (DSN) -->',
        f'        <meta-data android:name="io.sentry.dsn" android:value="{dsn}" />',
        '',
        '        <!-- Add data like request headers, user ip address and device name -->',
        f'        <meta-data android:name="io.sentry.send-default-pii" android:value="{send_pii}" />',
        '',
        '        <!-- enable automatic breadcrumbs for user interactions (clicks, swipes, scrolls) -->',
        f'        <meta-data android:name="io.sentry.traces.user-interaction.enable" android:value="{user_interaction}" />',
        '        <!-- enable screenshot for crashes -->',
        f'        <meta-data android:name="io.sentry.attach-screenshot" android:value="{screenshot}" />',
        '        <!-- enable view hierarchy for crashes -->',
        f'        <meta-data android:name="io.sentry.attach-view-hierarchy" android:value="{view_hierarchy}" />',
        '',
        '        <!-- enable the performance API by setting a sample-rate, adjust in production env -->',
        f'        <meta-data android:name="io.sentry.traces.sample-rate" android:value="{traces_rate}" />',
        '',
        '        <!-- Enable UI profiling, adjust in production env. This is evaluated only once per session -->',
        f'        <meta-data android:name="io.sentry.traces.profiling.session-sample-rate" android:value="{profiling_rate}" />',
        '        <!-- Set profiling mode. For more info see https://docs.sentry.io/platforms/android/profiling/#enabling-ui-profiling -->',
        f'        <meta-data android:name="io.sentry.traces.profiling.lifecycle" android:value="{profiling_lifecycle}" />',
        '        <!-- Enable profiling on app start. The app start profile will be stopped automatically when the app start root span finishes -->',
        f'        <meta-data android:name="io.sentry.traces.profiling.start-on-app-start" android:value="{profiling_start}" />',
        '',
        '        <!-- record session replays for 100% of errors and 10% of sessions -->',
        f'        <meta-data android:name="io.sentry.session-replay.on-error-sample-rate" android:value="{replay_error_rate}" />',
        f'        <meta-data android:name="io.sentry.session-replay.session-sample-rate" android:value="{replay_session_rate}" />'
    ]

    return '\n'.join(metadata_lines)

def generate_ios_config(config):
    """Generate iOS Sentry configuration file"""

    dsn = config.get('ios/dsn', '')
    # Remove surrounding quotes if present
    dsn = dsn.strip('"')
    debug = config.get('ios/debug', 'true').strip('"')
    send_pii = config.get('ios/send_default_pii', 'true').strip('"')
    screenshot = config.get('ios/attach_screenshot', 'true').strip('"')
    traces_rate = config.get('ios/traces_sample_rate', '1.0')
    environment = config.get('ios/environment', 'development').strip('"')
    release = config.get('ios/release', '1.0.0').strip('"')

    config_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">',
        '<plist version="1.0">',
        '<dict>',
        '    <!-- Required: set your sentry.io project identifier (DSN) -->',
        f'    <key>io.sentry.dsn</key>',
        f'    <string>{dsn}</string>',
        '',
        '    <!-- Environment and release information -->',
        f'    <key>io.sentry.environment</key>',
        f'    <string>{environment}</string>',
        f'    <key>io.sentry.release</key>',
        f'    <string>{release}</string>',
        '',
        f'    <!-- Debug mode -->',
        f'    <key>io.sentry.debug</key>',
        f'    <{debug.lower()} />',
        '',
        '    <!-- Add data like request headers, user ip address and device name -->',
        f'    <key>io.sentry.send-default-pii</key>',
        f'    <{send_pii.lower()} />',
        '',
        '    <!-- enable screenshot for crashes -->',
        f'    <key>io.sentry.attach-screenshot</key>',
        f'    <{screenshot.lower()} />',
        '',
        '    <!-- enable the performance API by setting a sample-rate, adjust in production env -->',
        f'    <key>io.sentry.traces.sample-rate</key>',
        f'    <real>{traces_rate}</real>',
        '</dict>',
        '</plist>'
    ]

    return '\n'.join(config_lines)

def main():
    """Main function"""
    print("🔧 Extracting Sentry configuration from project.godot...")

    # Parse project.godot
    sentry_config = parse_project_godot()

    if not sentry_config:
        print("❌ Failed to extract Sentry configuration")
        return 1

    # Generate Android metadata content
    android_metadata = generate_android_metadata(sentry_config)

    # Generate iOS configuration content
    ios_config = generate_ios_config(sentry_config)

    # Write Android metadata file
    try:
        # Path to inject directory (script is now in extras/sentry-godot/scripts/)
        project_root = Path(__file__).parent.parent.parent.parent
        android_metadata_path = project_root / "inject" / "sentry_metadata.xml"

        android_metadata_path.parent.mkdir(exist_ok=True)
        with open(android_metadata_path, 'w') as f:
            f.write(android_metadata)

        print(f"✅ Generated Android Sentry metadata: {android_metadata_path}")
        print(f"📝 Android DSN extracted: {sentry_config.get('android/dsn', 'NOT_FOUND')}")

    except Exception as e:
        print(f"❌ Failed to write Android metadata file: {e}")
        return 1

    # Write iOS configuration file
    try:
        # iOS configuration goes to export/ios directory
        ios_config_path = project_root / "export" / "ios" / "sentry_config.plist"

        ios_config_path.parent.mkdir(exist_ok=True)
        with open(ios_config_path, 'w') as f:
            f.write(ios_config)

        print(f"✅ Generated iOS Sentry configuration: {ios_config_path}")
        print(f"📝 iOS DSN extracted: {sentry_config.get('ios/dsn', 'NOT_FOUND')}")

    except Exception as e:
        print(f"❌ Failed to write iOS configuration file: {e}")
        return 1

    print("✅ Sentry configuration extraction completed successfully!")
    print("   🤖 Generated Android metadata for AndroidManifest.xml")
    print("   🍎 Generated iOS plist configuration for iOS export")
    return 0

if __name__ == "__main__":
    exit(main())