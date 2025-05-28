package com.example.myapplication;

import android.os.Bundle;
import android.view.MotionEvent;
import android.view.View;
import android.webkit.CookieManager;
import android.webkit.CookieSyncManager;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import androidx.appcompat.app.AppCompatActivity;

public class Dashboard2 extends AppCompatActivity {

    WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_dashboard2);

        webView = findViewById(R.id.webview);

        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setDomStorageEnabled(true);      // Απαραίτητο για σωστό session
        webSettings.setSaveFormData(true);

        webView.setWebViewClient(new WebViewClient());

        webSettings.setJavaScriptEnabled(true);
        webSettings.setDomStorageEnabled(true);
        webSettings.setDatabaseEnabled(true);
        webSettings.setAllowContentAccess(true);
        webSettings.setAllowFileAccess(true);
        webSettings.setDefaultTextEncodingName("utf-8");

        webView.setWebViewClient(new WebViewClient());

        webView.setFocusable(true);
        webView.setFocusableInTouchMode(true);
        webView.requestFocus(View.FOCUS_DOWN);

        webView.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                if ((event.getAction() == MotionEvent.ACTION_DOWN || event.getAction() == MotionEvent.ACTION_UP) && !v.hasFocus()) {
                    v.requestFocus();
                }
                return false;
            }
        });

        CookieManager cookieManager = CookieManager.getInstance();
        cookieManager.setAcceptCookie(true);
        cookieManager.setAcceptThirdPartyCookies(webView, true); // Για Android Lollipop+

        // Αν έχεις παλιά Android API:
        CookieSyncManager.createInstance(this);
        CookieSyncManager.getInstance().startSync();

        webView.loadUrl("http://10.0.2.2:5000");

        // --- ΠΡΟΣΘΗΚΕΣ ---
        if (android.os.Build.VERSION.SDK_INT < android.os.Build.VERSION_CODES.LOLLIPOP) {
            CookieSyncManager.createInstance(this);
            CookieSyncManager.getInstance().startSync();
        } else {
            cookieManager.flush();
        }

        String cookies = cookieManager.getCookie("http://10.0.2.2:5000");
        System.out.println("Cookies for URL: " + cookies);
    }
}



