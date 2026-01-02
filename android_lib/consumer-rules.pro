# Consumer ProGuard rules for Sentry Android Godot Plugin
# These rules are automatically applied to any app that uses this AAR

# Keep all Sentry SDK classes - the plugin uses SentryLogEvent and other APIs
-keep class io.sentry.** { *; }
-keep interface io.sentry.** { *; }
-keep enum io.sentry.** { *; }

# Specifically keep SentryLogEvent which is used directly by the plugin
-keep class io.sentry.SentryLogEvent { *; }
-keep class io.sentry.SentryLogEventAttributeValue { *; }

# Keep Godot plugin entry point
-keep class io.sentry.godotplugin.SentryAndroidGodotPlugin { *; }

# Keep native methods
-keepclasseswithmembernames class * {
    native <methods>;
}

# Keep any annotated classes
-keep @io.sentry.android.core.KeepPublicGetter class * { public void get*(***); *** get*(); }
