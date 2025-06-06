package com.example.myapplication;

import android.app.ActivityOptions;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.util.Pair;
import android.view.View;
import android.view.animation.Animation;
import android.view.animation.AnimationUtils;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

public class MainActivity extends AppCompatActivity {
//Variables
private static int SPLASH_SCREEN=3500;
    Animation topAnim, bottomAnim;
    ImageView image;
    TextView logo, slogan;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);

        //Animations
        topAnim= AnimationUtils.loadAnimation(this, R.anim.top_animation);
        bottomAnim= AnimationUtils.loadAnimation(this, R.anim.bottom_animation);
//Hooks
        image=findViewById(R.id.imageView);
        logo=findViewById(R.id.textView);
        slogan=findViewById(R.id.textView2);

        image.setAnimation(topAnim);
        logo.setAnimation(bottomAnim);
                 slogan.setAnimation(bottomAnim);

new Handler().postDelayed(new Runnable() {
    @Override
    public void run(){
        Intent intent = new Intent(MainActivity.this, Login.class);
    Pair[] pairs= new Pair[2];
    pairs[0]=new Pair<View, String>(image, "logo_image");
        pairs[1]=new Pair<View, String>(logo, "logo_text");
ActivityOptions options= ActivityOptions.makeSceneTransitionAnimation(MainActivity.this, pairs);
startActivity(intent, options.toBundle());


    }
},SPLASH_SCREEN);
    }
}