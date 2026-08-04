package com.abir.downloader;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.net.Uri;

public class MainActivity extends Activity {
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        webView = new WebView(this);
        setContentView(webView);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);

        webView.setWebViewClient(new WebViewClient());

        // Handle Share Intent from YouTube, Facebook, Instagram, Spotify
        Intent intent = getIntent();
        String action = intent.getAction();
        String type = intent.getType();

        String targetUrl = "file:///android_asset/web_app/index.html";

        if (Intent.ACTION_SEND.equals(action) && type != null && "text/plain".equals(type)) {
            String sharedText = intent.getStringExtra(Intent.EXTRA_TEXT);
            if (sharedText != null) {
                targetUrl += "?url=" + Uri.encode(sharedText);
            }
        }

        webView.loadUrl(targetUrl);
    }
}
