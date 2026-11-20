#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Builds the Official CapitalTrain Android APK (capital_train_lrt.apk)
Package: com.capitaltrain.app
"""

import os
import sys
import shutil
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = r"I:\CapitalTrain"
SRC_APP_DIR = os.path.join(ROOT_DIR, "android_build_src")
SDK_DIR = r"I:\n8n\android-sdk"
JDK_BIN = r"C:\Program Files\Microsoft\jdk-17.0.20.101-hotspot\bin"
BUILD_TOOLS_DIR = os.path.join(SDK_DIR, "build-tools", "34.0.0")
ANDROID_JAR = os.path.join(SDK_DIR, "platforms", "android-34", "android.jar")

AAPT2 = os.path.join(BUILD_TOOLS_DIR, "aapt2.exe")
D8 = os.path.join(BUILD_TOOLS_DIR, "d8.bat")
ZIPALIGN = os.path.join(BUILD_TOOLS_DIR, "zipalign.exe")
APKSIGNER = os.path.join(BUILD_TOOLS_DIR, "apksigner.bat")
JAVAC = os.path.join(JDK_BIN, "javac.exe")

KEYSTORE_PATH = r"I:\n8n\android_app\release.keystore"
KEYSTORE_PASS = "eduportal2026"
KEYSTORE_ALIAS = "eduportal"

OUTPUT_APK = os.path.join(ROOT_DIR, "downloads", "capital_train_lrt.apk")

def run_cmd(cmd, desc):
    print(f"\n[BUILD] >>> {desc}...")
    env = os.environ.copy()
    env["JAVA_HOME"] = r"C:\Program Files\Microsoft\jdk-17.0.20.101-hotspot"
    res = subprocess.run(cmd, shell=True, env=env, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if res.returncode != 0:
        print(f"[ERROR] {desc} failed (rc={res.returncode})")
        print("STDOUT:", res.stdout)
        print("STDERR:", res.stderr)
        sys.exit(1)
    if res.stdout.strip():
        print(res.stdout.strip())
    print(f"[SUCCESS] {desc} complete.")

def main():
    print("=== Starting CapitalTrain Android APK Builder ===")

    # 1. Prepare directory structure
    if os.path.exists(SRC_APP_DIR):
        shutil.rmtree(SRC_APP_DIR)
    
    res_dir = os.path.join(SRC_APP_DIR, "res")
    mipmap_dir = os.path.join(res_dir, "mipmap-xxxhdpi")
    values_dir = os.path.join(res_dir, "values")
    java_dir = os.path.join(SRC_APP_DIR, "java", "com", "capitaltrain", "app")
    build_dir = os.path.join(SRC_APP_DIR, "build")
    classes_dir = os.path.join(build_dir, "classes")
    dex_dir = os.path.join(build_dir, "dex")
    gen_dir = os.path.join(build_dir, "gen")

    for d in [mipmap_dir, values_dir, java_dir, classes_dir, dex_dir, gen_dir]:
        os.makedirs(d, exist_ok=True)

    # 2. Copy launcher icon
    icon_source = os.path.join(ROOT_DIR, "icons", "icon-192.png")
    if os.path.exists(icon_source):
        shutil.copy(icon_source, os.path.join(mipmap_dir, "ic_launcher.png"))
        shutil.copy(icon_source, os.path.join(mipmap_dir, "ic_launcher_round.png"))

    # 3. Write strings.xml
    with open(os.path.join(values_dir, "strings.xml"), "w", encoding="utf-8") as f:
        f.write('''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">قطار العاصمة LRT</string>
</resources>''')

    # 4. Write AndroidManifest.xml
    manifest_path = os.path.join(SRC_APP_DIR, "AndroidManifest.xml")
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write('''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.capitaltrain.app"
    android:versionCode="2"
    android:versionName="2.0">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <application
        android:label="@string/app_name"
        android:icon="@mipmap/ic_launcher"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:usesCleartextTraffic="true"
        android:hardwareAccelerated="true"
        android:theme="@android:style/Theme.NoTitleBar">

        <activity
            android:name=".MainActivity"
            android:configChanges="orientation|screenSize|keyboardHidden"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>''')

    # 5. Write MainActivity.java
    java_file = os.path.join(java_dir, "MainActivity.java")
    with open(java_file, "w", encoding="utf-8") as f:
        f.write('''package com.capitaltrain.app;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.view.Window;
import android.view.WindowManager;
import android.graphics.Color;
import android.webkit.WebChromeClient;

public class MainActivity extends Activity {
    private WebView webView;
    private static final String PRIMARY_URL = "https://capitaltrain.tafawuq-edu.site/";
    private static final String FALLBACK_URL = "http://192.168.1.3:6060/";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        Window window = getWindow();
        window.addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS);
        window.setStatusBarColor(Color.parseColor("#0f172a"));

        webView = new WebView(this);
        setContentView(webView);

        WebSettings ws = webView.getSettings();
        ws.setJavaScriptEnabled(true);
        ws.setDomStorageEnabled(true);
        ws.setDatabaseEnabled(true);
        ws.setUseWideViewPort(true);
        ws.setLoadWithOverviewMode(true);
        ws.setAllowFileAccess(true);
        ws.setAllowContentAccess(true);
        ws.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        ws.setCacheMode(WebSettings.LOAD_DEFAULT);

        webView.setBackgroundColor(Color.parseColor("#0f172a"));

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                view.loadUrl(url);
                return true;
            }

            @Override
            public void onReceivedError(WebView view, int errorCode, String description, String failingUrl) {
                if (failingUrl != null && failingUrl.startsWith("https://capitaltrain")) {
                    view.loadUrl(FALLBACK_URL);
                }
            }
        });

        webView.setWebChromeClient(new WebChromeClient());
        webView.loadUrl(PRIMARY_URL);
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
''')

    # 6. AAPT2 compile
    compiled_res = os.path.join(build_dir, "compiled_res.zip")
    run_cmd(f'"{AAPT2}" compile --dir "{res_dir}" -o "{compiled_res}"', "AAPT2 Compile Resources")

    # 7. AAPT2 link
    unaligned_apk = os.path.join(build_dir, "app-unaligned.apk")
    run_cmd(
        f'"{AAPT2}" link -I "{ANDROID_JAR}" "{compiled_res}" '
        f'--manifest "{manifest_path}" '
        f'--java "{gen_dir}" '
        f'-o "{unaligned_apk}" '
        f'--auto-add-overlay',
        "AAPT2 Link"
    )

    # 8. JAVAC compile
    r_java = os.path.join(gen_dir, "com", "capitaltrain", "app", "R.java")
    run_cmd(
        f'"{JAVAC}" -encoding UTF-8 -cp "{ANDROID_JAR}" '
        f'-d "{classes_dir}" '
        f'"{r_java}" "{java_file}"',
        "Compile Java Classes"
    )

    # 9. D8 Dexing
    class_files = []
    for root, _, files in os.walk(classes_dir):
        for fl in files:
            if fl.endswith(".class"):
                class_files.append(os.path.join(root, fl))

    classes_str = " ".join([f'"{cf}"' for cf in class_files])
    run_cmd(f'cmd /c ""{D8}" --lib "{ANDROID_JAR}" --output "{dex_dir}" {classes_str}"', "D8 Dexing")

    # 10. Add classes.dex into unaligned apk
    import zipfile
    classes_dex = os.path.join(dex_dir, "classes.dex")
    with zipfile.ZipFile(unaligned_apk, 'a') as z:
        z.write(classes_dex, "classes.dex")
    print("[SUCCESS] Added classes.dex into APK.")

    # 11. Zipalign
    aligned_apk = os.path.join(build_dir, "app-aligned.apk")
    if os.path.exists(aligned_apk):
        os.remove(aligned_apk)
    run_cmd(f'"{ZIPALIGN}" -v -p 4 "{unaligned_apk}" "{aligned_apk}"', "Zipalign APK")

    # 12. Apksigner
    signed_apk = os.path.join(build_dir, "app-release-signed.apk")
    if os.path.exists(signed_apk):
        os.remove(signed_apk)

    run_cmd(
        f'cmd /c ""{APKSIGNER}" sign --ks "{KEYSTORE_PATH}" '
        f'--ks-pass pass:{KEYSTORE_PASS} '
        f'--ks-key-alias {KEYSTORE_ALIAS} '
        f'--key-pass pass:{KEYSTORE_PASS} '
        f'--out "{signed_apk}" '
        f'"{aligned_apk}""',
        "Sign APK with Keystore"
    )

    # Verify APK signature
    run_cmd(
        f'cmd /c ""{APKSIGNER}" verify --verbose "{signed_apk}""',
        "Verify APK signature"
    )

    # 13. Copy to destination
    os.makedirs(os.path.dirname(OUTPUT_APK), exist_ok=True)
    shutil.copy(signed_apk, OUTPUT_APK)
    print(f"\n🎉 [SUCCESS] Official Android APK built and signed successfully at:\n>>> {OUTPUT_APK}")
    print(f"File size: {os.path.getsize(OUTPUT_APK) / 1024:.1f} KB")

if __name__ == "__main__":
    main()
