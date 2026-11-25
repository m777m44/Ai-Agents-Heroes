package com.raf3ly.app;

import android.app.Application;

/** Application entry point. Obfuscation only - no signature / integrity protection. */
public class App extends Application {
    @Override
    public void onCreate() {
        super.onCreate();
        I18n.init(this);
    }
}
