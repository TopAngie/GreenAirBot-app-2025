package com.example.myapplication;

import android.app.ActivityOptions;
import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.util.Pair;
import android.view.View;
import android.view.WindowManager;
import android.view.animation.Animation;
import android.view.animation.AnimationUtils;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;


import androidx.appcompat.app.AppCompatActivity;


import com.google.android.material.textfield.TextInputEditText;
import com.google.firebase.firestore.DocumentSnapshot;
import com.google.firebase.firestore.FirebaseFirestore;

public class Login extends AppCompatActivity {
    Button callSignUp;
    ImageView image;
    TextView logo, slogan;
    TextInputEditText usernameInput, passwordInput, email;
    FirebaseFirestore firestore;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Safe way to set full-screen mode
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            getWindow().setDecorFitsSystemWindows(false);
        } else {
            getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN, WindowManager.LayoutParams.FLAG_FULLSCREEN);
        }

        setContentView(R.layout.activity_login);

        // Ensure button ID matches XML
        callSignUp = findViewById(R.id.callSignUp);

        image = findViewById(R.id.logo_image);
        logo = findViewById(R.id.logo_name);
        slogan = findViewById(R.id.slogan_name);

        // Get references to the TextInputEditTexts
        // Updated to refer to TextInputEditText
        firestore= FirebaseFirestore.getInstance();
        usernameInput = findViewById(R.id.username);
        passwordInput = findViewById(R.id.password);




        callSignUp.setOnClickListener((view) -> {

            Intent intent = new Intent(Login.this, Dashboard2.class);

            // Create pairs for shared element transition
            Pair<View, String>[] pairs = new Pair[5];
            pairs[0] = new Pair<>(image, "logo_image");
            pairs[1] = new Pair<>(logo, "logo_text");
            pairs[2] = new Pair<>(findViewById(R.id.username), "username");  // Correct reference to the TextInputLayout
            pairs[3] = new Pair<>(findViewById(R.id.password), "password");  // Correct reference to the TextInputLayout
            pairs[4] = new Pair<>(callSignUp, "login");

            // Set up the transition and start the new activity
            ActivityOptions options = ActivityOptions.makeSceneTransitionAnimation(Login.this, pairs);
           // startActivity(intent, options.toBundle());

                String username = usernameInput.getText().toString();
                String password = passwordInput.getText().toString();

                if (validateUsername() && validatePassword()) {
                    firestore.collection("users")
                            .whereEqualTo("username", username)  // Query Firestore for the username
                            .get()
                            .addOnSuccessListener(queryDocumentSnapshots -> {
                                if (!queryDocumentSnapshots.isEmpty()) {
                                    // Get the first matching document
                                    DocumentSnapshot documentSnapshot = queryDocumentSnapshots.getDocuments().get(0);

                                    String storedEmail = documentSnapshot.getId(); // Document ID (email)
                                    String storedPassword = documentSnapshot.getString("password");

                                    if (storedPassword.equals(password)) {
                                        Toast.makeText(this, "Login Successful!", Toast.LENGTH_SHORT).show();
                                        startActivity(intent);
                                        finish();
                                    } else {
                                        Toast.makeText(this, "Incorrect password", Toast.LENGTH_SHORT).show();
                                    }
                                } else {
                                    Toast.makeText(this, "Username not found", Toast.LENGTH_SHORT).show();
                                }
                            })
                            .addOnFailureListener(e -> {
                                Log.e("LoginUser", "Error fetching user: " + e.getMessage());
                                Toast.makeText(this, "Error: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                            });






                }

        });



    }
    private Boolean validateUsername() {
        String val = usernameInput.getText().toString(); // Get the text directly from TextInputEditText
        if (val.isEmpty()) {
            usernameInput.setError("Username cannot be empty");
            return false;
        } else {
            usernameInput.setError(null); // Remove any error
            return true;
        }
    }

    private Boolean validatePassword() {
        String val = passwordInput.getText().toString(); // Get the text directly from TextInputEditText
        if (val.isEmpty()) {
            passwordInput.setError("Password cannot be empty");
            return false;
        } else {
            passwordInput.setError(null); // Remove any error
            return true;
        }
    }


}